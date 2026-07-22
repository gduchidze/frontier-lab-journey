#!/usr/bin/env bash
# Lab 06 grader — router + 2 engines
set -u
PASS=0; FAIL=0
ok()  { echo "  ✅ $1"; PASS=$((PASS+1)); }
bad() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
check(){ local d="$1"; shift; if eval "$@" >/dev/null 2>&1; then ok "$d"; else bad "$d"; fi; }

echo "Lab 06 — verifying…"
check "2 vLLM replicas Ready"            "[ \"\$(kubectl get deployment vllm -n llm -o jsonpath='{.status.readyReplicas}')\" = '2' ]"
check "serviceaccount vllm-router"       "kubectl get serviceaccount vllm-router -n llm"
check "role pod-reader"                  "kubectl get role pod-reader -n llm"
check "rolebinding bound"                "kubectl get rolebinding vllm-router-pod-reader -n llm"
check "router deployment Ready"          "[ \"\$(kubectl get deployment vllm-router -n llm -o jsonpath='{.status.readyReplicas}')\" = '1' ]"
check "router service exists"            "kubectl get svc vllm-router -n llm"
check "no RBAC 'Forbidden' in router"    "! kubectl logs -n llm -l app=vllm-router --tail=200 2>/dev/null | grep -qi forbidden"

echo "  … live test through router"
kubectl port-forward -n llm svc/vllm-router 18080:80 >/dev/null 2>&1 &
PF=$!; sleep 3
if curl -s -m 15 localhost:18080/v1/models | grep -q '"id"'; then
  ok "/v1/models served through router"
else
  bad "/v1/models served through router"
fi
kill $PF 2>/dev/null

echo
echo "Result: $PASS passed, $FAIL failed"
[ $FAIL -eq 0 ] && echo "🎉 Distributed serving. Now prove session affinity BY HAND (4 requests, one header, one pod's logs) — verify can't grade that for you." \
                || echo "Fix ❌ — router logs first (kubectl logs -n llm -l app=vllm-router), then ask teacher."
exit $FAIL
