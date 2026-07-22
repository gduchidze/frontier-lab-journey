# Lab 04 — vLLM Meets Kubernetes

Lesson: [0004-vllm-on-k8s.html](../../lessons/0004-vllm-on-k8s.html) · Time: 60–90 min

## Before you start

```bash
docker image inspect vllm-cpu:local >/dev/null && echo "image OK"
kubectl get ns llm >/dev/null && echo "namespace OK"
```

## Objectives

- `kind load` the image into the cluster
- Write `k8s/vllm.yaml`: PVC (`hf-cache`), Deployment (probes tuned for model load, `/dev/shm` mount), Service (port **named** `http` — lab 07 depends on it)
- Chat through the cluster; prove PVC survives pod deletion

## Checkpoints — `./verify.sh`

- [ ] Image present on kind nodes
- [ ] PVC `hf-cache` Bound
- [ ] vLLM pod READY 1/1
- [ ] Startup probe with ≥10 min budget; service port named `http`
- [ ] `/dev/shm` Memory-backed mount present
- [ ] Chat completion works via Service
- [ ] Pod deletion → replacement Ready in a fraction of first-boot time (PVC hit)

## If stuck

| Symptom | Likely cause | Move |
|---|---|---|
| `ImagePullBackOff` | Forgot `kind load` or `imagePullPolicy` | Load with `--name llm-stack`; policy `IfNotPresent` |
| `Pending` | Requests too big for node | Lower CPU request; check `describe pod` Events |
| `CrashLoopBackOff` before Ready | No startup probe / threshold too low | `failureThreshold: 60`, `periodSeconds: 10` |
| `OOMKilled` mid-load | Memory limit tight | Limit 8Gi+, `VLLM_CPU_KVCACHE_SPACE=2` |
| Ready but curl times out | port-forward to wrong svc/port | `kubectl get svc -n llm`; forward `svc/vllm 8000:8000` |
| Second boot still slow | PVC not mounted at HF path | mountPath must be `/root/.cache/huggingface` |

## Stretch (optional)

1. `kubectl exec` into the pod: `du -sh /root/.cache/huggingface` — see the weights on the PVC.
2. Add an HF token as a Secret + `valueFrom.secretKeyRef` (pattern in [manifest anatomy](../../reference/k8s-manifest-anatomy.html)) — required for gated models later.
3. Kill the *node* the pod runs on (`docker stop llm-stack-worker`). What happens? Bring it back. (Single-replica availability lesson — cheap now, expensive in prod.)

## Leave behind

Everything: PVC, Deployment, Service. Lab 05 converts them into a chart.
