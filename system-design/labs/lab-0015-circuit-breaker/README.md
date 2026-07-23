# Lab 0015 — Circuit Breaker & Reliability Lab

Companion to [Lesson 0015](../../lessons/0015-reliability-patterns.html). Everything the lesson claimed — retry amplification, the storm that outlives its outage, fail-fast vs eating the timeout, queues as latency bombs — you now verify with your own runs. Rule of the lab: **predict before you run.** Write your prediction down; the gap between prediction and output is where the learning is.

```bash
python3 reliability_lab.py
```

Three experiments: (1) **retry amplification** — a dependency fails 50% of attempts for 10 s; naive nested retries (2 layers × 3 attempts) vs a retry budget capped at 10%, with a per-second view of the storm and how long the dependency needs to dig out after the failure ends, (2) **circuit breaker** — a full closed/open/half-open state machine run through a 10 s outage; without the breaker every call eats the 1000 ms timeout, with it calls fail fast in microseconds after the trip and a half-open probe recloses on recovery, (3) **load shedding** — offered load ramps to 2× capacity; an unshed queue grows without bound (watch Little's law price each arrival) vs admission control at 0.9C, which rejects some requests so survivors keep flat latency.

Everything is simulated: time is a discrete clock and the "dependency" fails on a schedule, so runs are reproducible (seeded RNG) and finish in a few seconds.

## Exercises

All edits happen in the `CONFIG` block at the top of `reliability_lab.py`.

### E1 — Predict the amplification
Part A shows 2 layers × 3 attempts = worst case 9. Predict the mean and worst case with `LAYERS = 3` before touching anything — then change it, run, compare. Why does the *mean* at 50% failure stay so much lower than the worst case, and why does that stop mattering during a full outage? Restore `LAYERS = 2`.

### E2 — Make the breaker flap
Set `DEP_FAIL_PROB = 0.5` (a brownout, not a blackout) and `BREAKER_WINDOW = 5`. Predict: will the breaker stay open through the window, or bounce between closed and open? Run and count the state transitions. Then raise `BREAKER_WINDOW` to 50 and explain what a bigger sample buys and what it costs (hint: how many calls pay the timeout before the trip?). Restore both.

### E3 — Jitter the storm
In experiment 1, retries currently all land exactly one second later — synchronized. Set `RETRY_JITTER = True` (spreads each retry uniformly over the next 3 s). Predict the naive policy's peak multiplier and recovery time before running. Jitter lowers the *peak* — does it shorten the *storm*? Explain the trade you observe, then restore.

### E4 — Protect the checkout class
Set `PRIORITY_SHEDDING = True`. Predict the per-class rejection split: the shedder still drops the same total, so who pays? Run and compare checkout vs browse p99 and rejected counts against the uniform-shedding run. Then lower `ADMIT_FRAC` to `0.6` and check whether checkout is still untouched — at what offered load would it stop being safe?

### E5 — Stretch: adaptive concurrency
The admission cap `0.9 × CAPACITY` is a magic number: correct today, wrong after the next deploy. Replace the fixed cap with an AIMD controller: each second, if measured wait < 50 ms, raise the cap by +5; on any queue growth, multiply it by 0.8. Ramp the load and watch the cap discover capacity by itself. This is the idea behind [Netflix's adaptive concurrency limits](https://netflixtechblog.medium.com/performance-under-load-3e6fa9a60581) — the production form of the fix.

## Deliverable

A short note (5 lines) answering E1–E4: prediction vs observed, one sentence each. Bring it to the next session — wrong predictions are the most useful thing you can bring, and they become learning records.
