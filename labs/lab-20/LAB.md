# Lab 20 — vLLM Atlas: the API Tour

Lesson: [0020-vllm-atlas.html](../../lessons/0020-vllm-atlas.html) · Time: ~2 h · **FINAL**

## Objectives

- Structured outputs enforced through YOUR router (schema respected even against a hostile prompt)
- Multimodal request to Qwen3.5-0.8B (image finally!) — or the documented error + needed version
- Sampling safari: determinism (seed), chaos (temp 1.8), logprobs, repetition penalty
- Offline batch: `LLM` class inside a K8s Job over a 20-prompt JSONL
- `--served-model-name` alias live in the UI picker
- `docs/vllm-api-tour.md` + `docs/vllm-gap-map.md`

## Steps (condensed — solution Job in `../solutions/k8s-advanced/offline-batch-job.yaml`)

```bash
# structured output through the router (schema in lesson Spotlight 1)
curl -s localhost:8080/v1/chat/completions -d @payloads/structured.json | python3 -m json.tool
# multimodal: image as base64 data URL
IMG=$(base64 -i some.png)
# → content: [{"type":"image_url","image_url":{"url":"data:image/png;base64,'$IMG'"}}, {"type":"text","text":"Describe this."}]
# sampling safari: same prompt, 4 configs, table the results
# offline batch:
kubectl apply -f k8s/offline-batch-job.yaml && kubectl logs -n llm -l job-name=offline-batch -f
# alias:
helm upgrade slm charts/slm-stack --set vllm.model.servedName=qwen-prod   # add to chart first
```

## Checkpoints — `./verify.sh`

- [ ] api-tour doc: structured-output result (incl. the hostile-prompt case)
- [ ] Multimodal: response OR documented failure + version/flag needed
- [ ] Sampling table ≥4 rows; seed determinism answered
- [ ] Offline batch Job succeeded; outputs in logs
- [ ] `/v1/models` shows the alias; UI picker shows it
- [ ] vllm-gap-map.md, honest

## If stuck

| Symptom | Move |
|---|---|
| `response_format` ignored/error | Guided-decoding backend not in your build — try `guided_json` extra-body form; else document version gap |
| Multimodal 400 | Arch may need `--limit-mm-per-prompt` or newer vLLM — the documented-error path is a PASS here |
| Offline Job OOM | CPU: max_model_len 2048, small batch; it's a 20-prompt demo, not a benchmark |
| Alias breaks UI | UI caches model list — restart the webui pod |

## Stretch

Tool calling end-to-end: `--enable-auto-tool-choice --tool-call-parser hermes` (check the right parser for Qwen), then a curl with one `tools` entry. Getting the parser flag right IS the exercise.

## After this lab

Course complete. Book: (1) the lesson-18 defense if not done, (2) the 2-week cold rebuild, (3) quarterly gap-map re-grade. Update MISSION.md — your teacher will ask.
