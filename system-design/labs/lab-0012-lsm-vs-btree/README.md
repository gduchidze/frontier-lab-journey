# Lab 0012 — LSM vs B-tree

Companion to [Lesson 0012](../../lessons/0012-storage-engine-internals.html). Both storage engines from the lesson are built here in ~300 lines of stdlib Python, racing on identical workloads — write amplification, bloom filters, read amplification, compaction: all of it becomes numbers you produced yourself. Rule of the lab: **predict before you run.** Write your prediction down; the gap between prediction and output is where the learning is.

```bash
python3 lsm_btree_lab.py
```

Three experiments: (1) write 100k keys into both engines and compare total write cost + write amplification (LSM: entries rewritten by size-tiered compaction; B-tree: whole pages flushed from a 32-page buffer pool), (2) point-read cost for hot, cold, and *missing* keys — LSM with blooms vs without vs the B-tree's flat descent, (3) range scans of 100 keys — the LSM must seek into every SSTable, the B-tree walks sibling pages.

Everything is simulated: cost = comparisons made + bloom probes + entries rewritten, so runs are exact and reproducible (seeded RNG, finishes in well under a second). The bloom "filter" is a perfect set of keys per table — real blooms add a small false-positive rate on top of what you measure here.

## Exercises

All edits happen in the `CONFIG` block at the top of `lsm_btree_lab.py`.

### E1 — Halve the memtable
Predict: if `MEMTABLE_LIMIT` drops from `2000` to `1000`, does LSM write amplification rise or fall, and roughly by how much? Reason from tiers: twice the flushes means one extra merge generation for most entries. Run, compare to your number, restore. Lesson: the memtable threshold is a write-amp dial, not a memory dial.

### E2 — Turn off the blooms
Set `BLOOM_ENABLED = False` (experiment 2 prints both columns regardless — so instead: predict the "LSM no bloom" column before your first run counts). Predict the *ratio* for missing keys: bloom probes cost 1 per table, a binary search costs ~log2(table) — with 5 tables, how much worse is life without blooms? Then set `COMPACTION_ENABLED = False` too and watch the no-bloom missing-key cost against 50 tables.

### E3 — Random keys, B-tree pain
Switch `KEY_PATTERN` from `"sequential"` to `"random"` and predict the B-tree's write amp before running (sequential gave ~2x). Random inserts land on random pages; the 32-page buffer pool evicts a dirty page for almost every insert. This is exactly why random UUIDv4 primary keys wreck InnoDB and why ULID/sequential keys exist. Does the LSM's write amp change at all? Why not?

### E4 — Let compaction debt pile up
Set `COMPACTION_ENABLED = False` and predict three numbers before running: LSM write amp, cold-key point-read cost (blooms still on), and range-scan cost. Writes get *cheaper* (write amp → 1.0) while both read costs rot as tables accumulate — 50 sstables, every one a mandatory seek for range scans. Compaction is not overhead; it is the read path's rent, paid in write amplification.

### E5 — Stretch: leveled compaction
Size-tiered merges equal-sized tables; leveled (LevelDB/RocksDB-style) instead maintains one sorted run per level, each ~`FANOUT`x larger, merging a flushed table *into* the next level. Implement it: on flush, merge the new table into a single L1 run; when L1 exceeds `FANOUT × MEMTABLE_LIMIT`, merge into L2, and so on. Compare write amp (it should rise — each entry is rewritten per level) and read cost (it should fall — far fewer tables to consult). You have just reproduced the leveled-vs-size-tiered trade-off from the lesson's amplification table.

## Deliverable

A short note (5 lines) answering E1–E4: prediction vs observed, one sentence each. Bring it to the next session — wrong predictions are the most useful thing you can bring, and they become learning records.
