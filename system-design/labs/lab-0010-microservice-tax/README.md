# Lab 0010 — The Microservice Tax

Companion to [Lesson 0010](../../lessons/0010-monolith-to-microservices.html). Everything the lesson claimed — hops add tails, availability multiplies down, fan-out amplifies p99 — you now verify with your own runs. Rule of the lab: **predict before you run.** Write your prediction down; the gap between prediction and output is where the learning is.

```bash
python3 microservice_tax_lab.py
```

Three experiments: (1) the same 20 ms of work as a monolith vs split across N=2/5/10/20 services in a serial chain, each hop a lognormal draw (mean 1 ms, fat tail) — mean/p50/p99 end-to-end vs N, (2) availability of a serial chain: each service 99.9% available per call, 100k simulated requests per N, measured success rate vs the theoretical 0.999^N, (3) parallel fan-out — the request waits for the *slowest* of N calls, so the 1-in-100 straggler becomes the common case (theory 1 − 0.99^N), plus hedged requests at p95 showing the mitigation and its ~5% load price.

Everything is simulated: a "hop" is a lognormal latency draw (network calls have tails, not averages), a "service" is a coin that lands heads 99.9% of the time. Seeded RNG, so runs are reproducible and finish in ~2 seconds.

## Exercises

All edits happen in the `CONFIG` block at the top of `microservice_tax_lab.py`.

### E1 — Price the chain at N=20
Before looking at experiment 1's last row: predict end-to-end p99 for N=20 (base work 20 ms, hop mean 1 ms — but the *mean* is not the number that bites). Write your guess, run, compare. Then set `HOP_SIGMA = 0.5` (thinner tails) and predict the new p99 gap before rerunning. Lesson: the tax is paid in tails, not means.

### E2 — Buy a nine, spend it on services
With `SERVICE_AVAILABILITY = 0.999`, N=20 lands near 98%. Predict: if you raise it to `0.9999` (four nines per service), what is the largest N that still keeps end-to-end availability ≥ 99.9%? Compute 0.9999^N by hand first, then add your N to `SERVICE_COUNTS` and confirm. This is the "you must be this tall" arithmetic in reverse.

### E3 — One retry, two bills
Set `RETRIES = 1` and predict both columns before running: what happens to measured availability at N=20, and what happens to calls/req? You get most of a nine back — but every retry is extra load on a service that may already be struggling. Say out loud when this trade turns dangerous (hint: retries during a partial outage are a load multiplier aimed at the sick service).

### E4 — Hedge the tail
Experiment 3 hedges at `HEDGE_AT_PCTL = 95`. Predict: if you hedge earlier, at `90`, does fan-out p99 improve or worsen, and what happens to extra load? Then try `None` (hedging off) and watch N=100's p99 revert. Compare the two bills: hedged p99 vs percent extra calls — the Dean & Barroso trade in two columns.

### E5 — Stretch: a toy service registry
Write a small `Registry` class: `register(name, addr, ttl_s)`, `heartbeat(name)`, `resolve(name)`; entries whose TTL lapses without a heartbeat stop resolving. Then simulate one service crashing (heartbeats stop) and measure how many requests hit the dead address before the TTL expires. You have just rebuilt the core of Consul/etcd health-checked discovery — and discovered why TTL length is a trade between failover speed and heartbeat load.

## Deliverable

A short note (5 lines) answering E1–E4: prediction vs observed, one sentence each. Bring it to the next session — wrong predictions are the most useful thing you can bring, and they become learning records.
