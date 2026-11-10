# Pre-registration: final-minute settlement-average effect

**Filed:** 2026-11-10 ~02:00 UTC, before any data from the test period existed. Not edited since filing.

## Hypothesis
15-minute crypto contracts settle on the simple average of the 60 one-second reference-index values before close.
During the final minute, part of that average is already fixed and is streamed by the exchange. If the order book
reprices this information more slowly than a model that tracks the running average, buying the under-priced side
earns a positive return after fees. This is a structural, not predictive, hypothesis.

## Model (fixed)
- n = seconds already in the average, S = their sum, r = 60 − n, x = latest index value.
- Final average ~ Normal(mean = (S + r·x)/60, sd = 1.5 · σₛ · √(r(r+1)(2r+1)/6) / 60), with σₛ the per-second
  standard deviation of index changes over the last 120 ticks; 1.5 is a declared fat-tail allowance.
- p(YES) = P(final average ≥ strike).

## Bet rule (fixed)
- Only while 5 ≤ n ≤ 57, with order book, index tick and feed all ≤ 2 seconds old.
- Buy YES if p − ask − fee ≥ 3¢ (ask in [3¢, 97¢]); NO symmetrically. One bet per contract; $10 at limit = ask + 1¢.
- Fill simulated against the real order book re-read 0.15s later (realistic round trip), displayed size only;
  fee rounded up to the cent; no fill → no bet.

## Outcome measure
Return on stake after fees. 90% interval from resampling 15-minute slots.

## Stopping and decision rules
- **Ends:** 2026-11-23 08:40 UTC, or at 300 settled bets across ≥ 60 slots. Fewer than 150 bets at the deadline → **fail**.
- **Pass:** return > +1% and interval lower bound > −3%.
- **Early stop:** after 100 bets, return < −10% and interval upper bound < 0 → fail.

## Exploration (not part of the verdict)
Per-second observations from 3 minutes before close are logged for hypothesis generation; any idea found there
requires its own pre-registration on later data.
