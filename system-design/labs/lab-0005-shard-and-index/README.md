# Lab 0005 — Shard and Index

Companion to [Lesson 0005](../../lessons/0005-rdbms-scaling.html). Everything the lesson claimed about indexes, composite ordering, and sharding, you now verify with your own runs. Rule of the lab: **predict before you run.** Write your prediction down; the gap between prediction and output is where the learning is.

```bash
python3 shard_index_lab.py
```

Three experiments on a 300,000-row `messages(user_id, conversation_id, created_at, body)` table: (1) point and range queries without vs with an index, plus `EXPLAIN QUERY PLAN` receipts, (2) composite index ordering — `(user_id, created_at)` vs `(created_at, user_id)` for "last 50 messages of user X", (3) hash-sharding across 4 SQLite databases — balanced under uniform activity, a hot shard under Zipf activity, and a cross-shard top-10 query that forces scatter-gather. Uses in-memory databases plus temp files that delete themselves.

## Exercises

All edits happen in the `CONFIG` block at the top of `shard_index_lab.py`.

### E1 — Shrink the table
Predict: if `N_ROWS` drops from `300_000` to `30_000`, what happens to the point-lookup speedup in experiment 1 — does it grow, shrink, or stay put? (Hint: the scan is O(n), the index walk is O(log n) — which side of the ratio moved?) Write your guess, change it, run, compare. Then restore.

### E2 — Break the index's usefulness
Set `RANGE_HOURS = 720` (the whole 30 days). Predict experiment 1's range-query speedup before running. Lesson: an index helps in proportion to its *selectivity* — when the range matches every row, walking index + table can be no better than one clean scan.

### E3 — Turn the heat up, then off
Run once with `ZIPF_EXPONENT = 0.0` (uniform) and once with `1.5`. Predict the hottest shard's share of rows in each case before running. Then answer: which config change would a real team ship to fix the 1.5 case — more shards, or a different unit of sharding for the hot key?

### E4 — More shards don't cool a celebrity
Set `N_SHARDS = 8` with `ZIPF_EXPONENT = 1.2`. Predict: does the hottest shard's *percentage* halve compared to 4 shards? Explain what you observe using one sentence from the lesson's hot-key bullet. (Also notice: every row is now on a different shard than before — that's the `% N` resharding tax.)

### E5 — Stretch: build a covering index
In experiment 2's winning query, change the index to `(user_id, created_at, body)` and re-check the plan output. You should see SQLite report a **covering index** and refuse to touch the table at all. Measure whether the timing moves, and explain why the effect is small here but large on disk-backed tables.

## Deliverable

A short note (5 lines) answering E1–E4: prediction vs observed, one sentence each. Bring it to the next session — wrong predictions are the most useful thing you can bring, and they become learning records.
