#!/usr/bin/env bash
# Lab 01 grader — run BEFORE cleanup
set -u
PASS=0; FAIL=0
ok()  { echo "  ✅ $1"; PASS=$((PASS+1)); }
bad() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
check(){ local d="$1"; shift; if eval "$@" >/dev/null 2>&1; then ok "$d"; else bad "$d"; fi; }

echo "Lab 01 — verifying…"
check "kind cluster 'llm-stack' exists"          "kind get clusters | grep -qx llm-stack"
check "2 nodes registered"                        "[ \$(kubectl get nodes --no-headers | wc -l) -eq 2 ]"
check "all nodes Ready"                           "! kubectl get nodes --no-headers | grep -v ' Ready'"
check "deployment 'hello' exists"                 "kubectl get deployment hello"
check "hello has 2 available replicas"            "[ \"\$(kubectl get deployment hello -o jsonpath='{.status.availableReplicas}')\" = '2' ]"
check "service 'hello' exists"                    "kubectl get svc hello"
check "service has endpoints"                     "[ -n \"\$(kubectl get endpoints hello -o jsonpath='{.subsets[*].addresses[*].ip}')\" ]"

echo
echo "Result: $PASS passed, $FAIL failed"
if [ $FAIL -eq 0 ]; then
  echo "🎉 Lab 01 complete. Tell your teacher — get your learning record. Then do the lesson's cleanup step."
else
  echo "Fix ❌ items (kubectl describe / logs), or ask your teacher with this output."
fi
exit $FAIL
