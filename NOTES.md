# Teacher Notes

## User preferences

- Caveman mode active in chat (terse). Lessons themselves: normal, clean prose.
- 1–2 hour sessions: each lesson = short knowledge block + substantial hands-on lab.
- Career-driven (ML infra engineer) → always tie concepts to "how this works at a real company".

## Environment facts (verified 2026-07-22)

- Apple M4, 16 GB RAM, 10 cores, macOS (Darwin 24.6)
- kubectl + docker CLI installed; Docker daemon was NOT running
- minikube/kind/helm/k3d NOT installed → lesson 1 installs kind + helm via brew
- No NVIDIA GPU → vLLM CPU backend only

## Risks / open questions

- **Qwen3.5-0.8B is `qwen3_5` arch, multimodal (image-text-to-text)**. Needs recent vLLM. CPU + ARM + new arch = 3 risk multipliers. Verify support in phase 3; fallback: `Qwen/Qwen3-0.6B` (text-only, well supported) — keep mission model as target.
- No official ARM CPU vLLM image → phase 3 likely builds from `docker/Dockerfile.cpu` (slow build, run in background) or runs vLLM via pip in a python container.
- 16 GB RAM: kind + vLLM CPU + Prometheus + Grafana + UI all at once is tight. Keep replicas=1 until phase 6; teach resource requests/limits early.

## Progress log

- 2026-07-22: Workspace scaffolded. Mission set. Lesson 0001 (K8s big picture + first cluster) created.
- 2026-07-22: FULL COURSE built — lessons 0001–0010 + index, 5 reference cards (kubectl, manifest anatomy, vLLM, Helm, observability), shared assets (course.css, quiz.js). User has NOT started labs yet — no learning records. Next session: check lesson-1 lab progress before anything else.
- Verified from doronmak repo: it runs CPU vLLM on kind too (`VLLM_TARGET_DEVICE=cpu`, `VLLM_CPU_KVCACHE_SPACE=5`, image `doronmak/vllm-cpu-image`) — validates our whole local-CPU approach.
- Router lesson (0006) uses image `lmcache/lmstack-router:latest` + flags from production-stack README — VERIFY tag/flags against router README at lab time; they drift.
- kube-prometheus-stack release name assumed `kps` in lessons 7/10 port-forward commands.
- 2026-07-22 (later): `labs/` layer added — lab-01…10 worksheets + verify.sh graders + solutions (all manifests, full chart, k6 script). All bash/YAML/JS syntax-verified.
- 2026-07-22 (later): ADVANCED TRACK added — lessons 0011–0018 (scheduling/GPU fleet, edge+TLS, security/tenancy, GitOps, vLLM perf, distributed/disagg, SRE, cost+capstone) + labs 11–18 + solutions/k8s-advanced/. Lesson 11 REBUILDS the cluster (kind-advanced.yaml: 3 nodes, Cilium, ports 80/443/30080) — base-track leftovers get recreated there. Labs 15/16/18 produce docs/ artifacts the lab-18 capstone cross-references.
- Advanced drift risks: ingress-nginx kind manifest URL, cert-manager/cilium/argo chart versions, vllm bench flags, burn-rate expr metric names — verify at lab time.
- 2026-07-22 (final): ATLAS lessons 0019 (K8s: everything not covered — Jobs/Kueue/LWS/StatefulSet/PDB+drain/operators/DRA/Kustomize/mesh) + 0020 (vLLM: structured outputs/tool calling/multimodal/multi-LoRA/offline batch/fast loading/ecosystem) + labs 19–20 + solutions (batch-job, modelendpoint-crd, offline-batch-job). Course now 20 lessons, 20 labs. Gap-map docs (k8s-gap-map.md, vllm-gap-map.md) = user's permanent revision syllabus — re-grade quarterly.
- User has a `system-design/NOTES.md` open in IDE — separate folder, not created by the course; ask about it sometime.
