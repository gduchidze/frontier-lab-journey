# Labs

One directory per lesson. Each contains:

- **`LAB.md`** — worksheet: prerequisite check, objectives, checkpoints, troubleshooting table, stretch goals
- **`verify.sh`** — automated grader. Run it any time; it prints ✅/❌ per checkpoint. Run it **before** the lesson's cleanup step.

Steps live in the lesson HTML (`../lessons/`); the worksheet is your companion while doing them.

## Rules of engagement

1. **Type the YAML yourself.** Copy-paste teaches your clipboard, not you.
2. **`solutions/` is a last resort.** Try → break → `describe`/`logs` → ask the teacher agent → only then peek. Diff your attempt against the solution when you do — the diff is the lesson.
3. **Green verify ≠ done.** Done = you can explain every ❌→✅ transition you went through.
4. **After each lab**: tell the teacher agent what you did and what surprised you → it writes your learning record and calibrates the next session.

## Lab index

| Lab | Verify proves | State left behind (needed later) |
|-----|---------------|----------------------------------|
| 01 | Cluster up, Deployment self-heals, Service routes | kind cluster `llm-stack` |
| 02 | Hand-written manifests with probes/limits work | namespace `llm` |
| 03 | CPU vLLM image serves OpenAI API locally | image `vllm-cpu:local`, volume `hf-cache` |
| 04 | Engine runs in-cluster with PVC + probes | vLLM Deployment/Service in `llm` |
| 05 | Own Helm chart owns the stack | release `slm` |
| 06 | 2 engines behind discovering router | router + 2 replicas |
| 07 | Prometheus scrapes, Grafana graphs | `monitoring` namespace stack |
| 08 | Browser chat end-to-end | Open WebUI in `ui` |
| 09 | Saturation curve measured, SLO gate runs | `load_tests/` results |
| 10 | HPA closes the loop | full production stack |

### Advanced track (senior productization)

| Lab | Verify proves | Key artifact |
|-----|---------------|--------------|
| 11 | Cilium cluster + simulated GPU pool scheduling | rebuild-time log |
| 12 | Hostname + TLS edge, streaming annotations | the buffering demo story |
| 13 | Default-deny netpol, quotas, engine auth | attacker-blocked screenshot, `docs/rbac-audit.md` |
| 14 | Argo CD synced, selfHeal, git-driven rollback | `docs/model-rollout.md` |
| 15 | Tuning study artifacts | `docs/tuning-report.md` |
| 16 | Distributed design doc complete | `docs/distributed-design.md` |
| 17 | Alerts fired, runbooks, chaos day | `docs/chaos-day.md`, postmortem |
| 18 | Capstone: cost model + platform design | `docs/platform-design.md` |

### Final track (the atlases)

| Lab | Verify proves | Key artifact |
|-----|---------------|--------------|
| 19 | Batch Job 6/6, graceful drain, PDB, toy CRD live | `docs/k8s-gap-map.md` |
| 20 | Structured outputs, sampling safari, offline-batch Job, alias | `docs/vllm-api-tour.md`, `docs/vllm-gap-map.md` |

## Solutions layout

```
solutions/
├── k8s/            kind-config, lab2, vllm, servicemonitor, router, webui, hpa
├── k8s-advanced/   kind-advanced, fake-gpu.sh, gpu-workload, netpol, quota,
│                   ingress, cluster-issuer, argocd-app, alerts
├── charts/         slm-stack/ (complete chart)
└── load_tests/     chat.js
```
