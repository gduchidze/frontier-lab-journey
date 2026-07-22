# Lab 08 — The UI: Open WebUI

Lesson: [0008-ui-openwebui.html](../../lessons/0008-ui-openwebui.html) · Time: 60–75 min

## Before you start

```bash
kubectl get svc vllm-router -n llm && echo "router OK"
```

## Objectives

- `k8s/webui.yaml`: namespace `ui`, PVC, Deployment (env → router DNS), NodePort Service on 30080
- Chat at `http://localhost:30080` — no port-forward (trace WHY, hop by hop, out loud)
- Kill-an-engine resilience demo mid-conversation

## Checkpoints — `./verify.sh`

- [ ] open-webui pod Ready in `ui`
- [ ] Service type NodePort, nodePort 30080
- [ ] `OPENAI_API_BASE_URL` points at router's cluster DNS
- [ ] `curl localhost:30080` returns the app
- [ ] UI can reach the router from inside the cluster
- [ ] By hand: model picker shows your Qwen; conversation survives engine kill

## If stuck

| Symptom | Likely cause | Move |
|---|---|---|
| localhost:30080 refused | kind port mapping missing | `docker port llm-stack-control-plane` — no 30080? Your lesson-1 config lacked it; recreate cluster (ask teacher for the cheap path first) |
| UI loads, no models in picker | Base URL wrong/unreachable | `kubectl exec -n ui deploy/open-webui -- curl -s http://vllm-router.llm.svc.cluster.local/v1/models` |
| Picker empty but exec-curl works | Trailing `/v1` missing/doubled in env | Base URL must end in exactly one `/v1` |
| Chat hangs forever | CPU engines busy | Watch Grafana queue; short prompts; patience is realistic UX for CPU |
| Pod restarts at startup | PVC not writable / slow first boot | Give it 2 min (image unpacks); check `describe` restart reason |

## Stretch (optional)

1. In browser dev tools → Network: find the streaming response. It's the same SSE chunks you curled in lab 03.
2. Set `WEBUI_AUTH=True`, create an account — see the local-vs-exposed security line the lesson warns about.
3. Second model in the picker: add `--served-model-name qwen-alias` to the engine args — where does the alias surface?

## Leave behind

Everything. Lab 09 loads the same path the UI uses.
