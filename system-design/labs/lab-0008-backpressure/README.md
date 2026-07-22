# Lab 0008 — Backpressure

Companion to [Lesson 0008](../../lessons/0008-async-and-communication.html). Everything the lesson claimed about queues — the hockey stick, the runaway unbounded queue, bounded admission with 503s, retry storms vs backoff+jitter — you now watch happen in a real `queue.Queue` with real threads. Rule of the lab: **predict before you run.** Write your prediction down; the gap between prediction and output is where the learning is.

```bash
python3 backpressure_lab.py
```

Stdlib only, no network, ~10 s wall time. One consumer thread plays a fixed-capacity service (~100 req/s, ±40% service-time variance); wall clock is compressed 5× and all waits are printed in *simulated* milliseconds. Timings ride on real thread scheduling, so numbers wiggle slightly between runs — the shapes never do.

Three experiments: (1) arrival-rate sweep 50%→150% of capacity into an **unbounded** queue — the utilization–latency hockey stick, plus the runaway queue past 100%; (2) the same sweep into a **bounded** queue with immediate 503 rejection — accepted-request latency stays flat, rejections absorb the overload; (3) rejected clients retry — naive immediate retry vs exponential backoff with full jitter.

## Exercises

All edits happen in the `CONFIG` block at the top of `backpressure_lab.py`. Restore defaults after each exercise.

### E1 — Find the knee
The lesson's M/M/1 table says waits scale like ρ/(1−ρ): 4× service time at 80% utilization, 9× at 90%, 19× at 95%. Add `0.80` and `0.95` to `SWEEP`. Predict the mean waits at 80% and 95% first (mean service time is 10 ms — do the arithmetic). Run. How close does a messy threaded simulation come to textbook queueing theory, and where does it deviate?

### E2 — Choose the bound with Little's law
In experiment 2, the wait ceiling is roughly `QUEUE_BOUND / SERVICE_RATE`. Predict the p99 wait and the 150%-load rejection rate for `QUEUE_BOUND = 5`, then for `QUEUE_BOUND = 100`. Run both. You are watching the real trade: a deep bound buys fewer rejections at the price of worse accepted-request latency. Which bound would you pick if your SLO says p99 queueing ≤ 100 ms, and what rejection rate does that force you to accept at 150% load?

### E3 — The retry budget lie
"If retries fail, add more retries." Set `MAX_RETRIES = 8`. Predict amplification and success rate for *both* policies before running. Lesson: extra retries are worthless if they land inside the overload spike (naive burns twice the traffic for the same success rate) and decisive if they land after it (backoff should hit ~100%). This is why the Google SRE book caps attempts and budgets retries instead of piling them on.

### E4 — Manufacture the thundering herd
First flip `BACKOFF_JITTER = False` and re-run. Surprise: success may *improve* — because deterministic delay waits the full cap (longer than jitter's average cap/2), and this experiment's Poisson arrivals already desynchronize the rejections. Jitter looks useless… until the rejections are synchronized. Now set `OVERLOAD = 20.0` (all 200 clients arrive as one ~100 ms spike) and compare `BACKOFF_JITTER = False` vs `True`. Without jitter the retries return as synchronized waves that keep colliding with each other; with jitter they smear flat. Write down both success rates.

### E5 — Stretch: priority tiers
Add a second traffic class: tag each request in experiment 2 as `interactive` (30%) or `batch` (70%), and when the queue has fewer than 5 free slots, reject *batch* requests even though space remains — reserving headroom for interactive. Print rejection rate and p99 wait per class. You have just implemented load shedding by priority — the same policy your inference-gateway project step defines on paper.

## Deliverable

A short note (5 lines) answering E1–E4: prediction vs observed, one sentence each. Bring it to the next session — wrong predictions are the most useful thing you can bring, and they become learning records.
