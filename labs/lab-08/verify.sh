#!/usr/bin/env bash
# Lab 08 grader — UI end-to-end
set -u
PASS=0; FAIL=0
ok()  { echo "  ✅ $1"; PASS=$((PASS+1)); }
bad() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
check(){ local d="$1"; shift; if eval "$@" >/dev/null 2>&1; then ok "$d"; else bad "$d"; fi; }

echo "Lab 08 — verifying…"
check "namespace ui exists"                 "kubectl get ns ui"
check "open-webui pod Ready"                "[ \"\$(kubectl get deployment open-webui -n ui -o jsonpath='{.status.readyReplicas}')\" = '1' ]"
check "service type NodePort"               "kubectl get svc open-webui -n ui -o jsonpath='{.spec.type}' | grep -qx NodePort"
check "nodePort is 30080"                   "kubectl get svc open-webui -n ui -o jsonpath='{.spec.ports[0].nodePort}' | grep -qx 30080"
check "base URL targets router DNS"         "kubectl get deployment open-webui -n ui -o jsonpath='{.spec.template.spec.containers[0].env}' | grep -q 'vllm-router.llm.svc.cluster.local'"
check "UI answers on localhost:30080"       "[ \"\$(curl -s -o /dev/null -w '%{http_code}' -m 10 localhost:30080)\" = '200' ]"
check "UI pod can reach router /v1/models"  "kubectl exec -n ui deploy/open-webui -- curl -s -m 10 http://vllm-router.llm.svc.cluster.local/v1/models | grep -q '\"id\"'"

echo
echo "Result: $PASS passed, $FAIL failed"
[ $FAIL -eq 0 ] && echo "🎉 Product shipped. Do the engine-kill demo mid-chat, then trace the request path out loud: browser → ? → ? → ? → engine." \
                || echo "Fix ❌ — the exec-curl check tells you which side is broken (UI config vs router). Ask teacher."
exit $FAIL
