# Lab 05 — Helm: Package the Stack

Lesson: [0005-helm-package.html](../../lessons/0005-helm-package.html) · Time: 60–90 min

## Before you start

```bash
helm version --short && kubectl get deploy vllm -n llm >/dev/null && echo "ready"
```

## Objectives

- Chart `charts/slm-stack`: your `values.yaml` + templates for Deployment/Service/PVC
- Replace the raw-YAML deploy with release `slm`
- One `upgrade --set`, one `rollback`, read `helm history`

## Checkpoints — `./verify.sh`

- [ ] `helm lint` clean
- [ ] `helm template` renders your values (model name, kv space, port name `http`)
- [ ] Release `slm` deployed; vLLM Ready under Helm management
- [ ] History shows ≥3 revisions (install, upgrade, rollback)

## If stuck

| Symptom | Likely cause | Move |
|---|---|---|
| `error converting YAML` at install | Template renders bad indent | `helm template … \| less` — find the mangled block; fix `nindent` count |
| Value renders empty | Path typo (`.Values.vllm.modle…`) | `helm template --debug` shows unresolved paths |
| `resources:` block empty in output | Missing `toYaml` | `{{- toYaml .Values.vllm.resources | nindent 10 }}` |
| Install rejected: PVC exists | Old raw-YAML PVC ownerless | Either `kubectl delete pvc hf-cache -n llm` (weights re-download) or add Helm adoption annotations — ask teacher |
| Pod re-downloads weights after switch | New PVC name ≠ `hf-cache` | Keep the claim name identical to lab 04 |

## Stretch (optional)

1. Add `dashboard.enabled`-style flag: wrap the Service in `{{- if .Values.vllm.service.enabled }}`. Test both values.
2. Add a `NOTES.txt` template that prints the port-forward command after install (doronmak's chart does this).
3. `helm package charts/slm-stack` — you now have a distributable `.tgz`, same artifact form as `helm repo add vllm` pulls.

## Leave behind

Release `slm` running. `k8s/vllm.yaml` is now retired (keep for diffing).
