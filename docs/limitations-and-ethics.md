# Limitations, threats to validity and responsible use

## Threats to validity
- **Short sample, single regime.** Most live data covers a few weeks of one market regime; results may not generalize.
- **Simulation is not execution.** The simulated exchange uses the real book, but cannot observe true queue position,
  hidden replenishment or the market impact of our own orders.
- **Correlated observations.** Contracts sharing a close time or event move together; naive per-bet statistics overstate
  confidence. All intervals resample whole slots or events.
- **Forking paths.** Many variants were explored. Only pre-registered forward tests are treated as evidence; exploratory
  results are labeled as such.
- **Infrastructure dependence.** Results depend on latency; a faster participant could plausibly earn what this setup cannot,
  and the reverse.
- **LLM forecasting leakage.** Blind LLM forecasts used snapshot features only, with no web access, but overlapping time
  windows in a batch can leak later prices into earlier rows. A clean rerun isolates each row's history.

## Responsible use
- Only public market data and the researcher's own account were used, through the exchange's official API, within its rate limits.
- No strategy attempts to manipulate prices, spoof orders or exploit other participants' errors.
- Real-money exposure was capped at a few tens of dollars, with hard daily loss limits.
- Exchange data is not redistributed.

## Use of tools
Development used AI-assisted coding tools. Research questions, pre-registration decisions, go/stop rules and
interpretation of results were set and reviewed by the author.
