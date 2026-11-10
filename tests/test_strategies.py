import pytest

from kms.simulator import OrderBook
from kms.strategies import MarketSnapshot, SettlementAverageModel, edge_after_fee
from kms.strategies.settlement_average import normal_cdf
from kms.strategies.settlement_average import prob_average_at_or_above as p_above


def test_model_limits():
    assert p_above(100, 100, 101, 59, 0.05) > 0.999
    assert p_above(100, 100, 99, 59, 0.05) < 0.001
    assert p_above(100, 100, 0, 0, 0.05) == pytest.approx(0.5)
    assert p_above(100, 99, 101, 60, 0.05) == 1.0  # window complete: outcome known


def test_variance_formula_exact_case():
    # n = 59, r = 1: mean = (59*100 + 100.075)/60, sd = 1.5 * 0.05 / 60 -> z = 1
    assert p_above(100, 100.075, 100, 59, 0.05) == pytest.approx(normal_cdf(1.0), abs=1e-9)


def test_more_time_or_volatility_means_less_certainty():
    assert p_above(100, 100.2, 99.9, 30, 0.05) > p_above(100, 100.2, 99.9, 30, 0.10)
    assert p_above(100, 100.05, 0, 0, 0.05, seconds_before_window=120) < p_above(100, 100.05, 0, 0, 0.05)


def test_edge_after_fee():
    assert edge_after_fee(0.90, 0.80) == pytest.approx(0.90 - 0.80 - 0.07 * 0.8 * 0.2)


def _snap(book, spot=100.5, secs=30):
    return MarketSnapshot("T", strike=100.0, seconds_to_close=secs, spot=spot, book=book)


def test_signal_buys_underpriced_side():
    book = OrderBook.from_bids(yes=[(0.78, 50)], no=[(0.20, 50)])  # YES ask 0.80
    m = SettlementAverageModel(sigma_per_s=0.005, min_edge=0.03)
    m.update_average(100.4, 30)
    s = m.signal(_snap(book))
    assert s is not None and s.side == "YES" and s.edge >= 0.03


def test_no_signal_outside_price_band_or_without_edge():
    m = SettlementAverageModel(sigma_per_s=0.005, min_edge=0.03)
    m.update_average(100.4, 30)
    expensive = OrderBook.from_bids(yes=[(0.98, 50)], no=[(0.01, 50)])  # YES ask 0.99 > band
    assert m.signal(_snap(expensive)) is None
    fair = OrderBook.from_bids(yes=[(0.49, 50)], no=[(0.49, 50)])
    m.update_average(100.0, 30)
    assert m.signal(_snap(fair, spot=100.0)) is None
