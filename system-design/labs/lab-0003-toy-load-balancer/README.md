# Lab 0003 — Toy Load Balancer

Companion to [Lesson 0003](../../lessons/0003-traffic-edge.html). Three real HTTP backends, one load balancer with a pluggable strategy, background health checks, and a mid-run backend murder so you can watch failover with your own eyes. Rule of the lab: **predict before you run.** Write your prediction down; the gap between prediction and output is where the learning is.

```bash
python3 toy_lb.py --demo
```

The demo runs two phases: (1) 30 requests with all backends up — a distribution table plus client-side latency (mean/p50/p99); (2) 30 more requests, killing `backend-2` after the first 8 — watch the health checker and the retry path keep client-visible errors at zero while the survivors absorb the traffic. If your environment forbids binding localhost sockets, the script automatically falls back to an in-process simulation exercising the exact same strategy and health-check code.

## Exercises

All edits happen in the `CONFIG` block at the top of `toy_lb.py`.

### E1 — Skew the delays
Set `BACKEND_DELAYS_MS = [10, 10, 300]` and keep `STRATEGY = "round_robin"`. Predict the phase-1 distribution table (easy) and — the real question — the **p99**: round-robin gives the slow backend a third of the traffic, so what fraction of your requests eat ~300 ms, and where must p99 land? Write your guess, run, compare. Then answer in one sentence: *why does "fair by count" hurt the tail when servers aren't identical?*

### E2 — Switch strategies
Same skewed delays, but `STRATEGY = "least_connections"`. Predict first: does the slow backend get more, equal, or fewer requests than under round-robin? What happens to the **mean** vs the **p99**? Run and compare tables side by side. Then set `CLIENT_CONCURRENCY = 1` and re-run: why does least-connections lose most of its advantage when only one request is in flight at a time? Restore `4` when done.

### E3 — Tune the health checks
Detection time ≈ `HEALTH_INTERVAL_S × FAILS_TO_MARK_DOWN`. With the defaults (0.25 s × 2 → ~0.5 s), phase 2 shows only a few errors charged to the dead backend before it leaves rotation. Predict what happens with `HEALTH_INTERVAL_S = 2.0` and `FAILS_TO_MARK_DOWN = 5` — how many phase-2 picks hit the corpse before it's ejected? (Watch the per-backend `errors` column; clients stay at zero errors because the LB retries.) Then flip to the paranoid end (`0.05` / `1`) and say in one sentence what real-world risk that setting carries even though this demo can't show it. (Hint: lesson section 7, *flapping*.)

### E4 — Thought experiment: LLM serving
No code for this one. Your backends are now GPU servers running an LLM, and the traffic is a mix of 100-token and 10,000-token generations — a 100× spread in per-request cost hiding behind identical HTTP calls. Which of this lab's two strategies is the right starting point, and why exactly does the other one collapse? Connect your E1/E2 tables to lesson sections 6 and 10: what does a long generation do to the "fair by count" assumption, and what signal does least-connections (a.k.a. least-outstanding-requests) implicitly track that round-robin cannot see?

## Deliverable

A short note (5 lines) answering E1–E4: prediction vs observed, one sentence each. Bring it to the next session — wrong predictions are the most useful thing you can bring, and they become learning records.
