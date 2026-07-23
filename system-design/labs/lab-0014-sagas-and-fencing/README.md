# Lab 0014 — Sagas & Fencing

Companion to [Lesson 0014](../../lessons/0014-distributed-transactions.html). Everything the lesson claimed — the dual-write hole, the outbox trade, saga compensation and its failure, the GC-pause lock corruption that fencing tokens prevent — you now verify with your own runs. Rule of the lab: **predict before you run.** Write your prediction down; the gap between prediction and output is where the learning is.

```bash
python3 saga_lab.py
```

Three experiments: (1) naive dual write (commit DB, then publish) with a 2% crash injected between the two, 10,000 orders — count the committed-but-never-published orders, then the outbox+relay version: zero lost, but duplicates appear, and consumer dedup turns at-least-once into effectively-once; (2) a four-step checkout saga (order → payment → inventory → shipment) with 3% per-step crash injection — no compensation vs one-shot compensation vs retry-until-success, with an invariant check (no run may end charged-but-unshipped); (3) a TTL lock where worker A's simulated GC pause sometimes outlives the lease, worker B acquires and writes, then A's stale write lands — with and without a monotonic fencing token checked at the resource.

Everything is simulated: crashes are seeded coin flips placed at exactly the points where real processes die, so counts are exact and reproducible — no broker, no Redis, no threads.

## Exercises

All edits happen in the `CONFIG` block at the top of `saga_lab.py`.

### E1 — Price the dual-write hole
Predict: at `CRASH_AFTER_COMMIT_RATE = 0.05`, how many of the 10,000 orders are committed but never published? Write the number down, change it, run, compare. Then translate: at your day job's order volume, how many silently lost events per day is that? Restore to `0.02`.

### E2 — Grow the stuck queue
Predict the `stuck` count for "compensate, 1 attempt" if `COMP_FAIL_RATE` rises from `0.10` to `0.40`. (Hint: ~1,100 runs need compensation; each run needs 1–3 compensations, each failing 40% of the time.) Run, compare, and note that "compensate + retry" still shows 0 stuck — then say out loud what property of the compensation makes infinite retry safe.

### E3 — Race the lease
The pause is exponential with mean `PAUSE_MEAN_S = 4` and the lease is `LOCK_TTL_S = 10`, so P(pause > TTL) = e^(−10/4) ≈ 8.2%. Predict the corrupted-write count at `LOCK_TTL_S = 4.0`, then at `20.0`. Run both. Notice corruption never reaches zero for any finite TTL — that is Kleppmann's argument for why the *resource* must check the token.

### E4 — Break effectively-once
Set `CONSUMER_DEDUP = False` and predict the "consumer applied" number for the outbox row. Then set `COMP_IDEMPOTENT = False` and watch the `double-comps` column in experiment 2: those are refunds issued twice. Restore both to `True` and state the rule: at-least-once delivery is only safe in front of idempotent handlers.

### E5 — Stretch: choreography variant
Rewrite experiment 2 as a choreography saga: no orchestrator — each service, on finishing, emits an event that triggers the next, and on failure emits a failure event that each upstream service must independently subscribe to and compensate from. Log every event to a trace list. Compare the trace length and the number of subscription edges against the orchestrated version, then answer: which one would you rather debug at 3 a.m., and which one has no single point of failure?

## Deliverable

A short note (5 lines) answering E1–E4: prediction vs observed, one sentence each. Bring it to the next session — wrong predictions are the most useful thing you can bring, and they become learning records.
