# Lab 02 — Production-Shaped Manifests

Lesson: [0002-production-manifests.html](../../lessons/0002-production-manifests.html) · Time: 60–75 min

## Before you start

```bash
kubectl get nodes | grep -c Ready   # expect 2 (lab 01 cluster)
```

## Objectives

- Hand-write `k8s/lab2.yaml`: Namespace `llm`, ConfigMap, Deployment (probes + requests/limits), Service
- Break the readiness probe → watch the rollout stall safely → `rollout undo`
- Trigger `OOMKilled` on purpose and read it in `describe`

## Checkpoints — `./verify.sh` (run after step 2, before breaking things)

- [ ] Namespace `llm` exists
- [ ] Deployment `hello` in `llm`: 2/2 ready
- [ ] All three probes defined on the container
- [ ] Resources: requests AND limits set
- [ ] ConfigMap mounted — curl returns your custom HTML
- [ ] Later, by hand: `rollout undo` recovered the stalled rollout; `oom-demo` showed `OOMKilled`

## If stuck

| Symptom | Likely cause | Move |
|---|---|---|
| `error validating data` on apply | YAML indent | Check with `kubectl apply --dry-run=server -f k8s/lab2.yaml`; 2-space indent, no tabs |
| Pods `CreateContainerConfigError` | ConfigMap name mismatch | `describe pod` Events names the missing object |
| curl shows default nginx page | volumeMount path wrong | Must be `/usr/share/nginx/html` |
| Rollout doesn't stall when you break the probe | You broke liveness, not readiness | Patch path: `readinessProbe/httpGet/path` |
| `oom-demo` completes instead of OOM | Limit ≥ allocation | Limit 64Mi, stress 128M |

## Stretch (optional)

1. Add an `env` var sourced from the ConfigMap via `valueFrom.configMapKeyRef`.
2. Set requests == limits. Look up what QoS class the pod gets (`kubectl get pod -o jsonpath='{.status.qosClass}'`) and why it matters at eviction time.
3. Change ConfigMap HTML, `kubectl apply`, curl again — why is it stale? (Hint: mount propagation delay ~1 min; env vars never update.)

## Leave behind

Namespace `llm` stays (delete deployment/svc/configmap per lesson). Run `./verify.sh` before cleanup.
