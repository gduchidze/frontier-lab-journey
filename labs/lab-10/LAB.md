# Lab 10 — Autoscaling and the Capstone

Lesson: [0010-autoscaling-capstone.html](../../lessons/0010-autoscaling-capstone.html) · Time: ~2 h + writeup

## Before you start

```bash
kubectl get pods -n llm,monitoring 2>/dev/null || kubectl get pods -n llm && kubectl get pods -n monitoring
```

## Objectives — part A (mechanism)

- metrics-server installed (kind needs `--kubelet-insecure-tls`)
- HPA on the vLLM Deployment (CPU 70%, min 1 / max 2, 5-min scale-down window)
- Full loop witnessed: load → scale-out → router discovers → drain → scale-in
- You can say WHY CPU% is the wrong signal and what KEDA + `num_requests_waiting` fixes

## Objectives — part B (capstone)

- Repo restructured; `main.py` deleted; conventional commits
- README: pitch → architecture diagram → tested-from-scratch quickstart → benchmark table + Grafana screenshot → design decisions & limitations
- Mock interview with the teacher agent survived

## Checkpoints — `./verify.sh`

- [ ] `kubectl top nodes` works
- [ ] HPA exists, targets live (not `<unknown>`), stabilization window set
- [ ] By hand: scale-out AND scale-in both observed (paste timestamps in learning record)
- [ ] README sections present; quickstart replayed on a fresh cluster (the real final exam)

## If stuck

| Symptom | Likely cause | Move |
|---|---|---|
| `top` → "Metrics API not available" | metrics-server TLS on kind | The `--kubelet-insecure-tls` arg; wait 30 s |
| HPA target `<unknown>` | No CPU *request* on container | HPA computes % of request — your chart sets it, check the render |
| Scales up, never down | Window (good!) or steady load | Stop traffic fully; wait the 300 s |
| New replica Ready but idle | Router discovery lag | Watch router logs; seconds, not minutes |
| 2nd replica `Pending` | The RWO/memory issue from lab 06 | Same fix you chose then |

## Stretch (the real-world ending)

1. KEDA `ScaledObject` on `sum(vllm:num_requests_waiting) > 5` — the production answer. Document even if only prototyped.
2. Chaos day: engine kill / router kill / node kill (`docker stop llm-stack-worker`) during k6 load — write down blast radius of each. That's an incident-review skill.
3. Post the repo to r/LocalLLaMA or vLLM Slack (#production-stack). Real feedback = the wisdom step.

## The final exam (1 week later)

`kind delete cluster --name llm-stack` → rebuild everything from your README only. What you must look up = what to review.
