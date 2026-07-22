#!/usr/bin/env bash
# Lab 05 grader
set -u
cd "$(dirname "$0")/../.."   # repo root
PASS=0; FAIL=0
ok()  { echo "  ✅ $1"; PASS=$((PASS+1)); }
bad() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
check(){ local d="$1"; shift; if eval "$@" >/dev/null 2>&1; then ok "$d"; else bad "$d"; fi; }

echo "Lab 05 — verifying…"
check "chart dir exists"                     "[ -f charts/slm-stack/Chart.yaml ]"
check "helm lint passes"                     "helm lint charts/slm-stack"
check "template renders a Deployment"        "helm template charts/slm-stack | grep -q 'kind: Deployment'"
check "template renders PVC + Service"       "helm template charts/slm-stack | grep -q 'kind: PersistentVolumeClaim' && helm template charts/slm-stack | grep -q 'kind: Service'"
check "model name comes from values"         "helm template charts/slm-stack | grep -q 'Qwen'"
check "service port named http in render"    "helm template charts/slm-stack | grep -q 'name: http'"
check "release 'slm' deployed"               "helm status slm | grep -q 'STATUS: deployed'"
check "vllm Ready under the release"         "[ \"\$(kubectl get deployment vllm -n llm -o jsonpath='{.status.readyReplicas}')\" = '1' ]"
check "deployment managed by Helm"           "kubectl get deployment vllm -n llm -o jsonpath='{.metadata.labels.app\.kubernetes\.io/managed-by}' | grep -qi helm || helm get manifest slm | grep -q 'name: vllm'"
check "history has ≥3 revisions"             "[ \$(helm history slm --max 100 2>/dev/null | tail -n +2 | wc -l) -ge 3 ]"

echo
echo "Result: $PASS passed, $FAIL failed"
[ $FAIL -eq 0 ] && echo "🎉 Chart owns the stack. helm install slm charts/slm-stack is now your one-command deploy." \
                || echo "Fix ❌ — helm template | less is the debugger. Ask teacher with render output."
exit $FAIL
