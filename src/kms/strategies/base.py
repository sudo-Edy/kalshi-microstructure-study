"""Strategy interface. Strategies turn a snapshot into a probability; a shared rule turns probability into a signal.

Keeping the decision rule outside individual strategies means every forecaster is judged by the same edge
threshold, price band and fee model, which is what a pre-registered comparison needs.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..simulator.book import OrderBook, Side
from ..simulator.fills import TAKER_FEE_RATE


@dataclass(frozen=True)
class MarketSnapshot:
    ticker: str
    strike: float
    seconds_to_close: float
    spot: float
    book: OrderBook


@dataclass(frozen=True)
class Signal:
    ticker: str
    side: Side
    probability: float  # model probability that `side` wins
    ask: float
    edge: float         # probability - ask - fee per contract


def edge_after_fee(probability: float, ask: float, fee_rate: float = TAKER_FEE_RATE) -> float:
    return probability - ask - fee_rate * ask * (1 - ask)


class Strategy(ABC):
    name: str = "strategy"

    def __init__(self, min_edge: float = 0.03, price_band: tuple[float, float] = (0.03, 0.97)):
        self.min_edge = min_edge
        self.price_band = price_band

    @abstractmethod
    def probability_yes(self, snap: MarketSnapshot) -> float | None:
        """P(contract settles YES), or None when the model has no opinion."""

    def signal(self, snap: MarketSnapshot) -> Signal | None:
        p = self.probability_yes(snap)
        if p is None:
            return None
        for side, prob in (("YES", p), ("NO", 1 - p)):
            best = snap.book.best_ask(side)
            if best is None or not (self.price_band[0] <= best.price <= self.price_band[1]):
                continue
            e = edge_after_fee(prob, best.price)
            if e >= self.min_edge:
                return Signal(snap.ticker, side, prob, best.price, round(e, 6))
        return None
