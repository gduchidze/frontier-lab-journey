# Lab 0013 — Mini Kafka

Companion to [Lesson 0013](../../lessons/0013-streams-and-events.html). Everything the lesson claimed — per-partition ordering, hot-key skew, the consumer-count ceiling, where duplicates actually come from, what compaction keeps and what it destroys — you now verify with your own runs. Rule of the lab: **predict before you run.** Write your prediction down; the gap between prediction and output is where the learning is.

```bash
python3 mini_kafka_lab.py
```

Three experiments: (1) 50k keyed events hashed across 8 partitions — per-key order violations counted (spoiler: zero) vs global-order inversions in a round-robin read (~half of all adjacent pairs), plus a partition-size skew table under zipf(1.1) keys, (2) a consumer group sweep from 1 to 12 consumers over 8 partitions — watch speedup hit the partition ceiling — then a mid-run consumer crash comparing commit-after-batch (duplicates) with commit-before-batch (losses), (3) a 30k-update changelog compacted to latest-value-per-key, with state rebuilt from both and replay counts compared.

Everything is simulated: partitioning is a deterministic CRC32 hash, "processing" charges a fixed cost per event, and the crash is modeled by cutting the consumer's progress at a configurable point — so every duplicate and every lost event is exactly countable.

## Exercises

All edits happen in the `CONFIG` block at the top of `mini_kafka_lab.py`.

### E1 — The parallelism ceiling
Predict: with `NUM_PARTITIONS = 4`, how many of the 8 consumers in experiment 2's `CONSUMER_COUNTS` row for 8 sit idle, and what happens to the best finish time? Write it down, set it, run, compare. Then restore. Lesson: consumer count beyond partition count buys exactly nothing — partitions are the parallelism budget you fix at design time.

### E2 — Buy fewer duplicates
The crash run commits every `COMMIT_EVERY = 500` events and produces ~148 duplicates. Predict the duplicate count at `COMMIT_EVERY = 2_000` and at `50`, then run both. What is the relationship between commit interval and worst-case redelivery — and what does each commit cost you in exchange?

### E3 — Crank the celebrity
Set `ZIPF_S = 1.3` (hotter hot keys). Predict the worst partition's share of all events before running (at 1.1 it was ~23% against an even 12.5%). How does the hot partition change experiment 2's finish times even when no consumer is idle? Restore afterwards.

### E4 — Poison pill
Set `POISON_OFFSET = 1_000`. Before running, predict both rows of the new table: how many events sit blocked behind one unprocessable event if the consumer retries forever, and what a dead-letter queue changes. Then answer in one sentence: what property of the partition did the DLQ sacrifice to make progress?

### E5 — Stretch: idempotent consumer
The crash experiment counts ~148 duplicate deliveries. Make them harmless: add a consumer that keeps a `set` of processed `(partition, offset)` pairs (or event `seq` numbers) and skips events it has already seen, then re-run the crash and show effective (deduplicated) processing count equals the partition totals exactly. That set is the in-memory form of the idempotency key the lesson says belongs in your database.

## Deliverable

A short note (5 lines) answering E1–E4: prediction vs observed, one sentence each. Bring it to the next session — wrong predictions are the most useful thing you can bring, and they become learning records.
