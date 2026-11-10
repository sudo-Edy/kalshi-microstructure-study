from kms.feed import FreshnessGate, LagMonitor


class Clock:
    def __init__(self, t=1000.0):
        self.t = t

    def __call__(self):
        return self.t


def test_lag_percentiles_from_exchange_timestamps():
    clk = Clock()
    m = LagMonitor(clock=clk)
    for lag in [0.2, 0.4, 0.5, 0.6, 9.0]:
        m.observe(exchange_ts=clk.t - lag, received_ts=clk.t)
    assert m.p50 == 0.5
    assert m.p90 == 9.0


def test_lag_unknown_when_stale_or_empty():
    clk = Clock()
    m = LagMonitor(max_age_s=60, clock=clk)
    assert m.p50 is None
    m.observe(clk.t - 0.3, clk.t)
    clk.t += 61
    assert m.p50 is None  # an old reading is not evidence of a healthy feed


def test_reset_on_reconnect():
    clk = Clock()
    m = LagMonitor(clock=clk)
    m.observe(clk.t - 20, clk.t)
    m.reset()
    assert m.p50 is None


def test_gate_fails_closed():
    g = FreshnessGate(max_lag_s=2, max_book_age_s=2)
    assert g.check(0.5, 0.3).allowed
    assert not g.check(None, 0.3).allowed
    assert not g.check(float("nan"), 0.3).allowed
    assert not g.check(0.5, 2.5).allowed
    assert not g.check(0.5, 0.3, signal_age_s=40).allowed
    assert "feed lag" in g.check(9.0, 0.1).reason
