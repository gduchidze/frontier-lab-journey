# Lab 14 — GitOps: the Cluster Follows Git

Lesson: [0014-gitops-delivery.html](../../lessons/0014-gitops-delivery.html) · Time: ~2 h · **ADVANCED**

## Prereq

Repo pushed to GitHub (public, or private + repo credentials in Argo).

## Objectives

- Argo CD installed; Application tracking `charts/slm-stack` with automated sync + selfHeal
- One deploy via commit, one rollback via `git revert` — zero kubectl
- selfHeal vs manual drift experienced; HPA collision understood (`ignoreDifferences`)
- `docs/model-rollout.md` canary design written

## Steps (condensed — solution in `../solutions/k8s-advanced/argocd-app.yaml`)

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d
kubectl port-forward svc/argocd-server -n argocd 8443:443   # UI: https://localhost:8443
# edit argocd-app.yaml: YOUR repo URL → apply → watch it adopt release 'slm'
# deploy-by-commit: change values.yaml → push → watch sync
# drift: kubectl scale deployment vllm -n llm --replicas=3 → watch Argo revert
```

## Checkpoints — `./verify.sh`

- [ ] Argo CD Running; Application exists, Synced + Healthy
- [ ] Auto-sync + selfHeal + prune enabled
- [ ] Git log shows a config-change commit AND a revert commit
- [ ] `docs/model-rollout.md` exists with weights/metrics/abort criteria
- [ ] By hand: you watched selfHeal stomp your manual scale — explain to teacher when that's wrong

## If stuck

| Symptom | Move |
|---|---|
| App stuck `Unknown` | Repo URL/branch typo, or private repo without credentials |
| `OutOfSync` loops forever | Mutating webhook or HPA fighting a tracked field — `ignoreDifferences` on `/spec/replicas` |
| Sync fails on PVC | Immutable field diff — PVCs can't be resized/renamed by sync; keep them out or annotate keep |
| Adoption deleted resources | `prune: true` + resources not in chart = pruned. Everything must live in git — that's the deal |

## Stretch

App-of-apps: root Application spawning slm-stack + monitoring + edge as children. Your whole platform, one tree, one git URL.
