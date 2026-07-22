# Lab 03 — The Engine: vLLM in Docker

Lesson: [0003-vllm-engine-docker.html](../../lessons/0003-vllm-engine-docker.html) · Time: ~2 h (30–60 min is a background build)

## Before you start

```bash
docker info --format 'CPUs {{.NCPU}} Mem {{.MemTotal}}'   # want ≥8 CPUs, ≥10 GB for the build
df -h / | tail -1                                          # want ≥25 GB free disk
```

## Objectives

- Build `vllm-cpu:local` (ARM) from vLLM's `docker/Dockerfile.cpu` — **start first, read while it builds**
- Serve `Qwen/Qwen3.5-0.8B` (fallback `Qwen/Qwen3-0.6B` if arch unsupported — record which!)
- Hit `/v1/models`, `/v1/chat/completions`, `/metrics`
- Observe `num_requests_running > 1` under concurrent load

## Checkpoints — `./verify.sh` (with the container running)

- [ ] Image `vllm-cpu:local` exists, arch arm64
- [ ] Container serving: `/health` → 200
- [ ] `/v1/models` lists your model
- [ ] Chat completion returns content
- [ ] `/metrics` exposes `vllm:` series
- [ ] HF cache volume populated (no re-download on restart)

## If stuck

| Symptom | Likely cause | Move |
|---|---|---|
| Build dies OOM (`g++: killed`) | Docker RAM too low | Docker Desktop → Resources → 10–12 GB, rebuild (cache resumes) |
| Build error mid-layer | Upstream main broke | `git checkout` latest release tag (`git tag --sort=-v:refname \| head -3`), rebuild |
| `ValueError: ... architecture not supported` | qwen3_5 too new for checkout | Fallback `--model Qwen/Qwen3-0.6B`; note in learning record |
| Engine killed during load | Container memory | `docker run -m 10g …`; drop `VLLM_CPU_KVCACHE_SPACE` to 2 |
| Slow first tokens, then fine | Warmup/compile | Normal; use `--enforce-eager` to trade steady-state speed for startup |
| Download crawls | HF rate limit | `-e HF_TOKEN=$HF_TOKEN` (free account token) |

## Stretch (optional)

1. `"stream": true` with `curl -sN` — watch SSE chunks arrive token by token. This is what the UI consumes in lab 08.
2. Time 1 request with `max_tokens: 100`, then 4 concurrent — is total wall time 4×? Why not? (That's continuous batching, measured.)
3. Restart with `--enable-prefix-caching`, send the same long prompt twice, compare TTFT in logs.

## Leave behind

Image `vllm-cpu:local` + volume `hf-cache` — labs 04+ depend on both. Stop/remove only the container.
