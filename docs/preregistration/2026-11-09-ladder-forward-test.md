# Pre-registration: hourly/daily ladder forward test

**Filed:** 2026-11-09 08:40 UTC, before any data from the test period existed. Not edited since filing.

## Hypothesis
A volatility-based probability model identifies positive-expectancy taker bets on Kalshi's hourly and daily crypto
"above-strike" ladder contracts.

## Strategy (fixed)
- Every 30 seconds: spot = multi-exchange composite; volatility = blend of short-horizon (1-minute EWMA) and 24-hour
  (5-minute candle) estimates; probability of settling above the strike under a random walk with the settlement-average adjustment.
- Bet when model probability − ask − taker fee ≥ 5¢, ask between 10¢ and 90¢, spread ≤ 4¢, ≥ 3 minutes to close,
  at most 2 bets per close per coin, at most 10 open. Held to settlement.
- Executed on the simulated exchange (real live order book, hypothetical money).

## Outcome measure
Return on stake after fees, as traded. 90% interval from resampling whole time slots.

## Stopping and decision rules
- **Ends:** 2026-11-23 08:40 UTC, or at 100 settled bets across ≥ 30 slots, whichever comes first. Fewer than 100 bets
  at the deadline → judged on what exists; too few → **fail**.
- **Pass:** return > 0 and the interval's lower bound > −5%.
- **Fail:** anything else.
- **Early stop:** after 50 settled bets, return < −20% and the interval's upper bound < 0 → fail.

## Consequence
Pass → propose a small, capped real-money pilot. Fail → recommend ending the 15-minute/ladder line of work.

## Known handicap (declared in advance)
No signal-age guard was deployed; stale-signal fills during feed lag count, because that is how the system trades.
