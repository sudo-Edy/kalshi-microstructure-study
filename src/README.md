# Architecture (implementation withheld)

The source code is not published. This outline describes the components so the methodology can be understood and,
in principle, reimplemented.

```
             exchange websocket ──► feed/  ──► latency monitor (p50/p90 lag, reconnects, stalls)
                                       │
  spot exchanges ─► composite price ───┤
                                       ▼
                              strategies/  ── signals ──► freshness gate (≤ 2s) ──► order path
                                                                                    │
                                     ┌──────────────────────────────────────────────┤
                                     ▼                    ▼                          ▼
                             simulator/ (real book,   shadow ledger          real account
                              fake money)             (book at 0/1/3s)       (disabled unless a
                                     │                                         pre-registered pass)
                                     ▼
                              evaluation/  ── pre-registered scoring, resampled intervals, health alarms
```

| Folder | Responsibility |
|---|---|
| `feed/` | Websocket client, order-book reconstruction, exchange-timestamp lag measurement, watchdog reconnects |
| `simulator/` | Hypothetical account against the live book: taker fills limited to displayed depth after a round-trip delay; resting orders queue behind displayed size and fill only on real trades; settlement on official results |
| `strategies/` | Probability models (volatility, settlement-average), quoting rules, ladder scanner |
| `evaluation/` | Scoring scripts for each pre-registration, Brier comparisons, slot-resampled confidence intervals, health checks |
