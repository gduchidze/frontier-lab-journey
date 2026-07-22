# The Frontier-Lab Engineer Journey

This repo is a single, deliberate journey: becoming an AI engineer at the caliber hired by **Anthropic, OpenAI, and DeepMind** — built in public, as working systems and graded curricula rather than a reading list.

Three pillars, three workspaces:

| Pillar | Workspace | What it builds |
|---|---|---|
| **AI Infrastructure** | repo root (`lessons/`, `labs/`, `reference/`) | A production-style SLM inference platform on Kubernetes + vLLM, via a 20-lesson hands-on course — cluster to capstone design doc |
| **System Design** | [`system-design/`](system-design/) | Frontier-lab design rounds ("inference batching service @ 100k RPS"): CS/ML foundations → estimation → distributed systems → AI-infra design, spine project = designing the very platform the infra pillar runs |
| **Behavioral & Culture** | [`behaviour/`](behaviour/) | The rounds where most candidates actually fail: true-story bank mapped to competencies, values reasoning under pressure, lab-specific culture literacy |

Each workspace is a self-contained teaching environment: HTML lessons with labs and retrieval quizzes, reference cheat-sheets, and learning records. The pillars feed each other — the infra stack built here is the system the design pillar whiteboards, and both become the stories the behavioral pillar mines.

---

## Pillar 1 — AI Infrastructure: SLM Inference Production Stack

A production-style **small language model inference platform** built entirely on a laptop. Modeled on [vLLM production-stack](https://github.com/vllm-project/production-stack), serving [Qwen/Qwen3.5-0.8B](https://huggingface.co/Qwen/Qwen3.5-0.8B) on a CPU backend.

```
Browser ──► NodePort/Ingress ──► Open WebUI ──► Request Router ──► vLLM engines × N
                                                     │                  ▲
                              Prometheus ◄── scrapes ┘        HPA ──────┘
                                  │
                               Grafana (TTFT, queue depth, KV cache, tok/s)
```

Runs locally: [kind](https://kind.sigs.k8s.io/) cluster on Docker, vLLM CPU backend (Apple Silicon), no GPU required. The architecture is identical to a GPU deployment — only the image and one resource line differ.

### The stack

| Layer | Tech |
|---|---|
| Inference engine | vLLM (CPU build, OpenAI-compatible API) |
| Orchestration | Kubernetes via kind (Cilium CNI in the advanced setup) |
| Packaging | Helm chart — model, resources, probes, KV cache as values |
| Routing | production-stack router: K8s service discovery, session affinity |
| Observability | kube-prometheus-stack, ServiceMonitor, vLLM metrics dashboards |
| Edge | ingress-nginx + cert-manager TLS, LLM-tuned (streaming, timeouts) |
| Security | Default-deny NetworkPolicy, quotas, RBAC, engine API keys |
| Delivery | Argo CD GitOps + model rollout strategy |
| UI | Open WebUI against the router's OpenAI API |
| Load testing | k6 SLO gates + `vllm bench serve` saturation curves |
| Autoscaling | HPA (+ KEDA-on-queue-depth design) |

### The course (20 lessons, graded labs)

Open `lessons/index.html`. Each lesson: theory → hands-on lab → retrieval quiz → primary source. Each lab has an automated grader (`labs/lab-NN/verify.sh`).

| Track | Lessons | Covers |
|---|---|---|
| **Base** | 01–10 | K8s core → manifests/probes → vLLM engine → deploy → Helm → router/scale-out → Prometheus/Grafana → UI → load testing → HPA + capstone |
| **Advanced** | 11–18 | GPU-fleet scheduling → Ingress/TLS edge → NetworkPolicy/tenancy → GitOps → vLLM perf engineering (quantization, chunked prefill, spec decode) → distributed/disaggregated inference → SRE (SLOs, burn-rate alerts, chaos) → cost & capacity + design-doc capstone |
| **Atlas** | 19–20 | Everything else: K8s (Jobs, LWS, Kueue, operators, DRA, PDB/drain…) and vLLM (structured outputs, multi-LoRA, multimodal, offline batch, ecosystem…) |

### Quickstart

Prereqs: Docker Desktop (≥8 GB RAM), `kubectl`, `kind`, `helm`.

```bash
# 1. Cluster
kind create cluster --config labs/solutions/k8s/kind-config.yaml

# 2. Engine image (30–60 min build, once)
git clone https://github.com/vllm-project/vllm.git && cd vllm
docker build -f docker/Dockerfile.cpu -t vllm-cpu:local .
kind load docker-image vllm-cpu:local --name llm-stack

# 3. The stack
helm install slm labs/solutions/charts/slm-stack
kubectl apply -f labs/solutions/k8s/router.yaml
kubectl apply -f labs/solutions/k8s/webui.yaml

# 4. Wait for the engine (first boot downloads + loads the model)
kubectl get pods -n llm -w

# 5. Chat: http://localhost:30080   — or via API:
kubectl port-forward -n llm svc/vllm-router 8080:80
curl -s localhost:8080/v1/chat/completions -H "Content-Type: application/json" \
  -d '{"model":"Qwen/Qwen3.5-0.8B","messages":[{"role":"user","content":"Hello!"}],"max_tokens":50}'
```

### Design decisions & limitations

- **CPU backend, deliberately.** A 0.8B model on CPU exercises every production pattern; GPU migration is a documented one-line swap (lessons 11, 15–16).
- **NodePort + local CA** are the honest local stand-ins for LoadBalancer/ACME; the manifests mark where production differs.
- **CPU-based HPA is the mechanism demo**; the production answer (KEDA on `vllm:num_requests_waiting`) is designed in lessons 10/17.
- **`WEBUI_AUTH=False` is local-only** — auth, TLS, rate limiting get wired at the edge in lessons 12–13 before anything is exposed.
- Benchmark results and tuning reports accumulate in `load_tests/` and `docs/` as labs complete.

---

## Pillar 2 — System Design (`system-design/`)

From weak fundamentals to whiteboarding frontier-lab prompts cold. Diagnostic-gated foundations (data structures, OS, concurrency, networking, ML/DL/transformer anatomy) feed into estimation drills, distributed-systems building blocks, classic designs (rate limiter, news feed, distributed search), and AI-infra designs (inference batching service, RAG at scale, training-data pipelines). Spine project: designing the LLM inference platform that Pillar 1 actually runs. Grounded in DDIA, System Design Primer, Chip Huyen, CS336, and the vLLM internals literature.

## Pillar 3 — Behavioral & Culture (`behaviour/`)

Story mining (true, specific, bullet-outlined — never scripts), a story-bank matrix mapping each story to competencies, question banks from the three labs' reported loops, and values-reasoning practice for the rounds that reject rehearsed answers — Anthropic's 45-minute culture interview foremost.

---

## Method

The same learning system runs in every workspace: **missions** ground each pillar in the real goal, **lessons** stay inside the zone of proximal development, **labs** create tight feedback loops (automated graders where possible), **retrieval quizzes** build storage strength over fluency, **learning records** capture what actually happened, and **gap maps** get re-graded quarterly. Mock interviews close each pillar.

## Reference

- [vllm-project/production-stack](https://github.com/vllm-project/production-stack) · [doronmak/VLLM-Kubernetes-Deployment](https://github.com/doronmak/VLLM-Kubernetes-Deployment)
- [vLLM docs](https://docs.vllm.ai/) · [Kubernetes docs](https://kubernetes.io/docs/) · [Helm docs](https://helm.sh/docs/)

## License

Apache-2.0 (model: Qwen3.5-0.8B, Apache-2.0).
