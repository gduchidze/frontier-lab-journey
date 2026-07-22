#!/usr/bin/env bash
# Lab 19 grader — K8s atlas drills
set -u
cd "$(dirname "$0")/../.."
PASS=0; FAIL=0
ok()  { echo "  ✅ $1"; PASS=$((PASS+1)); }
bad() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
check(){ local d="$1"; shift; if eval "$@" >/dev/null 2>&1; then ok "$d"; else bad "$d"; fi; }

C='{.spec.template.spec.containers[0]}'
echo "Lab 19 — verifying…"
check "batch Job exists"                    "kubectl get job batch-eval -n llm"
check "Job completed 6/6"                   "[ \"\$(kubectl get job batch-eval -n llm -o jsonpath='{.status.succeeded}')\" = '6' ]"
check "engine preStop hook set"             "kubectl get deploy vllm -n llm -o jsonpath=\"$C{.lifecycle.preStop}\" | grep -q ."
check "grace period ≥300s"                  "[ \"\$(kubectl get deploy vllm -n llm -o jsonpath='{.spec.template.spec.terminationGracePeriodSeconds}')\" -ge 300 ]"
check "PDB on engines"                      "kubectl get pdb -n llm --no-headers | grep -q vllm"
check "all nodes schedulable (uncordoned)"  "! kubectl get nodes --no-headers | grep -q SchedulingDisabled"
check "engines Ready post-drain"            "kubectl get deployment vllm -n llm -o jsonpath='{.status.readyReplicas}' | grep -qE '^[12]$'"
check "ModelEndpoint CRD registered"        "kubectl get crd | grep -qi modelendpoint"
check "≥1 ModelEndpoint object"             "[ \$(kubectl get modelendpoints -A --no-headers 2>/dev/null | wc -l) -ge 1 ]"
check "k8s-gap-map.md exists"               "[ -f docs/k8s-gap-map.md ]"
check "gap map admits gaps"                 "grep -qi 'need study' docs/k8s-gap-map.md"

echo
echo "Result: $PASS passed, $FAIL failed"
[ $FAIL -eq 0 ] && echo "🎉 Atlas drills done. The gap map is your revision syllabus — schedule it." \
                || echo "Fix ❌ — each drill is a real on-call move; don't skip."
exit $FAIL
