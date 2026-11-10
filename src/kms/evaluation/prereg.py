"""Pre-registered decision rules as code, so a verdict cannot be argued after the fact.

A protocol fixes minimum sample, deadline, pass rule and early-stop rule before any data exists. The verdict
function is pure: same bets and time in, same verdict out.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Sequence

from .stats import Bet, resampled_roi


class Verdict(str, Enum):
    RUNNING = "running"
    PASS = "pass"
    FAIL = "fail"
    EARLY_FAIL = "fail (early stop)"


@dataclass(frozen=True)
class Preregistration:
    name: str
    deadline: datetime
    target_bets: int
    target_clusters: int
    min_bets_at_deadline: int
    pass_min_roi: float          # e.g. 0.01 for +1%
    pass_min_lower: float        # lower bound of the 90% interval, e.g. -0.03
    early_stop_after: int
    early_stop_max_roi: float    # e.g. -0.10
    level: float = 0.90

    def verdict(self, bets: Sequence[Bet], now: datetime, seed: int = 0) -> Verdict:
        if not bets:
            return Verdict.FAIL if now >= self.deadline else Verdict.RUNNING
        point, lo, hi = resampled_roi(bets, level=self.level, seed=seed)
        clusters = len({b.cluster for b in bets})
        if len(bets) >= self.early_stop_after and point < self.early_stop_max_roi and hi < 0:
            return Verdict.EARLY_FAIL
        complete = (len(bets) >= self.target_bets and clusters >= self.target_clusters) or now >= self.deadline
        if not complete:
            return Verdict.RUNNING
        if len(bets) < self.min_bets_at_deadline:
            return Verdict.FAIL  # too few observations is a fail, never an extension
        return Verdict.PASS if point > self.pass_min_roi and lo > self.pass_min_lower else Verdict.FAIL
