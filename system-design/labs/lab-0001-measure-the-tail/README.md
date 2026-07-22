# Lab 0001 — Measure the Tail

Companion to [Lesson 0001](../../lessons/0001-performance-vocabulary.html). Everything the lesson claimed, you now verify with your own runs. Rule of the lab: **predict before you run.** Write your prediction down; the gap between prediction and output is where the learning is.

```bash
python3 latency_lab.py
```

Three experiments: (1) mean vs percentiles on a service with a 1% slow tail, (2) tail amplification under fan-out, (3) the batching throughput/latency trade.

## Exercises

All edits happen in the `CONFIG` block at the top of `latency_lab.py`.

### E1 — Kill the tail
Predict: what happens to **mean** vs **p99** if `TAIL_PROB` drops from `0.01` to `0.001`? Which moves more, in relative terms? Write your guess, change it, run, compare. Then restore.

### E2 — The invisible catastrophe
Set `TAIL_MS = 10_000` (10-second stalls) with `TAIL_PROB = 0.001`. Predict the mean and the p99 first. Lesson: which monitoring alert would have caught this — one on mean latency or one on p999?

### E3 — Find your fan-out budget
Your SLO says at most 10% of page loads may exceed the single-call p99. Using experiment 2's `theory` column (`1 − 0.99^N`), compute the maximum N by hand, then confirm by adding your value to `FANOUTS`. (Sanity anchor: lesson said N=100 → ~63%.)

### E4 — Batching sweet spot
With `ARRIVAL_RATE_RPS = 400`, which batch size gives the best throughput-per-ms-of-latency? Now set `ARRIVAL_RATE_RPS = 20` and re-run: why does large-batch latency explode when traffic is light? (This exact failure is why real inference servers use a batching *timeout* — you'll design one in Phase 4.)

### E5 — Stretch: real network percentiles
Replace the simulator with reality: time 200 `HEAD` requests to any URL using `urllib.request` + `time.perf_counter()`, feed the samples into `Summary.of()`, and compare your home network's p50/p99 ratio to the simulator's.

## Deliverable

A short note (5 lines) answering E1–E4: prediction vs observed, one sentence each. Bring it to the next session — wrong predictions are the most useful thing you can bring, and they become learning records.
