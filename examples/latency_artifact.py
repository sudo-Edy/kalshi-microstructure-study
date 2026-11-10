"""Synthetic demonstration: how a lagging order-book feed manufactures a fake edge.

SYNTHETIC DATA ONLY. No real market data is used. The point is the mechanism, not the magnitudes.

Setup
- A spot price follows a random walk. Each 15-minute window has a binary contract: does the price finish at or above
  the window's opening price?
- The market is perfectly efficient: its ask is always the true probability plus a 1c half-spread.
- Our "forecaster" is also perfect: it knows the true probability from the live spot price. It has NO edge.
- The only difference between runs is how old the order book we *record* is.

A paper trader that compares a fresh model against a stale recorded book sees mispricings that are just the
market having moved, and books profits at prices that no longer exist. Executing the same signals against the
book as it really stood removes the "edge" entirely.

usage: python examples/latency_artifact.py [--windows 3000] [--out docs/figures/latency_artifact.png]
"""
from __future__ import annotations

import argparse
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from kms.evaluation import Bet, resampled_roi  # noqa: E402
from kms.simulator.fills import taker_fee  # noqa: E402
from kms.strategies.base import edge_after_fee  # noqa: E402
from kms.strategies.settlement_average import normal_cdf  # noqa: E402

WINDOW_S = 900
SIGMA = 0.0006      # per-second relative volatility (synthetic)
HALF_SPREAD = 0.01
MIN_EDGE = 0.03
STAKE = 10.0
CHECK_EVERY = 5     # seconds between strategy evaluations


def fair_prob(spot: float, strike: float, seconds_left: float) -> float:
    if seconds_left <= 0:
        return 1.0 if spot >= strike else 0.0
    return normal_cdf(math.log(spot / strike) / (SIGMA * math.sqrt(seconds_left)))


def ask_from_prob(p: float) -> float:
    return min(0.99, max(0.01, round(p + HALF_SPREAD, 2)))


def run(windows: int, lag_s: int, seed: int):
    rng = random.Random(seed)
    paper, real = [], []
    for w in range(windows):
        path = [100.0]
        for _ in range(WINDOW_S):
            path.append(path[-1] * math.exp(SIGMA * rng.gauss(0, 1)))
        strike, final = path[0], path[-1]
        yes_wins = final >= strike
        for t in range(max(lag_s, 30), WINDOW_S - 30, CHECK_EVERY):
            p_now = fair_prob(path[t], strike, WINDOW_S - t)              # perfect, live forecaster
            stale_ask = {"YES": ask_from_prob(fair_prob(path[t - lag_s], strike, WINDOW_S - t + lag_s))}
            stale_ask["NO"] = ask_from_prob(1 - fair_prob(path[t - lag_s], strike, WINDOW_S - t + lag_s))
            true_ask = {"YES": ask_from_prob(p_now), "NO": ask_from_prob(1 - p_now)}
            for side, prob in (("YES", p_now), ("NO", 1 - p_now)):
                a = stale_ask[side]
                if not 0.05 <= a <= 0.95 or edge_after_fee(prob, a) < MIN_EDGE:
                    continue
                won = yes_wins == (side == "YES")
                for book, out in ((a, paper), (true_ask[side], real)):
                    n = int(STAKE // book)
                    cost = n * book + taker_fee(book, n)
                    out.append(Bet(w, cost, n * won))
                break
            else:
                continue
            break  # one bet per window
    return paper, real


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--windows", type=int, default=3000)
    ap.add_argument("--out", default=os.path.join("docs", "figures", "latency_artifact.png"))
    args = ap.parse_args()
    lags = [0, 2, 5, 9, 15, 24]
    rows = []
    print(f"{'lag':>4} {'bets':>5}  {'paper ROI (stale book)':>26}  {'executed ROI (true book)':>26}")
    for lag in lags:
        paper, real = run(args.windows, lag, seed=lag + 1)
        if not paper:
            print(f"{lag:>3}s {0:>5}  {'no signals':>26}")
            rows.append((lag, None, None))
            continue
        p, plo, phi = resampled_roi(paper, n_boot=500)
        r, rlo, rhi = resampled_roi(real, n_boot=500)
        rows.append((lag, (p, plo, phi), (r, rlo, rhi)))
        print(f"{lag:>3}s {len(paper):>5}  {p:+8.1%} ({plo:+.1%}, {phi:+.1%})   {r:+8.1%} ({rlo:+.1%}, {rhi:+.1%})")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed; skipping figure")
        return
    xs = [r[0] for r in rows if r[1]]
    fig, ax = plt.subplots(figsize=(7, 4.2), dpi=150)
    for idx, label, color in ((1, "Paper result (stale recorded book)", "#c0392b"),
                              (2, "Same signals, executed on the true book", "#2c3e50")):
        ys = [r[idx][0] * 100 for r in rows if r[1]]
        lo = [r[idx][1] * 100 for r in rows if r[1]]
        hi = [r[idx][2] * 100 for r in rows if r[1]]
        ax.plot(xs, ys, marker="o", color=color, label=label)
        ax.fill_between(xs, lo, hi, color=color, alpha=0.15)
    ax.axhline(0, color="#7f8c8d", lw=0.8)
    ax.set_xlabel("Order-book feed lag (seconds)")
    ax.set_ylabel("Return on stake after fees (%)")
    ax.set_title("A perfect forecaster with no edge looks profitable on a lagging feed\n"
                 "(synthetic data, 90% cluster-resampled bands)", fontsize=10)
    ax.legend(frameon=False, fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    fig.savefig(args.out)
    print("figure:", args.out)


if __name__ == "__main__":
    main()
