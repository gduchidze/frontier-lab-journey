# Lab 0004 — Replication Lag

Companion to [Lesson 0004](../../lessons/0004-cap-and-replication.html). Everything the lesson claimed about lag, read-your-writes, quorums, and nines, you now verify with your own runs. Rule of the lab: **predict before you run.** Write your prediction down; the gap between prediction and output is where the learning is.

```bash
python3 replication_lab.py
```

Four experiments: (1) stale-read % vs how long you wait after writing, (2) read-your-writes via leader pinning and its cost, (3) the R + W > N quorum overlap guarantee, (4) availability arithmetic — nines, serial chains, parallel redundancy.

## Exercises

All edits happen in the `CONFIG` block at the top of `replication_lab.py`.

### E1 — Slower replication
Predict: if `REPL_MEDIAN_MS` goes from `30` to `120`, what happens to the stale-read % at read delay 100 ms? At 500 ms? Write your guesses, change it, run, compare. Then restore.

### E2 — The tail strikes again
Keep the median at 30 ms but double `REPL_SIGMA` to `1.6`. The *median* replication delay is unchanged — predict whether stale reads at 250 ms rise or fall, then explain the result using Lesson 0001's tail vocabulary. Lesson: "replication lag is usually small" and "replication lag is bounded" are very different claims.

### E3 — Quorum at N = 5
Set `N_REPLICAS = 5`. Before running, list every (W, R) pair out of the 25 that guarantees overlap, using R + W > N. Confirm each shows exactly 0.000%. Then answer: which (W, R) would you pick for a write-heavy workload, and which for a read-heavy one, and what do you give up in each case?

### E4 — Buying nines
Experiment 4 showed two 99.9% services in series land at ~99.8%. How many **99%** replicas in parallel does it take to beat a single 99.99% box? Compute `1 − 0.01^k` by hand for k = 1, 2, 3, then set `COMPOSED = 0.99` and check the parallel row against your k = 2 answer.

### E5 — Stretch: monotonic reads
Modify experiment 1 so each session reads **twice**, from two *different* random replicas, and count how often the second read is staler than the first (the user watches their message vanish — time travel). Then fix it the standard way: pin each session to one replica, and confirm the anomaly disappears even though staleness itself does not.

## Deliverable

A short note (5 lines) answering E1–E4: prediction vs observed, one sentence each. Bring it to the next session — wrong predictions are the most useful thing you can bring, and they become learning records.
