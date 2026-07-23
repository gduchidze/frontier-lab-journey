# Lab p0-02 — Processes and Memory

Companion to [Lesson p0-02](../../lessons/p0-02-os-essentials.html). Everything the lesson claims about process cost, lazy memory, thrashing, and context switches, you now verify with your own runs. Rule of the lab: **predict before you run.** Write your prediction down; the gap between prediction and output is where the learning is.

```bash
python3 os_lab.py
```

Four experiments: (1) creation cost of thread vs fork vs spawn, (2) allocation vs first-touch page faults, (3) an LRU paging simulator that walks off the thrashing cliff, (4) the price of a context switch.

## Exercises

All edits happen in the `CONFIG` block at the top of `os_lab.py`.

### E1 — Creation cost ratios
Predict the per-unit ratio thread : fork : spawn before your first run (guess actual multipliers, not just the order). Then set `THREADS = 1000`: does per-thread cost stay flat, or does creating many threads get more expensive per thread? Explain using what a thread does and does not share.

### E2 — Page-fault math scales linearly (or does it?)
Experiment 2 reports an implied per-page soft-fault cost. Predict the first-touch time for `ALLOC_MB = 1024` (4× the pages), then run. Within what % was the linear extrapolation right? Restore to 256 after.

### E3 — Find the cliff's edge
With `RAM_PAGES = 256`, the LRU fault rate for an oversized uniform working set W is roughly `1 − RAM/W`. Predict the fault rate for `W = 260` and `W = 320`, add both to `WORKING_SETS`, and run. How sharp is the cliff just 1.5% past RAM? This is why "we're at 98% memory, we're fine" is a famous last sentence.

### E4 — What if swap were faster?
Keep a 33% fault rate row (working set 384). Sweep `FAULT_COST_US` through `10_000` (HDD), `1_000` (SSD), and `10` (compressed RAM, like zswap). Predict each slowdown first via `eff = (1−r)·hit + r·fault`. At what fault cost does a 33% miss rate stay under 100× slowdown — and does any realistic device achieve it?

### E5 — Stretch: locality rescues paging
Replace the uniform access in `_lru_faults` with a 90/10 hot-cold pattern (90% of accesses go to the first 10% of pages). Predict: for `W = 512`, does the fault rate beat `1 − RAM/W`? Why? Connect your answer to why vLLM's PagedAttention can pack KV-cache blocks without thrashing.

## Deliverable

A short note (5 lines) answering E1–E4: prediction vs observed, one sentence each. Bring it to the next session — wrong predictions are the most useful thing you can bring, and they become learning records.
