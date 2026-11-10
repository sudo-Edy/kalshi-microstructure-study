"""Binary-contract order book.

Event-contract exchanges typically publish only *bids* for each side: YES bids and NO bids. Because a YES and a
NO contract together pay exactly $1, buying YES at price p is the same as matching a NO bid at 1 - p. So the YES
asks are derived from the NO bids, and vice versa.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Literal

Side = Literal["YES", "NO"]


@dataclass(frozen=True)
class Level:
    price: float  # dollars, 0 < price < 1
    size: float   # contracts


def _levels(raw: Iterable[tuple[float, float]]) -> list[Level]:
    out = []
    for price, size in raw:
        p = float(price)
        p = p / 100 if p > 1 else p  # accept cents or dollars
        if 0 < p < 1 and size > 0:
            out.append(Level(round(p, 4), float(size)))
    return out


@dataclass
class OrderBook:
    yes_bids: list[Level] = field(default_factory=list)
    no_bids: list[Level] = field(default_factory=list)

    @classmethod
    def from_bids(cls, yes: Iterable[tuple[float, float]], no: Iterable[tuple[float, float]]) -> OrderBook:
        return cls(_levels(yes), _levels(no))

    def asks(self, side: Side) -> list[Level]:
        """Ask levels for buying `side`, cheapest first."""
        other = self.no_bids if side == "YES" else self.yes_bids
        return sorted((Level(round(1 - lvl.price, 4), lvl.size) for lvl in other), key=lambda lvl: lvl.price)

    def best_bid(self, side: Side) -> Level | None:
        bids = self.yes_bids if side == "YES" else self.no_bids
        return max(bids, key=lambda lvl: lvl.price) if bids else None

    def best_ask(self, side: Side) -> Level | None:
        a = self.asks(side)
        return a[0] if a else None

    def mid(self) -> float | None:
        """Market-implied probability of YES, the baseline forecaster in the study."""
        bid, ask = self.best_bid("YES"), self.best_ask("YES")
        if bid is None or ask is None:
            return None
        return (bid.price + ask.price) / 2
