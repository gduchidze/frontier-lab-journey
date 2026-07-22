# Lab 19 — K8s Atlas: Jobs, Drains, Debug, CRDs

Lesson: [0019-k8s-atlas.html](../../lessons/0019-k8s-atlas.html) · Time: ~2 h · **FINAL TRACK**

## Objectives

- Batch inference as an Indexed Job (parallelism 2, completions 6) against the router
- Graceful drain: preStop + 300s grace + PDB on engines, then a real `kubectl drain` under load
- `kubectl debug` into a running engine pod
- Toy `ModelEndpoint` CRD applied + queried
- `docs/k8s-gap-map.md` — honest three-state self-grade of every atlas row

## Steps (condensed — solutions in `../solutions/k8s-advanced/batch-job.yaml`, `modelendpoint-crd.yaml`)

```bash
kubectl apply -f k8s/batch-job.yaml && kubectl get jobs -n llm -w
kubectl logs -n llm -l job-name=batch-eval --tail=20
# chart: add lifecycle.preStop sleep 15, terminationGracePeriodSeconds 300, PDB minAvailable 1
helm upgrade slm charts/slm-stack
kubectl drain llm-stack-worker --ignore-daemonsets --delete-emptydir-data   # under k6 load!
kubectl uncordon llm-stack-worker
kubectl debug -it $(kubectl get pod -n llm -l app=vllm -o name | head -1) -n llm --image=busybox --target=vllm
kubectl apply -f k8s/modelendpoint-crd.yaml && kubectl get modelendpoints
```

## Checkpoints — `./verify.sh`

- [ ] Job succeeded: 6 completions
- [ ] Engine deployment has preStop + grace ≥300s; PDB present
- [ ] Drain survived: engines Ready again after uncordon (note user impact you saw)
- [ ] CRD registered; ≥1 ModelEndpoint object exists
- [ ] Gap map with all three grades used honestly (something must be "need study")

## If stuck

| Symptom | Move |
|---|---|
| Job pods CrashLoop | Router DNS/API key — same debugging as lab 08's exec-curl |
| Drain hangs forever | PDB minAvailable=1 with 1 replica = undrainable (correct behavior!) — scale to 2 first. Understand WHY |
| debug: `--target` rejected | Older kubectl — drop `--target` (loses process namespace sharing, still useful) |
| CRD applies, CR rejected | Schema mismatch — read the error, it names the bad field. That's the CRD teaching |

## Stretch

Kyverno: one policy — "every pod in llm MUST have resource limits". Try to deploy a violator.
