"""Evaluation statistics with cluster resampling.

Bets that share a time slot or event are strongly correlated (one price move decides them together), so
per-bet confidence intervals are far too narrow. All intervals here resample whole clusters.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, Hashable, List, Mapping, Sequence, Tuple


@dataclass(frozen=True)
class Bet:
    cluster: Hashable  # time slot or event
    cost: float        # dollars paid including fees
    payout: float      # dollars received at settlement


def roi(bets: Sequence[Bet]) -> float:
    cost = sum(b.cost for b in bets)
    if cost <= 0:
        raise ValueError("no stake")
    return (sum(b.payout for b in bets) - cost) / cost


def _clusters(items, key) -> Dict[Hashable, list]:
    out: Dict[Hashable, list] = {}
    for it in items:
        out.setdefault(key(it), []).append(it)
    return out


def resampled_roi(bets: Sequence[Bet], n_boot: int = 2000, level: float = 0.90,
                  seed: int = 0) -> Tuple[float, float, float]:
    """(point ROI, lower, upper) with whole clusters resampled with replacement."""
    groups = list(_clusters(bets, lambda b: b.cluster).values())
    rng = random.Random(seed)
    stats = []
    for _ in range(n_boot):
        sample = [b for g in rng.choices(groups, k=len(groups)) for b in g]
        stats.append(roi(sample))
    stats.sort()
    lo_i = int((1 - level) / 2 * n_boot)
    hi_i = int((1 + level) / 2 * n_boot) - 1
    return roi(bets), stats[lo_i], stats[hi_i]


def brier(probs: Sequence[float], outcomes: Sequence[int]) -> float:
    if len(probs) != len(outcomes) or not probs:
        raise ValueError("need equal, non-empty sequences")
    return sum((p - y) ** 2 for p, y in zip(probs, outcomes)) / len(probs)


def brier_difference_interval(model: Mapping[str, float], baseline: Mapping[str, float], outcomes: Mapping[str, int],
                              cluster_of: Mapping[str, Hashable], n_boot: int = 1000, level: float = 0.90,
                              seed: int = 0) -> Tuple[float, float, float]:
    """Brier(model) - Brier(baseline) with a cluster-resampled interval. Negative = model better than baseline."""
    ids = [i for i in outcomes if i in model and i in baseline]
    groups = list(_clusters(ids, lambda i: cluster_of[i]).values())

    def diff(sample: List[str]) -> float:
        y = [outcomes[i] for i in sample]
        return brier([model[i] for i in sample], y) - brier([baseline[i] for i in sample], y)

    rng = random.Random(seed)
    stats = sorted(diff([i for g in rng.choices(groups, k=len(groups)) for i in g]) for _ in range(n_boot))
    return diff(ids), stats[int((1 - level) / 2 * n_boot)], stats[int((1 + level) / 2 * n_boot) - 1]
