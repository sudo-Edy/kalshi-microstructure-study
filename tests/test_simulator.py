import math

import pytest

from kms.simulator import OrderBook, simulate_taker_fill, taker_fee


@pytest.fixture
def book():
    # YES bids 0.78 / 0.77, NO bids 0.20 / 0.19  ->  YES asks 0.80 / 0.81, NO asks 0.22 / 0.23
    return OrderBook.from_bids(yes=[(0.78, 50), (0.77, 100)], no=[(0.20, 4), (0.19, 100)])


def test_asks_derived_from_opposite_bids(book):
    assert [(l.price, l.size) for l in book.asks("YES")] == [(0.80, 4), (0.81, 100)]
    assert book.best_ask("NO").price == 0.22
    assert book.mid() == pytest.approx(0.79)


def test_cents_input_accepted():
    b = OrderBook.from_bids(yes=[(78, 5)], no=[(20, 5)])
    assert b.best_bid("YES").price == 0.78


def test_fill_respects_limit_and_displayed_size(book):
    f = simulate_taker_fill(book, "YES", limit=0.81, contracts=12)
    assert f.filled == 12
    assert f.notional == pytest.approx(4 * 0.80 + 8 * 0.81)
    f2 = simulate_taker_fill(book, "YES", limit=0.80, contracts=12)
    assert f2.filled == 4  # never pays above the limit


def test_zero_fill_costs_nothing():
    f = simulate_taker_fill(OrderBook(), "YES", 0.5, 10)
    assert f.filled == 0 and f.cost == 0 and math.isnan(f.avg_price)


def test_fee_rounds_up_to_cent():
    assert taker_fee(0.50, 10) == 0.18   # 0.175 -> 0.18
    assert taker_fee(0.95, 10) == 0.04   # 0.03325 -> 0.04
    assert taker_fee(0.5, 0) == 0.0


def test_settlement_pnl(book):
    f = simulate_taker_fill(book, "YES", 0.81, 10)
    assert f.pnl(outcome_yes=True) == pytest.approx(10 - f.cost)
    assert f.pnl(outcome_yes=False) == pytest.approx(-f.cost)
