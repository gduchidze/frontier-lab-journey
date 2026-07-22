#!/usr/bin/env bash
# Lab 03 grader — run while the vllm container is up on :8000
set -u
PASS=0; FAIL=0
ok()  { echo "  ✅ $1"; PASS=$((PASS+1)); }
bad() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
check(){ local d="$1"; shift; if eval "$@" >/dev/null 2>&1; then ok "$d"; else bad "$d"; fi; }

echo "Lab 03 — verifying…"
check "image vllm-cpu:local exists"          "docker image inspect vllm-cpu:local"
check "image is arm64"                       "docker image inspect vllm-cpu:local --format '{{.Architecture}}' | grep -q arm64"
check "container 'vllm' running"             "docker ps --format '{{.Names}}' | grep -qx vllm"
check "/health returns 200"                  "[ \"\$(curl -s -o /dev/null -w '%{http_code}' localhost:8000/health)\" = '200' ]"
check "/v1/models lists a Qwen model"        "curl -s localhost:8000/v1/models | grep -q Qwen"
check "chat completion returns content"      "curl -s -m 120 localhost:8000/v1/chat/completions -H 'Content-Type: application/json' -d '{\"model\":\"'\$(curl -s localhost:8000/v1/models | python3 -c 'import json,sys;print(json.load(sys.stdin)[\"data\"][0][\"id\"])')'\",\"messages\":[{\"role\":\"user\",\"content\":\"say ok\"}],\"max_tokens\":5}' | grep -q '\"content\"'"
check "/metrics exposes vllm: series"        "curl -s localhost:8000/metrics | grep -q '^vllm:'"
check "hf-cache volume exists"               "docker volume inspect hf-cache"
check "weights cached in volume"             "docker run --rm -v hf-cache:/c alpine sh -c 'ls /c/hub 2>/dev/null | grep -q models'"

echo
echo "Result: $PASS passed, $FAIL failed"
if [ $FAIL -eq 0 ]; then
  echo "🎉 Engine mastered. Note WHICH model worked (Qwen3.5-0.8B or fallback) for the learning record."
else
  echo "Fix ❌ items — docker logs vllm is your friend; or ask your teacher with that output."
fi
exit $FAIL
