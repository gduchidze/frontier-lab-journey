# Lab 15 — The Tuning Study

Lesson: [0015-vllm-performance.html](../../lessons/0015-vllm-performance.html) · Time: ~2.5 h · **ADVANCED**

## Objectives

Run a disciplined tuning study on your CPU stack (one knob per run, fixed workload) and publish `docs/tuning-report.md`. Method > numbers.

## Protocol

Fixed workload for every run: 128 in / 64 out, `--request-rate 0.5`, `--num-prompts 30`, single engine.

| Run | Change (ONE) | Record |
|---|---|---|
| 0 | baseline | TTFT P50/P90, TPOT, tok/s, waiting-queue peak |
| 1–3 | `--max-num-seqs` 4 / 8 / 16 | same |
| 4 | `--enable-prefix-caching` + shared-prefix workload (400-token system prompt) | TTFT dist vs run 0-with-prefixes |
| 5 | `--max-model-len 2048`, high concurrency | admission behavior |

Prefix run: use the `vllm-prefix-cache-bench` skill for the harness. Save every bench JSON into `load_tests/tuning/`.

## Checkpoints — `./verify.sh`

- [ ] ≥5 bench JSONs in `load_tests/tuning/`
- [ ] `docs/tuning-report.md`: workload spec, run table (≥5 rows), ≥3 conclusions
- [ ] Report has a "on H100s I would…" section (FP8, kv fp8, spec decode — with predicted effects)
- [ ] By hand: you can state the max-num-seqs throughput/TPOT trade from YOUR numbers

## If stuck

| Symptom | Move |
|---|---|
| Runs not comparable | Something else changed (replicas? Docker load?) — kill noise, rerun |
| Prefix caching shows nothing | Workload must actually share prefixes; the system prompt must exceed the block size |
| Bench flag rejected | Flags drift — `vllm bench serve --help` in the container is truth |
| Numbers noisy run-to-run | 30 prompts is small; do 2 trials, report both — honesty beats precision |

## Stretch

Add `vllm:kv_cache_usage_perc` peak (from Prometheus) as a column — correlate cache pressure with the TPOT cliff.
