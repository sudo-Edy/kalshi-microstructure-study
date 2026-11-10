"""Binary-contract order book.

Event-contract exchanges typically publish only *bids* for each side: YES bids and NO bids. Because a YES and a
NO contract together pay exactly $1, buying YES at price p is the same as matching a NO bid at 1 - p. So the YES
asks are derived from the NO bids, and vice versa.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Literal, Optional, Tuple

Side = Literal["YES", "NO"]


@dataclass(frozen=True)
class Level:
    price: float  # dollars, 0 < price < 1
    size: float   # contracts


def _levels(raw: Iterable[Tuple[float, float]]) -> List[Level]:
    out = []
    for price, size in raw:
        p = float(price)
        p = p / 100 if p > 1 else p  # accept cents or dollars
        if 0 < p < 1 and size > 0:
            out.append(Level(round(p, 4), float(size)))
    return out


@dataclass
class OrderBook:
    yes_bids: List[Level] = field(default_factory=list)
    no_bids: List[Level] = field(default_factory=list)

    @classmethod
    def from_bids(cls, yes: Iterable[Tuple[float, float]], no: Iterable[Tuple[float, float]]) -> "OrderBook":
        return cls(_levels(yes), _levels(no))

    def asks(self, side: Side) -> List[Level]:
        """Ask levels for buying `side`, cheapest first."""
        other = self.no_bids if side == "YES" else self.yes_bids
        return sorted((Level(round(1 - l.price, 4), l.size) for l in other), key=lambda l: l.price)

    def best_bid(self, side: Side) -> Optional[Level]:
        bids = self.yes_bids if side == "YES" else self.no_bids
        return max(bids, key=lambda l: l.price) if bids else None

    def best_ask(self, side: Side) -> Optional[Level]:
        a = self.asks(side)
        return a[0] if a else None

    def mid(self) -> Optional[float]:
        """Market-implied probability of YES, the baseline forecaster in the study."""
        bid, ask = self.best_bid("YES"), self.best_ask("YES")
        if bid is None or ask is None:
            return None
        return (bid.price + ask.price) / 2
