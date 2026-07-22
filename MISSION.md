# Mission

## Why

Giorgi wants to become an **ML Infrastructure Engineer**. The goal is employable, production-grade skill: how real companies serve LLMs — Kubernetes, vLLM, request routing, observability, load testing, autoscaling.

## The Project (capstone)

Build a **full SLM inference production stack, running locally**, modeled on real reference implementations:

- **Model**: [Qwen/Qwen3.5-0.8B](https://huggingface.co/Qwen/Qwen3.5-0.8B) (0.8B, multimodal, apache-2.0, ungated)
- **Engine**: vLLM (CPU backend — Mac M4, no NVIDIA GPU)
- **Orchestration**: Kubernetes via `kind` on Docker Desktop
- **Packaging**: Helm charts
- **Routing**: vLLM production-stack request router patterns
- **Monitoring**: Prometheus + Grafana (TTFT, latency distribution, pending requests, KV cache usage)
- **UI**: chat frontend (Open WebUI) against the OpenAI-compatible API
- **Load testing**: k6 / `vllm bench serve`

Reference repos:
- [vllm-project/production-stack](https://github.com/vllm-project/production-stack) — official reference architecture
- [doronmak/VLLM-Kubernetes-Deployment](https://github.com/doronmak/VLLM-Kubernetes-Deployment) — compact kind + Helm + dashboard + load-test demo

## Constraints

- Hardware: Apple M4, 16 GB RAM, 10 cores, **no NVIDIA GPU** → vLLM CPU backend, small model only
- Session length: **1–2 hours** (lesson + hands-on lab each session)
- Everything free / local

## Roadmap (phases)

| # | Phase | Win |
|---|-------|-----|
| 1 | K8s core: cluster, Pods, Deployments, Services (kind) | First app running in own cluster |
| 2 | K8s config: namespaces, ConfigMaps, Secrets, probes, resources | Production-shaped manifest |
| 3 | vLLM solo in Docker: engine, OpenAI API, CPU backend | Chat with Qwen3.5 via curl |
| 4 | vLLM on K8s: Deployment + Service + model cache PVC + probes | Inference served by the cluster |
| 5 | Helm: package the stack (study doronmak chart) | `helm install` own chart |
| 6 | production-stack: router, multi-replica, session routing | Distributed serving |
| 7 | Observability: Prometheus + Grafana, vLLM metrics | Live dashboard of TTFT/latency |
| 8 | UI: Open WebUI on top of the stack | Full user-facing product |
| 9 | Load testing: k6, vllm bench serve | Numbers: throughput, TTFT, TPOT |
| 10 | Autoscaling (HPA) + capstone writeup | Portfolio-ready project |

## Success Criteria

- Can explain and rebuild the whole stack from scratch, unaided
- Grafana dashboard shows real inference metrics under load
- Repo is portfolio-quality: README, architecture diagram, benchmark results
