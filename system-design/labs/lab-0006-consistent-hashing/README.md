# Lab 0006 — Consistent Hashing

Companion to [Lesson 0006](../../lessons/0006-nosql-taxonomy.html). Everything the lesson claimed about `hash(key) % N`, the ring, virtual nodes, and hot keys, you now verify with your own runs. Rule of the lab: **predict before you run.** Write your prediction down; the gap between prediction and output is where the learning is.

```bash
python3 hash_ring_lab.py
```

Four experiments: (1) add a 6th node to a 5-node cluster — % of 100k keys that move under mod-N vs a vnode ring, (2) remove a node, same comparison, (3) per-node key-count imbalance as vnodes sweep {1, 10, 100, 500}, (4) hot-key reality check — zipf-distributed popularity shows the ring balances key *count* but not *load*.

## Exercises

All edits happen in the `CONFIG` block at the top of `hash_ring_lab.py`.

### E1 — The lottery of one token
Before re-reading experiment 3's output: predict the **max/fair** ratio for `vnodes = 1` and for `vnodes = 100`. Then predict what `vnodes = 2000` buys over 500. Add `2000` to `VNODE_SWEEP`, run, compare — where does the smoothing flatten out, and what does each extra vnode cost (ring size = nodes × vnodes entries)?

### E2 — Big-cluster arithmetic
Set `NUM_NODES = 50`. Predict experiment 1's two "keys moved" numbers first (hint: the ring's theory is `1/(N+1)`; mod-N stays terrible). Lesson: the ring's advantage *grows* with cluster size — exactly when you need it.

### E3 — Cache-stampede math
Using experiment 1's mod-N number and lesson §5's method: your cache tier runs at a 95% hit rate in front of a database. Compute the database read multiplier right after a mod-N resize (miss rate jumps from 5% to ≈ the moved fraction). Would your favorite RDBMS survive a 17× read surge? Which alert fires first?

### E4 — Taming the hot key
In experiment 4, sweep `ZIPF_EXPONENT` through `0.7`, `1.1`, `1.3`. Predict the hottest node's traffic share each time before running. Then answer in one sentence each: why doesn't raising `RING_VNODES` help, and which two mitigations from lesson §9 would you deploy first?

### E5 — Stretch: salt the celebrity
Implement hot-key salting: replace the single hottest key with `R = 5` copies (`key#0…key#4`), spread its weight equally across them, and re-run experiment 4. How far does the hottest node's share drop, and what did reads have to pay for it?

## Deliverable

A short note (5 lines) answering E1–E4: prediction vs observed, one sentence each. Bring it to the next session — wrong predictions are the most useful thing you can bring, and they become learning records.
