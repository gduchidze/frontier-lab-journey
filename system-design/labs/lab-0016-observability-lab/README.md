# Lab 0016 — Observability Lab

Companion to [Lesson 0016](../../lessons/0016-observability-and-ops.html). Everything the lesson claimed — RED tables exposing a fault, error budgets consumed by one bad window, burn-rate paging beating naive thresholds, traces naming the guilty hop — you now verify with your own runs. Rule of the lab: **predict before you run.** Write your prediction down; the gap between prediction and output is where the learning is.

```bash
python3 observability_lab.py
```

A 3-service chain (gateway → orders → payments) emits one structured event per request for a compressed "month": 1,440 simulated minutes at 140 req/min (~200k requests). Two injected faults — payments slowness 10:00–10:05 and a payments error burst 15:00–15:10 — plus three 1-minute error blips that should *not* page anyone.

Three experiments plus a demo: (1) RED tables per service per minute — spot both faults in raw numbers, and notice p99 fingers *payments* while err% only says *when*, (2) SLO math — availability + latency SLIs vs a 99.9% SLO, budget-remaining timeline, and how one 6-minute window eats ~78% of the monthly latency budget, (3) burn-rate alerting — fast (1h+5m, 14.4×) and slow (6h+30m, 6×) multi-window alerts vs a naive per-minute error threshold, scored on pages fired, false pages, incidents caught, and detection delay. The demo reconstructs the slowest request's span tree (guilty hop: payments) and counts metric time series for the cardinality exercise.

Everything is simulated and deterministic (seeded RNG): the "services" are latency samples and a status code, so budgets and burn rates are exact and every run is reproducible.

## Exercises

All edits happen in the `CONFIG` block at the top of `observability_lab.py`.

### E1 — Buy a tighter SLO
Predict: at 99.95% (`SLO = 0.9995`), how many bad events is the monthly budget — and do both faults now blow their budgets? Do the arithmetic first (0.05% of 201,600), then run and check the month-end budget lines. What would you tell the team that wants 99.99%?

### E2 — Shrink the fault, watch who stays silent
Set `ERROR_WINDOW = (900, 902)` (a 3-minute burst). Predict which alerts still fire: naive? fast burn? slow burn? Run and explain why a burst that eats ~20% of the monthly budget in 3 minutes may still — correctly — not deserve a page. Restore afterwards.

### E3 — Explode the cardinality
Predict the series count when `METRIC_LABELS = ("service", "user_id")` — closer to 3, 50k, or 150k? Run, look at the demo's last line, and write one sentence on why per-user latency belongs in *traces or logs*, never in metric labels.

### E4 — Sample away the evidence
Set `LOG_SAMPLE_RATE = 100` (keep 1 in 100 traces). Predict: how many traces survive inside the 6-minute slow window, and can the demo still print a guilty-hop tree? Run twice with different `SEED`s if you want to see luck at work. What does this say about head sampling during the incident you most need traces for?

### E5 — Stretch: tail-based sampling
Head sampling decides at trace start; tail sampling decides after the outcome is known. Modify the `kept` logic in `demo_trace_and_cardinality` to keep **all** traces that are bad (status 500 or end-to-end > `LATENCY_SLO_MS`) plus 1 in 100 of the good ones. Confirm the guilty hop survives even at aggressive sampling — and count how many traces you now store versus `LOG_SAMPLE_RATE = 1`.

## Deliverable

A short note (5 lines) answering E1–E4: prediction vs observed, one sentence each. Bring it to the next session — wrong predictions are the most useful thing you can bring, and they become learning records.
