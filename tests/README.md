# Testing philosophy

The private implementation has offline regression tests that must pass before any change reaches the running system:
order-path latency, freshness gating, simulated fill and queue accounting, settlement-average model math, memory
boundedness across market rollovers, and a reconnect test against the live feed. Each test reproduces a failure that
actually occurred (e.g. silent cancel failures, stale-price orders, unbounded per-market history) before it is fixed.
