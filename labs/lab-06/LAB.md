# Lab 06 — Scale Out: Replicas and the Router

Lesson: [0006-router-scaleout.html](../../lessons/0006-router-scaleout.html) · Time: ~2 h

## Before you start — MEMORY GATE

```bash
docker info --format '{{.MemTotal}}'   # want ≥ 12884901888 (12 GB to Docker)
```
Too low → Docker Desktop → Resources first. Machine swapping anyway → rerun lab with `facebook/opt-125m`; routing lessons identical.

## Objectives

- 2 engine replicas (slimmed resources, PVC-vs-RWO decision made consciously)
- Router deployed with ServiceAccount + Role + RoleBinding (it watches Pods)
- Round-robin proven in engine logs, then session affinity via `x-user-id` header

## Checkpoints — `./verify.sh`

- [ ] 2 vLLM pods Ready
- [ ] RBAC trio exists; router Ready and discovered both engines (its logs)
- [ ] `/v1/models` served through the router
- [ ] By hand: 4 same-session requests land on ONE engine (logs) — verify can't see this

## If stuck

| Symptom | Likely cause | Move |
|---|---|---|
| 2nd replica `Pending` | RWO PVC or CPU requests | You chose emptyDir/nodeSelector in step 1 — actually apply it; or lower requests |
| Router `CrashLoopBackOff`, flag error in logs | Upstream flags drifted | `kubectl logs` the exact error; check [router README](https://github.com/vllm-project/production-stack/tree/main/src/vllm_router); ask teacher |
| Router logs `Forbidden: pods is forbidden` | RBAC missing/mis-bound | ServiceAccount name in Deployment == RoleBinding subject |
| Router finds 0 engines | Label selector mismatch | `--k8s-label-selector app=vllm` must match pod labels exactly |
| Affinity not sticking | Header/flag mismatch | Session key flag must name the same header you send |
| Everything slow, fans loud | 2×CPU inference is heavy | Expected. Short prompts, `max_tokens` ≤ 10 for routing tests |

## Stretch (optional)

1. Scale to 3 replicas mid-traffic; watch router logs discover #3 with zero config. That's the K8s-watch pattern earning its keep.
2. `curl router:/metrics` — find per-engine request counts; compare with your log-based counting.
3. Read the routing logic source (`src/vllm_router/`) — find where roundrobin picks the next engine. Reading production code = free senior-engineer time.

## Leave behind

Router + 2 replicas: labs 07–10 route everything through `vllm-router.llm.svc.cluster.local`. If RAM hurts between sessions: scale engines to 1 (`helm upgrade slm charts/slm-stack --set vllm.replicaCount=1`), scale back for lab 10.
