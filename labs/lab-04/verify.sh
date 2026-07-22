#!/usr/bin/env bash
# Lab 04 grader — run once the vllm pod is Ready
set -u
PASS=0; FAIL=0
ok()  { echo "  ✅ $1"; PASS=$((PASS+1)); }
bad() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
check(){ local d="$1"; shift; if eval "$@" >/dev/null 2>&1; then ok "$d"; else bad "$d"; fi; }

C='{.spec.template.spec.containers[0]}'
echo "Lab 04 — verifying…"
check "image on kind node"              "docker exec llm-stack-worker crictl images 2>/dev/null | grep -q vllm-cpu || docker exec llm-stack-control-plane crictl images | grep -q vllm-cpu"
check "PVC hf-cache Bound"              "[ \"\$(kubectl get pvc hf-cache -n llm -o jsonpath='{.status.phase}')\" = 'Bound' ]"
check "deployment vllm exists"          "kubectl get deployment vllm -n llm"
check "vllm pod Ready"                  "[ \"\$(kubectl get deployment vllm -n llm -o jsonpath='{.status.readyReplicas}')\" = '1' ]"
check "startup probe budget ≥10 min"    "[ \$(( \$(kubectl get deploy vllm -n llm -o jsonpath=\"$C{.startupProbe.failureThreshold}\") * \$(kubectl get deploy vllm -n llm -o jsonpath=\"$C{.startupProbe.periodSeconds}\") )) -ge 600 ]"
check "service port named 'http'"       "kubectl get svc vllm -n llm -o jsonpath='{.spec.ports[0].name}' | grep -qx http"
check "/dev/shm Memory emptyDir"        "kubectl get deploy vllm -n llm -o jsonpath='{.spec.template.spec.volumes}' | grep -q '\"medium\":\"Memory\"'"
check "PVC mounted at HF cache path"    "kubectl get deploy vllm -n llm -o jsonpath=\"$C{.volumeMounts}\" | grep -q '/root/.cache/huggingface'"

echo "  … live chat test (may take ~60s on CPU)"
kubectl port-forward -n llm svc/vllm 18000:8000 >/dev/null 2>&1 &
PF=$!; sleep 3
MODEL=$(curl -s localhost:18000/v1/models | python3 -c 'import json,sys;print(json.load(sys.stdin)["data"][0]["id"])' 2>/dev/null || echo "")
if [ -n "$MODEL" ] && curl -s -m 120 localhost:18000/v1/chat/completions -H 'Content-Type: application/json' \
     -d "{\"model\":\"$MODEL\",\"messages\":[{\"role\":\"user\",\"content\":\"say ok\"}],\"max_tokens\":5}" | grep -q '"content"'; then
  ok "chat completion via cluster Service"
else
  bad "chat completion via cluster Service"
fi
kill $PF 2>/dev/null

echo
echo "Result: $PASS passed, $FAIL failed"
[ $FAIL -eq 0 ] && echo "🎉 Engine lives in the cluster. Do the PVC-speed test (delete pod, time the reload), then report to teacher." \
                || echo "Fix ❌ items — describe/logs first, then ask your teacher."
exit $FAIL
