# Lab 0007 — Cache Lab

Companion to [Lesson 0007](../../lessons/0007-caching-deep.html). Everything the lesson claimed — Zipf skew, diminishing returns, update-pattern trade-offs, the stampede — you now verify with your own runs. Rule of the lab: **predict before you run.** Write your prediction down; the gap between prediction and output is where the learning is.

```bash
python3 cache_lab.py
```

Three experiments: (1) LRU cache-aside hit-rate curve over a zipf(1.1) workload — 200k requests, 50k keys, cache sizes 100 → 10,000, (2) cache-aside vs write-through under a 90/10 read/write mix, (3) a real thundering herd — 50 threads racing for one expired hot key, unprotected vs per-key lock vs TTL jitter.

Everything is simulated: the "database" is a counter that charges a fixed cost per access (5 ms/read, 8 ms/write), so DB load is exact and there is no network. Experiment 3 uses real threads with a short real DB sleep — that sleep *is* the race window that makes a stampede possible.

## Exercises

All edits happen in the `CONFIG` block at the top of `cache_lab.py`.

### E1 — Flatten the curve
Predict: if `ZIPF_S` drops from `1.1` to `0.7` (much less skew), what happens to the hit rate of the size-100 cache — small drop or collapse? Write your guess, change it, run, compare. Then restore. Lesson: caching pays *because* traffic is skewed, not because caches are magic.

### E2 — Buy the next 10 points
Using experiment 1's table, estimate the cache size needed to reach a 92% hit rate. Add your guess to `CACHE_SIZES`, run, and check. How many *times* more memory did the last 5–6 points cost compared with the first 47?

### E3 — Make write-through lose
Write-through wins experiment 2 at `WRITE_FRACTION = 0.10`. Predict the crossover: at what write fraction does cache-aside's *total simulated DB load* come out ahead, if ever? Sweep `0.3`, `0.5`, `0.7` and explain what write-through spends its wins on. (Hint: watch whose reads stay cheap and whose cache fills with keys nobody reads.)

### E4 — Shrink the herd
Set `STAMPEDE_DB_LATENCY_S = 0.0` and predict the "no protection" row before running. Why does the stampede vanish when the DB is infinitely fast — and what does that tell you about which systems *actually* suffer stampedes? Restore, then set `TTL_JITTER_FRAC = 0.05` and watch the jitter row creep back toward the unprotected disaster.

### E5 — Stretch: single-flight with request coalescing
The per-key lock makes 49 threads *wait*. Upgrade it: have the loading thread store a `threading.Event` plus a slot for the value, so waiters block on the event and read the shared result without ever touching the cache dict twice. This is `singleflight` (Go) / request coalescing — the production form of the fix.

## Deliverable

A short note (5 lines) answering E1–E4: prediction vs observed, one sentence each. Bring it to the next session — wrong predictions are the most useful thing you can bring, and they become learning records.
