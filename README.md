# Retail-Scale Algorithmic Trading on Event-Contract Markets

**An empirical study of edge, latency and evaluation integrity on Kalshi's short-horizon crypto contracts**

> Status: **ongoing** (started October 2026). Two pre-registered forward tests are running; verdicts due 2026-11-23.
> This repository documents the research design, pre-registrations and findings, with tested reference
> implementations of the core components. The full trading system is private.

![tests](https://github.com/sudo-Edy/kalshi-microstructure-study/actions/workflows/tests.yml/badge.svg)

---

## Abstract

Regulated event-contract exchanges such as Kalshi list binary contracts on whether a cryptocurrency's price will be
above a threshold at a fixed time (15-minute, hourly and daily horizons). These markets settle on a published
reference index and are open to retail participants through an API, which makes them a convenient laboratory for a
practical question: **can a single developer, with commodity cloud hardware and no co-location, extract a durable
edge from these markets after fees?**

This study builds a complete trading-research stack: a live order-book feed with latency monitoring, a simulated
exchange that fills hypothetical orders against the *real* live order book, a library of forecasting and quoting
strategies, and an evaluation framework built around frozen, pre-registered forward tests. Interim results are
predominantly negative: taker strategies lose to fees, passive quoting is adversely selected, and every forecaster
tested (a volatility model, a large language model and a calibrated-probability service) is at best equal to the
market-implied probability. The most important methodological finding is that **an apparent +15% edge was produced
entirely by data-feed latency** caused by CPU throttling on the host machine, an artifact that standard health checks
did not detect.

## Research questions

1. **Forecasting.** Do model-based probabilities beat the market-implied probability (Brier score) on short-horizon crypto contracts? → [docs/research-questions.md](docs/research-questions.md)
2. **Execution.** Can passive (maker) or aggressive (taker) strategies earn positive returns after fees at retail latency?
3. **Structure.** Do settlement mechanics (a 60-second averaged reference index) create predictable, exploitable information in the final minute?
4. **Integrity.** How do infrastructure faults (feed lag, dropped messages, stale prices) distort backtests and paper results, and how can they be detected?

## Approach in one paragraph

Every idea passes through the same pipeline: historical replay → paper trading → simulated execution against the
live book (fake money, real liquidity) → a **pre-registered forward test** with a fixed sample size, fixed metric and
fixed pass/fail rule written before any test data exists → only then a capped real-money pilot. Details in
[docs/methodology.md](docs/methodology.md).

## Interim findings (summary)

| Question | Result so far |
|---|---|
| Taker betting on 15-minute contracts | Negative across ~25k replayed bets; mispricings (≈1–1.5¢) are smaller than fee + spread |
| Passive market making (15-minute) | Fills are adversely selected ("picked off"); no quoting variant reached significance in live shadow testing |
| Forecasters vs. market (Brier) | Market-implied probability ≈ best; an LLM forecaster tied the market on 141 settled contracts; a pure volatility model was worse |
| The "+15% edge" | **Artifact.** Feed ran ~9s behind the exchange; corrected value ≈ 0% |
| Hourly/daily ladder contracts | Pre-registered test running |
| Final-minute settlement-average effect | Pre-registered test running |

Full write-up: [docs/findings-interim.md](docs/findings-interim.md) · Timeline: [docs/lab-notebook.md](docs/lab-notebook.md)

## Repository layout

```
docs/
  research-questions.md     hypotheses and what would falsify them
  methodology.md            data, simulation, evaluation, statistics
  findings-interim.md       results to date, including negative results
  lab-notebook.md           dated log of key events and corrections
  limitations-and-ethics.md scope, threats to validity, responsible-use notes
  preregistration/          frozen forward-test protocols (unedited after filing)
src/kms/
  feed/        lag monitor (exchange-timestamp latency) and fail-closed freshness gate
  simulator/   binary order book and conservative taker-fill simulation with fee rounding
  strategies/  strategy interface and the pre-registered settlement-average model
  evaluation/  cluster-resampled ROI and Brier statistics; pre-registered verdicts as code
tests/                      pytest suite (runs in CI)
analysis/                   planned analyses and figures
data/                       data policy (no market data is redistributed)
```

## Quick start

```bash
pip install -e ".[dev]"
pytest -q
```

```python
from kms.simulator import OrderBook, simulate_taker_fill
from kms.strategies import MarketSnapshot, SettlementAverageModel

book = OrderBook.from_bids(yes=[(0.78, 50)], no=[(0.20, 50)])     # YES ask = 0.80
model = SettlementAverageModel(sigma_per_s=0.005)
model.update_average(fixed_mean=100.4, n_fixed=30)                 # 30 of 60 settlement seconds fixed
signal = model.signal(MarketSnapshot("DEMO", strike=100.0, seconds_to_close=30, spot=100.5, book=book))
fill = simulate_taker_fill(book, signal.side, limit=signal.ask + 0.01, contracts=10)
print(signal, fill.cost)
```

## What is intentionally not here

- **The full trading system.** Private. `src/kms` holds clean, tested reference implementations of the generic
  components; [src/README.md](src/README.md) describes the full architecture.
- **Market data.** Exchange data is not redistributed. See [data/README.md](data/README.md).
- **Credentials or account details.** None are stored in this repository.

## Disclaimer

Research and education only. Nothing here is financial advice or a recommendation to trade. Event contracts can lose
their entire value. Past simulated or real results do not predict future results.

## Citation

See [CITATION.cff](CITATION.cff).
