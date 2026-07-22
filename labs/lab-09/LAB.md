# Lab 09 — Load Testing: Get the Numbers

Lesson: [0009-load-testing.html](../../lessons/0009-load-testing.html) · Time: 60–90 min

## Before you start

```bash
kubectl get pods -n llm | grep -c Running    # engines + router up
brew list k6 >/dev/null 2>&1 || brew install k6
```

## Objectives

- `vllm bench serve` (containerized) against the router at rates 0.25 / 0.5 / 1 / 2 req/s
- Saturation table filled in `load_tests/RESULTS.md`
- `load_tests/chat.js` k6 scenario with SLO thresholds — a real pass/fail gate
- One full run narrated against Grafana

## Checkpoints — `./verify.sh`

- [ ] k6 installed, `chat.js` parses, thresholds + stages present
- [ ] `load_tests/RESULTS.md` exists with your numbers (≥3 rates)
- [ ] Bench result JSON saved
- [ ] By hand: you can point at the knee in your table and say "capacity"

## If stuck

| Symptom | Likely cause | Move |
|---|---|---|
| bench: connection refused | port-forward down / wrong host | Forward router; from container use `host.docker.internal` |
| bench: model not found | Name mismatch | `--model` must equal an id from `/v1/models` |
| All k6 requests timeout | CPU stack slower than timeout | `timeout: '120s'`, `max_tokens: 32`, fewer VUs |
| Numbers absurdly good | You hit a cached/error path | Check k6 `http_req_failed`; 100% errors = "fast" |
| Mac melts | 2 engines + bench + browser | Close what you can; this IS the saturation experiment |

## Stretch (optional)

1. Rerun the 0.5 req/s bench with **1** engine (scale down) — quantify what the second replica buys. That's a capacity-planning datapoint, the real job.
2. Session-affinity ON vs round-robin at same rate: compare P50 TTFT. You're measuring the KV-cache-reuse dividend.
3. `k6 run --out json=run.json` and plot request duration over time — see the ramp phases in data.

## Leave behind

`load_tests/` with scripts + RESULTS.md — capstone README material.
