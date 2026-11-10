"""Feed-latency measurement and the freshness gate.

The study's central integrity lesson: a market-data feed can report "connected" while running many seconds behind
the exchange, and stale prices manufacture fake edges. Latency is therefore measured continuously from the
exchange's own timestamps, and no order is allowed while the measured lag is too high or unknown.
"""
from __future__ import annotations

import math
import time
from collections import deque
from dataclasses import dataclass
from typing import Callable, Deque, Optional


class LagMonitor:
    """Rolling percentiles of (receive time - exchange time) for recent messages.

    Exchange timestamps often have one-second resolution, so ~0.5s is a practical floor for the median.
    Readings expire: if no sample arrives for `max_age_s`, the lag is unknown (None), never assumed fine.
    """

    def __init__(self, window: int = 400, max_age_s: float = 60.0, clock: Callable[[], float] = time.time):
        self._samples: Deque[float] = deque(maxlen=window)
        self._last_sample_t: float = -math.inf
        self.max_age_s = max_age_s
        self._clock = clock

    def observe(self, exchange_ts: float, received_ts: Optional[float] = None) -> None:
        recv = self._clock() if received_ts is None else received_ts
        if not (math.isfinite(exchange_ts) and math.isfinite(recv)):
            return
        self._samples.append(recv - exchange_ts)
        self._last_sample_t = recv

    def reset(self) -> None:
        """Call on reconnect: samples from a previous session say nothing about the new one."""
        self._samples.clear()
        self._last_sample_t = -math.inf

    def percentile(self, q: float) -> Optional[float]:
        if not self._samples or self._clock() - self._last_sample_t > self.max_age_s:
            return None
        xs = sorted(self._samples)
        return xs[min(len(xs) - 1, int(q * len(xs)))]

    @property
    def p50(self) -> Optional[float]:
        return self.percentile(0.5)

    @property
    def p90(self) -> Optional[float]:
        return self.percentile(0.9)


@dataclass(frozen=True)
class GateDecision:
    allowed: bool
    reason: str


class FreshnessGate:
    """Blocks orders unless every input is demonstrably fresh. Missing or invalid readings fail closed."""

    def __init__(self, max_lag_s: float = 2.0, max_book_age_s: float = 2.0, max_signal_age_s: float = 2.0):
        self.max_lag_s = max_lag_s
        self.max_book_age_s = max_book_age_s
        self.max_signal_age_s = max_signal_age_s

    def check(self, feed_lag_s: Optional[float], book_age_s: Optional[float],
              signal_age_s: Optional[float] = 0.0) -> GateDecision:
        for name, value, limit in (("feed lag", feed_lag_s, self.max_lag_s),
                                   ("book age", book_age_s, self.max_book_age_s),
                                   ("signal age", signal_age_s, self.max_signal_age_s)):
            if value is None or not math.isfinite(value) or value < 0:
                return GateDecision(False, f"{name} unknown")
            if value > limit:
                return GateDecision(False, f"{name} {value:.2f}s > {limit:.2f}s")
        return GateDecision(True, "fresh")
