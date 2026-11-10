# Lab notebook (abridged)

Dated record of decisions, results and corrections. Corrections are kept, not erased.

| Date (2026) | Entry |
|---|---|
| late Oct | First trading prototypes on 15-minute BTC contracts; small real-money trials. |
| Nov 4 | Taker replay (~25k bets) negative across strategies; taker trading disabled. Market maker moved to ETH/XRP/SOL/DOGE. Shadow "practice" makers introduced so rule changes are learned on the real book without risking money. |
| Nov 4 | Bug found: order cancellations silently failed (missing parameter, error treated as success). Stale bids rested until close. Fixed; fees added to P&L accounting. |
| Nov 5 | Historical cycles 1–9: maker profitability by price band flips between periods (frozen test **failed**); order-flow conditioning **passed** on untouched data. Tick recorder added. |
| Nov 6 | Paper results suggested a +15% edge for one strategy family. |
| Nov 7 | **Correction.** Six independent audits show the feed ran ~9s behind with ~50% of trades missing; the +15% was a latency artifact. Fixes deployed; clean-data period begins. Simulated exchange on the real live book introduced. |
| Nov 8 | Order path latency cut from ~2.5s to ~0.14s. Hourly/daily ladder contracts added (simulation only). Hunter strategy frozen test **failed** at 1,020 bets. |
| Nov 9 | Go/stop rule adopted: no further spending without evidence. Ladder forward test pre-registered. 15-minute practice strategies switched off. |
| Nov 10 | LLM forecaster ties the market (Brier) on 141 settled contracts. Memory leak found (per-market history never freed) and fixed. Final-minute settlement-average test pre-registered. System slimmed to the two active experiments; CPU throttling eliminated. |
| Nov 23 | *Verdicts due for both pre-registered tests.* |
