# Interim findings

*Last updated: 2026-11-10. Results are reported as measured, including negative and inconclusive ones.*

## 1. Taker strategies lose to costs
A replay of roughly 25,000 taker bets across strategy families lost money in every family. Systematic mispricings in
short-horizon contracts were on the order of 1–1.5¢, smaller than the combined cost of fee plus spread. Taker
trading was disabled for real money.

## 2. Passive quoting is adversely selected
Resting bids on 15-minute contracts were filled disproportionately when the price moved through them. Early real
fills showed average 60-second markouts of about −7.7¢ against a 3¢ quoted edge. Up to 22 rule variants ran in live
shadow mode on the real order book; after about 250 contract-windows on clean data, none beat the baseline at a
meaningful significance level. Publicly available wallet-level analyses suggest that profitable participants in these
markets are dominated by faster participants and liquidity rebates, consistent with this result.

## 3. Forecasters vs. the market
Brier scores on 141 settled hourly/daily ladder snapshots (59 events), resampled by event:

| Forecaster | Brier | Δ vs. market (90% interval) |
|---|---|---|
| Market mid | 0.1594 | — |
| Large language model, blind | 0.1595 | +0.0000 (−0.006, +0.005) |
| 80% market + 20% LLM | 0.1591 | −0.0003 (−0.002, +0.001) |
| Volatility model alone | 0.1730 | +0.0136 (+0.001, +0.027) |

The market-implied probability was the best single forecaster. The volatility model was reliably worse, and its
edge-based bets lost about 23% of stake. An earlier test of a calibrated-probability service on 901 historical
15-minute snapshots found a small Brier improvement only when blended with the market price. *Pilot scale; a hint,
not proof.*

## 4. Case study: a latency artifact that looked like an edge
Paper results showed a strategy family earning about **+15%** on stake. An audit found that the recorded order book
lagged the exchange by a median of about 9 seconds (90th percentile ≈ 24s) and that roughly half of all trades were
never recorded, while every health check reported normal operation. Causes:

1. CPU throttling on the burstable cloud instance (more than 50% steal time).
2. A model-training job holding the interpreter lock.
3. Two dozen quoting engines re-pricing on every book update, overwhelming the message consumer until keep-alive
   messages were missed and the connection silently cycled.

Re-priced on the book as it actually stood, the "edge" was approximately **0%**. Remediation included continuous lag
measurement against exchange timestamps, a freshness gate on all orders, rate-limited re-pricing and a vectorized
training step. **Lesson:** a positive backtest on stale data is indistinguishable from a real edge unless data
timeliness is measured directly.

## 5. Pre-registered tests in progress
| Test | Filed | Deadline | Status |
|---|---|---|---|
| Hourly/daily ladder, volatility-model taker bets | 2026-11-09 | 2026-11-23 | Running; too few settled bets for a verdict |
| Final-minute settlement-average effect | 2026-11-10 | 2026-11-23 | Running |

Earlier frozen tests: a 15-minute "hunter" strategy family **failed** its pre-registered criterion (−2.88% after fees
over 1,020 bets; required a positive return with interval above zero). An order-flow conditioning hypothesis passed
on untouched historical data but showed no sign of reaching a back-of-queue participant in simulation.

## 6. Real-money pilot
A small real-money pilot (tens of dollars) produced a net loss after fees. Real-money trading is disabled pending a
pre-registered pass.
