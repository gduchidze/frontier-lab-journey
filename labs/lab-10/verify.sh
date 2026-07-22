#!/usr/bin/env bash
# Lab 10 grader — autoscaling + capstone artifacts
set -u
cd "$(dirname "$0")/../.."   # repo root
PASS=0; FAIL=0
ok()  { echo "  ✅ $1"; PASS=$((PASS+1)); }
bad() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
check(){ local d="$1"; shift; if eval "$@" >/dev/null 2>&1; then ok "$d"; else bad "$d"; fi; }

echo "Lab 10 — verifying…"
check "metrics API live (kubectl top nodes)"   "kubectl top nodes"
check "HPA 'vllm' exists"                      "kubectl get hpa vllm -n llm"
check "HPA target not <unknown>"               "! kubectl get hpa vllm -n llm --no-headers | grep -q unknown"
check "scale-down stabilization window set"    "[ \"\$(kubectl get hpa vllm -n llm -o jsonpath='{.spec.behavior.scaleDown.stabilizationWindowSeconds}')\" = '300' ]"
check "container has CPU request (HPA math)"   "kubectl get deploy vllm -n llm -o jsonpath='{.spec.template.spec.containers[0].resources.requests.cpu}' | grep -q ."

echo "  … capstone artifacts"
check "README.md exists"                       "[ -f README.md ]"
check "README has architecture section"        "grep -qi 'architecture' README.md"
check "README has quickstart"                  "grep -qiE 'quick ?start' README.md"
check "README has benchmark/results section"   "grep -qiE 'benchmark|results' README.md"
check "README covers limitations/decisions"    "grep -qiE 'limitation|design decision|trade-?off' README.md"
check "main.py boilerplate removed"            "[ ! -f main.py ]"
check "load test results committed"            "[ -f load_tests/RESULTS.md ]"

echo
echo "Result: $PASS passed, $FAIL failed"
if [ $FAIL -eq 0 ]; then
  echo "🎉 CAPSTONE COMPLETE. Book the mock interview with your teacher. Final exam in 1 week: rebuild from README alone."
else
  echo "Fix ❌ — part A issues: describe hpa; part B: the README checklist in lesson 10."
fi
exit $FAIL
