# Research questions and hypotheses

Each hypothesis states what would count as support and what would falsify it. Hypotheses marked *pre-registered*
have a frozen protocol in [preregistration/](preregistration/).

## RQ1: Forecasting
**H1.** A model combining spot price, realized volatility and order-flow features produces better-calibrated
probabilities than the market-implied probability (mid-price) on 15-minute, hourly and daily crypto contracts.

- *Metric:* Brier score difference vs. market mid, resampled by event (contracts within one event are correlated).
- *Support:* model Brier lower than market with the 90% resampled interval excluding zero.
- *Falsified by:* interval including or exceeding zero across repeated out-of-sample slices.

**H1b.** Large language models and calibrated-probability services add information beyond the market price.
- *Design:* blind forecasts from snapshot features only (no web access), scored against settled outcomes; blends
  with the market tested at fixed weights.

## RQ2: Execution at retail latency
**H2a (taker).** Buying contracts when the model's probability exceeds the ask plus fees by a margin yields positive
return on stake.

**H2b (maker).** Resting bids below fair value earn the spread net of adverse selection.
- *Key measurement:* markouts, the contract's price 10/30/60 seconds after a fill, to quantify adverse selection.

## RQ3: Settlement structure
**H3 (pre-registered).** Because 15-minute contracts settle on the average of 60 one-second index values before
close, part of the outcome is fixed during the final minute. If the order book reprices this information slower than
a model that tracks the running average, buying the under-priced side earns a positive return after fees.

**H4 (pre-registered).** A volatility-based probability model finds positive-expectancy taker bets on hourly/daily
"above-strike" ladder contracts, where competition is assumed to be thinner.

## RQ4: Evaluation integrity
**H5.** Infrastructure faults (feed latency, dropped messages, throttled compute) can manufacture apparent edges in
paper and simulated results that disappear on correctly timed data.
- *Status:* supported by a documented incident (see [findings-interim.md](findings-interim.md) §4).
