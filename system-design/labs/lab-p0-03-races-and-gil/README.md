# Lab p0-03 — Races, Locks, the GIL, and the Event Loop

Companion to [Lesson p0-03](../../lessons/p0-03-concurrency.html). **Run this lab FIRST, read the lesson second** — the lesson explains what you just watched happen. Rule of the lab: **predict before you run.** Write your prediction down; the gap between prediction and output is where the learning is.

```bash
python3 concurrency_lab.py
```

Four experiments: (1) the lost-update race, unsynchronized vs locked, (2) deadlock from opposite lock order vs a global lock order, (3) CPU-bound work on threads vs processes under the GIL, (4) 1,000 fake I/O calls on an asyncio event loop vs a thread pool.

## Exercises

All edits happen in the `CONFIG` block at the top of `concurrency_lab.py`.

### E1 — How bad can a race get?
Predict: with `RACE_THREADS = 8` instead of 4, does the **lost fraction** go up, down, or stay the same? Why would more writers change the collision odds? Write your guess, change it, run twice, compare across the trials. Then restore.

### E2 — Make the race disappear (without a lock)
Set `SWITCH_INTERVAL = 0.005` (CPython's default). Predict: how many updates get lost now? Run it three times. Lesson to internalize: a race that "never happens" on your laptop is still a race — the window is open on every run, and production traffic + different hardware will eventually hit it. Restore `5e-6`.

### E3 — Where does the process speedup go?
Experiment 3 shows processes beating threads, but not by the ideal core count. Predict the three timings for `CPU_CHUNK = 2_000_000` (6× less work): does the process speedup grow or shrink? Run and explain the result in one sentence (hint: spawn + IPC overhead is roughly constant while the work shrank).

### E4 — Size the pool like an SRE
With `IO_MS = 50`, ideal pool time is `IO_TASKS / THREAD_POOL_WORKERS × 50 ms`. Predict wall time for `THREAD_POOL_WORKERS = 10`, then for `500`. Run both. Which knob did NOT move asyncio's time, and why does the event loop not care about a worker count at all?

### E5 — Stretch: block the loop
Add a CPU-bound coroutine to the asyncio batch: one task that runs `cpu_work(20_000_000)` **without** awaiting. Predict what happens to total asyncio wall time, then measure. You have just reproduced the number-one async production bug: one blocking call starves every other task on the loop.

## Deliverable

A short note (5 lines) answering E1–E4: prediction vs observed, one sentence each. Bring it to the next session — wrong predictions are the most useful thing you can bring, and they become learning records.
