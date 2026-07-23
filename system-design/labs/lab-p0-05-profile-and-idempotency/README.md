# Lab p0-05 — Profile It, Then Make It Safe to Retry

Companion to [Lesson p0-05](../../lessons/p0-05-senior-code-craft.html). The lesson's three central claims — hotspots hide until you profile, retries without idempotency duplicate money, and naive retries amplify outages — all become numbers here. Rule of the lab: **predict before you run.** Write your prediction down; the gap between prediction and output is where the learning is.

```bash
python3 craft_lab.py
```

Three experiments: (1) string-concat O(n²) vs join O(n) plus a real cProfile readout, (2) a retry storm against a payment endpoint with and without idempotency keys, (3) retry amplification on a degraded server and the SRE retry-budget fix.

## Exercises

All edits happen in the `CONFIG` block at the top of `craft_lab.py`.

### E1 — Extrapolate the quadratic
From experiment 1's table, predict the concat time for `n = 256_000` (hint: 4× input on O(n²) ≈ 16× time). Write the number down, add `256_000` to `CONCAT_SIZES`, run, compare. How far off were you, and in which direction?

### E2 — Make double charges disappear "by luck"
Predict: with `RESPONSE_LOSS_PROB = 0.01` and no idempotency key, roughly how many of the 200 clients get double-charged? Run and check. Then answer in one sentence: why is "the network is usually fine" not an acceptable defense in a payments code review?

### E3 — The worst possible client
Set `MAX_RETRIES = 10` and `RESPONSE_LOSS_PROB = 0.5`. Predict both rows of experiment 2 (total charges with and without keys) before running. Which number stayed exactly at 200, and what single server-side data structure guaranteed it?

### E4 — Find the storm threshold
With `FAILURE_RATE = 0.8` (a server in serious trouble), predict the load multiplier for 4 attempts (geometric series: 1 + 0.8 + 0.8² + 0.8³). Run and compare. Then lower `RETRY_BUDGET` to `1.05`: what does the capped multiplier become, and who pays the price for that cap (which requests give up)?

### E5 — Stretch: profile something real
Run `python3 -m cProfile -s cumulative craft_lab.py | head -30`. Identify the top three functions by `cumtime` in the whole lab. Then profile any script from your day job the same way and write down whether the hotspot was where you assumed it was.

## Deliverable

A short note (5 lines) answering E1–E4: prediction vs observed, one sentence each. Bring it to the next session — wrong predictions are the most useful thing you can bring, and they become learning records.
