from datetime import datetime, timedelta, timezone

import pytest

from kms.evaluation import Bet, Preregistration, Verdict, brier, brier_difference_interval, resampled_roi, roi

NOW = datetime(2026, 11, 10, tzinfo=timezone.utc)


def test_roi_and_brier():
    bets = [Bet("a", 10, 12), Bet("b", 10, 0)]
    assert roi(bets) == pytest.approx(-0.4)
    assert brier([1.0, 0.0], [1, 0]) == 0
    assert brier([0.5], [1]) == 0.25


def test_cluster_resampling_widens_interval():
    # 50 clusters x 10 identical bets: per-cluster outcome is all-or-nothing
    bets = [Bet(c, 1.0, 2.0 if c % 2 else 0.0) for c in range(50) for _ in range(10)]
    point, lo, hi = resampled_roi(bets, seed=1)
    assert point == pytest.approx(0.0)
    assert lo < -0.15 and hi > 0.15  # correlated bets: wide, honest interval


def test_brier_difference_sign():
    ids = [str(i) for i in range(40)]
    y = {i: int(int(i) % 2) for i in ids}
    good = {i: 0.9 if y[i] else 0.1 for i in ids}
    base = {i: 0.5 for i in ids}
    d, lo, hi = brier_difference_interval(good, base, y, {i: i for i in ids}, seed=2)
    assert d < 0 and hi < 0


def prereg(**kw):
    base = dict(name="t", deadline=NOW + timedelta(days=13), target_bets=300, target_clusters=60,
                min_bets_at_deadline=150, pass_min_roi=0.01, pass_min_lower=-0.03,
                early_stop_after=100, early_stop_max_roi=-0.10)
    base.update(kw)
    return Preregistration(**base)


def test_verdict_running_then_pass():
    winners = [Bet(c, 1.0, 1.1) for c in range(300)]
    assert prereg().verdict(winners[:50], NOW) == Verdict.RUNNING
    assert prereg().verdict(winners, NOW) == Verdict.PASS


def test_too_few_at_deadline_is_fail():
    winners = [Bet(c, 1.0, 1.1) for c in range(40)]
    assert prereg().verdict(winners, NOW + timedelta(days=14)) == Verdict.FAIL


def test_early_stop():
    losers = [Bet(c, 1.0, 0.0) for c in range(100)]
    assert prereg().verdict(losers, NOW) == Verdict.EARLY_FAIL
