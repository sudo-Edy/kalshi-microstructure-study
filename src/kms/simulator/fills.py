"""Conservative taker-fill simulation against a real order-book snapshot.

Paper trading usually assumes every order fills at the quoted price. Here a hypothetical immediate-or-cancel order
fills only the size actually displayed at or better than its limit, at those prices, using a book snapshot taken
after a realistic round-trip delay, and pays the fee rounded up to the cent.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .book import OrderBook, Side

TAKER_FEE_RATE = 0.07  # fee per contract = rate x p x (1 - p), the published schedule shape


def taker_fee(avg_price: float, contracts: int, rate: float = TAKER_FEE_RATE) -> float:
    """Order-level taker fee, rounded up to the next cent."""
    if contracts <= 0:
        return 0.0
    raw = rate * contracts * avg_price * (1 - avg_price)
    return math.ceil(raw * 100 - 1e-9) / 100


@dataclass(frozen=True)
class Fill:
    side: Side
    wanted: int
    filled: int
    notional: float  # dollars paid for contracts, before fee
    fee: float

    @property
    def avg_price(self) -> float:
        return self.notional / self.filled if self.filled else math.nan

    @property
    def cost(self) -> float:
        return self.notional + self.fee

    def pnl(self, outcome_yes: bool) -> float:
        """Settlement P&L: each held contract pays $1 if its side wins."""
        won = outcome_yes == (self.side == "YES")
        return self.filled * (1.0 if won else 0.0) - self.cost


def simulate_taker_fill(book: OrderBook, side: Side, limit: float, contracts: int) -> Fill:
    """Walk the ask ladder cheapest-first, never above `limit`, never beyond displayed size."""
    got, notional = 0, 0.0
    for level in book.asks(side):
        if level.price > limit + 1e-9 or got >= contracts:
            break
        take = min(int(level.size), contracts - got)
        got += take
        notional += take * level.price
    return Fill(side, contracts, got, round(notional, 6), taker_fee(notional / got, got) if got else 0.0)
