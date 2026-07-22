# Lab 11 — Advanced Cluster + Simulated GPU Fleet

Lesson: [0011-advanced-scheduling.html](../../lessons/0011-advanced-scheduling.html) · Time: ~2 h · **ADVANCED**

## Objectives

- Rebuild: 3-node cluster from `k8s/kind-advanced.yaml` (Cilium CNI, ports 80/443/30080) — time yourself
- Redeploy the full stack from your chart (reproducibility exam)
- Fake GPU pool: label + taint worker2, advertise `example.com/gpu: 2` via status PATCH
- Scheduling drills: toleration+affinity placement, `Insufficient` Pending, preemption, topology spread

## Steps (condensed — solution files in `../solutions/k8s-advanced/`)

```bash
kind delete cluster --name llm-stack
kind create cluster --config k8s/kind-advanced.yaml
# Cilium (CNI is disabled in the config — nodes stay NotReady until this):
helm repo add cilium https://helm.cilium.io && helm repo update
helm install cilium cilium/cilium -n kube-system
kubectl get nodes -w                      # all 3 → Ready
# redeploy stack: kind load image → helm install slm → router → webui → monitoring
# fake GPU node:
kubectl label node llm-stack-worker2 gpu=true
kubectl taint node llm-stack-worker2 gpu=true:NoSchedule
kubectl proxy &   # then PATCH status (see solutions/k8s-advanced/fake-gpu.sh)
```

Then: deploy `gpu-workload.yaml` (3 replicas requesting `example.com/gpu: 1`) → 2 placed, 1 Pending. PriorityClasses + preemption demo. Add `topologySpreadConstraints` to your chart.

## Checkpoints — `./verify.sh`

- [ ] 3 nodes Ready, Cilium running
- [ ] Full stack redeployed (engines, router, UI, monitoring)
- [ ] worker2 tainted + advertising `example.com/gpu`
- [ ] 2 "GPU" pods on worker2, 1 Pending with `Insufficient example.com/gpu`
- [ ] PriorityClasses exist; preemption witnessed (Events)
- [ ] vLLM replicas spread across workers

## If stuck

| Symptom | Move |
|---|---|
| Nodes NotReady forever | Cilium not installed / still starting — `kubectl get pods -n kube-system` |
| PATCH rejected | Must hit `/status` subresource via proxy with `application/json-patch+json` — use the solution script |
| Fake GPU vanished | Kubelet restarts wipe status patches — re-run the script |
| GPU pods on worker1 | Affinity missing — taint only repels, affinity attracts |

## Stretch

Karpenter reading (30 min): how would scale-to-zero interact with your taints? Note in NOTES.md.
