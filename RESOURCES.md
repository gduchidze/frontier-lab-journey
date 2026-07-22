# Resources

High-trust sources grounding this course. Prefer these over memory.

## Primary (reference implementations)

| Resource | What it gives | Trust |
|----------|---------------|-------|
| [vllm-project/production-stack](https://github.com/vllm-project/production-stack) | Official reference stack: Helm chart, request router, Prometheus+Grafana observability, tutorials 00–06 | High (official vLLM project) |
| [production-stack tutorials](https://github.com/vllm-project/production-stack/tree/main/tutorials) | Step-by-step: install K8s env, minimal helm install, vLLM config, model from PV, multi-model, KV offload | High |
| [doronmak/VLLM-Kubernetes-Deployment](https://github.com/doronmak/VLLM-Kubernetes-Deployment) | Compact demo: `k8s/kind-config.yaml`, Helm chart `charts/vllm-demo` (vllm + dashboard + ingress + PVC), k6 + guidellm load tests, metrics dashboard | Medium (personal demo, good structure) |

## Official docs

| Resource | Use for |
|----------|---------|
| [Kubernetes docs — Concepts](https://kubernetes.io/docs/concepts/) | Pods, Deployments, Services, probes — canonical definitions |
| [kind quickstart](https://kind.sigs.k8s.io/docs/user/quick-start/) | Local cluster setup, port mappings, multi-node |
| [vLLM docs](https://docs.vllm.ai/) | Engine args, OpenAI server, metrics |
| [vLLM CPU installation](https://docs.vllm.ai/en/latest/getting_started/installation/cpu.html) | ARM/CPU backend build — critical for Mac M4 |
| [production-stack docs](https://docs.vllm.ai/projects/production-stack) | Router, helm values, observability |
| [Helm docs](https://helm.sh/docs/) | Chart structure, values, templating |
| [Prometheus docs](https://prometheus.io/docs/introduction/overview/) | Scraping, PromQL |
| [Grafana docs](https://grafana.com/docs/grafana/latest/) | Dashboards, panels |
| [Qwen3.5-0.8B model card](https://huggingface.co/Qwen/Qwen3.5-0.8B) | Chat template, context length, multimodal usage |

## Communities (wisdom)

| Community | Why |
|-----------|-----|
| [vLLM developers Slack](https://communityinviter.com/apps/vllm-dev/join-vllm-developers-slack) | production-stack channel; bi-weekly community meetings (Tuesdays 5:30 PM PT) |
| [Kubernetes Slack](https://slack.k8s.io/) | #kind channel, #kubernetes-novice |
| r/kubernetes, r/LocalLLaMA | Real-world war stories, local inference practice |

## Local skills available in this workspace

- `vllm-deploy-k8s` — deploy templates + troubleshooting runbook
- `vllm-deploy-simple`, `vllm-deploy-docker` — engine-only deploys
- `vllm-bench-serve`, `vllm-bench-random-synthetic`, `vllm-prefix-cache-bench` — benchmarking (phase 9)
