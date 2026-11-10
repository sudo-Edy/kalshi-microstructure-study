"""Reference implementation of the pre-registered final-minute model
(docs/preregistration/2026-11-10-final-minute-settlement.md).

Contracts settle on the mean of the 60 one-second index values before close. With n values already fixed (sum S)
and r = 60 - n still to come, the remaining values are modeled as a random walk from the latest value x:

    final mean ~ Normal( (S + r*x) / 60 ,  k * sigma * sqrt(r(r+1)(2r+1)/6) / 60 )

because the sum of a random walk's next r positions has variance sigma^2 * sum_{i=1..r} i^2. k is a declared
fat-tail allowance. Before the averaging window opens, the walk also runs for the remaining time first.
"""
from __future__ import annotations

import math
from typing import Optional

from .base import MarketSnapshot, Strategy

WINDOW_S = 60


def normal_cdf(z: float) -> float:
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def prob_average_at_or_above(strike: float, latest: float, fixed_mean: float, n_fixed: int,
                             sigma_per_s: float, tail: float = 1.5, seconds_before_window: float = 0.0) -> float:
    n = max(0, min(WINDOW_S, int(n_fixed)))
    r = WINDOW_S - n
    mean = ((fixed_mean * n if n else 0.0) + r * latest) / WINDOW_S
    if r == 0 or sigma_per_s <= 0:
        return 1.0 if mean >= strike else 0.0
    var_sum = sigma_per_s ** 2 * (r * (r + 1) * (2 * r + 1) / 6 + r ** 2 * max(0.0, seconds_before_window))
    sd = tail * math.sqrt(var_sum) / WINDOW_S
    return normal_cdf((mean - strike) / sd)


class SettlementAverageModel(Strategy):
    """Prices a contract from the running settlement average. Needs the exchange's running-average stream."""

    name = "settlement_average"

    def __init__(self, sigma_per_s: float, tail: float = 1.5, **kw):
        super().__init__(**kw)
        self.sigma_per_s = sigma_per_s
        self.tail = tail
        self.fixed_mean: Optional[float] = None
        self.n_fixed: int = 0

    def update_average(self, fixed_mean: Optional[float], n_fixed: int) -> None:
        self.fixed_mean, self.n_fixed = fixed_mean, n_fixed

    def probability_yes(self, snap: MarketSnapshot) -> Optional[float]:
        if snap.seconds_to_close <= 0:
            return None
        in_window = snap.seconds_to_close <= WINDOW_S and self.n_fixed > 0 and self.fixed_mean is not None
        return prob_average_at_or_above(
            snap.strike, snap.spot, self.fixed_mean if in_window else 0.0, self.n_fixed if in_window else 0,
            self.sigma_per_s, self.tail, 0.0 if in_window else snap.seconds_to_close - WINDOW_S)
