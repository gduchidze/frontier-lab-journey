# Lab 01 — Your First Cluster

Lesson: [0001-first-cluster.html](../../lessons/0001-first-cluster.html) · Time: 45–60 min

## Before you start

```bash
docker info >/dev/null 2>&1 && echo "docker OK" || echo "START DOCKER DESKTOP FIRST"
```

## Objectives

- 2-node kind cluster named `llm-stack` (config in `k8s/kind-config.yaml`)
- nginx Deployment with 2 replicas; watch a deleted Pod resurrect
- Service exposing it; curl through a port-forward

## Checkpoints — `./verify.sh` (run BEFORE the cleanup step)

- [ ] kind cluster `llm-stack` exists
- [ ] 2 nodes, both `Ready`
- [ ] Deployment `hello` has 2/2 available
- [ ] Service `hello` has ≥1 endpoint
- [ ] You watched a Pod get deleted and replaced (verify can't see this — be honest)

## If stuck

| Symptom | Likely cause | Move |
|---|---|---|
| `kind create` hangs at "Starting control-plane" | Docker low on RAM | Docker Desktop → Resources → 8 GB+, retry |
| Nodes `NotReady` | CNI still starting | Wait 60s, `kubectl get nodes` again |
| `curl localhost:8080` refused | port-forward not running / wrong terminal | Re-run port-forward, keep that terminal open |
| Pods `Pending` | Worker missing | `kubectl get nodes` — did the config have 2 node entries? |

## Stretch (optional)

1. `kubectl scale deployment hello --replicas=5` — where do the pods land? Why that spread?
2. `kubectl get pod POD -o yaml` — find 3 fields you didn't declare. Who added them?
3. Delete the *Deployment* (not a pod). Why does nothing resurrect it?

## Leave behind

Cluster stays. Delete only the `hello` Deployment/Service (lesson step 6) — but run `./verify.sh` first.
