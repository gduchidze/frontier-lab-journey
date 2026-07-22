#!/usr/bin/env bash
# Lab 13 grader — security posture
set -u
cd "$(dirname "$0")/../.."
PASS=0; FAIL=0
ok()  { echo "  ✅ $1"; PASS=$((PASS+1)); }
bad() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
check(){ local d="$1"; shift; if eval "$@" >/dev/null 2>&1; then ok "$d"; else bad "$d"; fi; }

echo "Lab 13 — verifying…"
check "Cilium enforcing (not kindnet)"       "kubectl get pods -n kube-system -l k8s-app=cilium --no-headers | grep -q Running"
check "default-deny policy in llm"           "kubectl get networkpolicy -n llm -o json | grep -q '\"ingress\":\\[\\]' || kubectl get networkpolicy -n llm --no-headers | grep -qi 'deny'"
check "≥3 allow policies in llm"             "[ \$(kubectl get networkpolicy -n llm --no-headers | wc -l) -ge 4 ]"
check "UI still reaches router"              "kubectl exec -n ui deploy/open-webui -- curl -s -m 10 -o /dev/null -w '%{http_code}' http://vllm-router.llm.svc.cluster.local/v1/models | grep -qE '200|401'"
echo "  … attacker isolation test (10s)"
if kubectl run verify-attacker --rm -i --restart=Never --image=curlimages/curl --command -- curl -s -m 5 http://vllm.llm.svc.cluster.local:8000/health 2>/dev/null | grep -q .; then
  bad "attacker pod BLOCKED from engines (it got through!)"
else
  ok "attacker pod BLOCKED from engines"
fi
check "ResourceQuota active in llm"          "kubectl get resourcequota -n llm --no-headers | grep -q ."
check "LimitRange active in llm"             "kubectl get limitrange -n llm --no-headers | grep -q ."
check "api-key secret exists"                "kubectl get secret vllm-api-key -n llm"
echo "  … engine auth test"
kubectl port-forward -n llm svc/vllm 18000:8000 >/dev/null 2>&1 &
PF=$!; sleep 3
CODE=$(curl -s -o /dev/null -w '%{http_code}' -m 10 localhost:18000/v1/models)
[ "$CODE" = "401" ] && ok "engine returns 401 without key" || bad "engine returns 401 without key (got $CODE)"
kill $PF 2>/dev/null
check "RBAC audit saved"                     "[ -f docs/rbac-audit.md ]"

echo
echo "Result: $PASS passed, $FAIL failed"
[ $FAIL -eq 0 ] && echo "🎉 Locked. Screenshot the attacker timeout — portfolio evidence of defense in depth." \
                || echo "Fix ❌ — 'cilium hubble observe' or describe networkpolicy to see who's blocking whom."
exit $FAIL
