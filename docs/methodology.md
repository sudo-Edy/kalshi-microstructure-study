# Methodology

## 1. Setting
- **Venue:** Kalshi, a US-regulated event-contract exchange (binary contracts paying $1 if true).
- **Contracts:** crypto "above strike" contracts on BTC, ETH, SOL, XRP and DOGE at 15-minute, hourly and daily horizons.
- **Settlement:** a simple average of the 60 one-second values of the CF Benchmarks real-time index before close.
- **Fees:** taker fee ≈ 0.07 × p × (1 − p) per contract, measured from real fills; maker fee observed at zero during the study.
- **Infrastructure:** one small cloud virtual machine (1 GB RAM, burstable CPU) with no co-location. This is the retail constraint under study.

## 2. Data
- Live order-book and trade stream via the exchange websocket; exchange timestamps used to measure **feed lag**
  (receive time − exchange time) continuously.
- Spot reference: median of several exchange feeds, approximating the settlement index; the official index stream
  used where available.
- Historical one-minute data for replay; tick-level recordings for later replay.
- Settlement outcomes fetched from the public API after close.

## 3. Evaluation ladder
Every strategy moves through stages, and may only advance on evidence:

| Stage | What it measures | Known bias |
|---|---|---|
| Historical replay | Rough plausibility | One-minute bars hide queue position and timing; can be optimistic or pessimistic |
| Paper trading | Signal quality at quoted prices | Assumes every order fills at the quote; ignores slippage and latency |
| **Simulated exchange** | Execution economics | Fake money, **real live order book**: taker orders wait a realistic round trip and fill only displayed size; resting orders join the back of the real queue and fill only on real trades |
| Shadow ledger | Fill-price realism | Records the real book at 0s, 1s and 3s after each signal without trading |
| **Pre-registered forward test** | Out-of-sample verdict | Frozen rules, sample size, metric and deadline |
| Real-money pilot | Ground truth | Small capped size; only after a pre-registered pass |

## 4. Pre-registration
A protocol is written and dated *before* any data from its test period exists. It fixes: the exact strategy rules,
the scoring command, the minimum sample, the deadline, the pass/fail rule and an early-stop rule. Protocols are not
edited after filing; any change requires a new protocol on new data. A test with too few observations at its deadline
is scored as a **fail** (no extensions).

## 5. Statistics
- **Calibration:** Brier score against the market mid as the baseline forecaster.
- **Returns:** return on stake after fees, as traded.
- **Uncertainty:** 90% intervals by resampling whole time slots or events, not individual bets, because bets in the
  same window or event are strongly correlated.
- **Multiple comparisons:** variants found after looking at data are treated as hypotheses for a new forward test,
  never as results.

## 6. Data-integrity controls
- Continuous feed-lag percentiles (p50/p90) with alarms; reconnect and stall counters.
- **Freshness gate:** no simulated or real order while measured lag exceeds 2 seconds.
- Test results are accepted only for periods when the setup was demonstrably healthy.
- Offline regression tests must pass before any change reaches the running system.
