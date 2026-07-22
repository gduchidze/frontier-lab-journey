# Lab 16 — Distributed Inference: Capacity Math + Design Doc

Lesson: [0016-distributed-inference.html](../../lessons/0016-distributed-inference.html) · Time: ~2 h · **ADVANCED** (paper lab)

## Objectives

`docs/distributed-design.md` containing: three sizing problems solved with shown arithmetic, a mapping of production-stack's KV-offload tutorial to concepts, and a defended P/D-vs-DP architecture choice.

## The three sizing problems (show your work)

1. **Llama-3.1-70B bf16 on H100-80GB**: weights GB? min TP for weights alone? KV/token (~320 KB) × 8k ctx × 32 concurrent = ? → final TP and the binding constraint.
2. **Same, fp8 weights + fp8 KV**: recompute both. What's now binding? What did quantization actually buy — capacity or hardware count?
3. **405B bf16 across 8×H100 nodes**: TP×PP layout; where do bubbles bite; why not TP=16 across nodes?

## Then

- Read production-stack [tutorial 05 (KV offload / LMCache)](https://github.com/vllm-project/production-stack/blob/main/tutorials/05-offload-kv-cache.md); map each config block to a lesson concept in the doc.
- Final section: the 30k-user P/D vs monolithic-DP decision from the lesson — pick, justify, blast radii, "metrics that would prove me wrong".
- Book the defense: teacher attacks the doc; revise once.

## Checkpoints — `./verify.sh`

- [ ] Doc exists with all three problems and visible arithmetic
- [ ] fp8 section identifies the NEW binding constraint
- [ ] TP/PP/DP/EP each appear (you can't design with words you don't use)
- [ ] Architecture choice section with failure/blast-radius analysis
- [ ] By hand: survived the teacher's attack; doc revised

## If stuck

| Symptom | Move |
|---|---|
| KV math feels hand-wavy | Params: layers=80, kv_heads=8, head_dim=128 for 70B; 2 bytes bf16, ×2 for K and V |
| Can't choose P/D vs DP | Wrong frame — list what each optimizes, then which the SCENARIO rewards. The scenario decides, not the tech |
| Doc balloons past 3 pages | Senior docs compress. Tables + arithmetic, adjectives out |

## Stretch (optional, costs money)

1 hr on 2×A10 (RunPod/Lambda): real `--tensor-parallel-size 2`, compare tok/s vs single GPU. Ask teacher to plan the session first.
