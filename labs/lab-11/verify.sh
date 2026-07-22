#!/usr/bin/env bash
# Lab 11 grader — advanced cluster + fake GPU fleet
set -u
PASS=0; FAIL=0
ok()  { echo "  ✅ $1"; PASS=$((PASS+1)); }
bad() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
check(){ local d="$1"; shift; if eval "$@" >/dev/null 2>&1; then ok "$d"; else bad "$d"; fi; }

echo "Lab 11 — verifying…"
check "3 nodes Ready"                       "[ \$(kubectl get nodes --no-headers | grep -c ' Ready') -eq 3 ]"
check "Cilium running"                      "kubectl get pods -n kube-system -l k8s-app=cilium --no-headers | grep -q Running"
check "stack redeployed: engines Ready"     "kubectl get deployment vllm -n llm -o jsonpath='{.status.readyReplicas}' | grep -qE '^[12]$'"
check "router Ready"                        "[ \"\$(kubectl get deployment vllm-router -n llm -o jsonpath='{.status.readyReplicas}')\" = '1' ]"
check "worker2 labeled gpu=true"            "kubectl get node llm-stack-worker2 -o jsonpath='{.metadata.labels.gpu}' | grep -qx true"
check "worker2 tainted NoSchedule"          "kubectl get node llm-stack-worker2 -o jsonpath='{.spec.taints}' | grep -q NoSchedule"
check "fake GPU resource advertised"        "kubectl get node llm-stack-worker2 -o jsonpath='{.status.capacity.example\.com/gpu}' | grep -q ."
check "2 gpu pods on worker2"               "[ \$(kubectl get pods -l app=gpu-workload -o wide --no-headers 2>/dev/null | grep -c worker2) -eq 2 ]"
check "1 gpu pod Pending (insufficient)"    "kubectl get pods -l app=gpu-workload --no-headers 2>/dev/null | grep -q Pending"
check "priorityclasses exist"               "kubectl get priorityclass prod-inference && kubectl get priorityclass batch-experiment"
check "vLLM spread across workers (if 2 replicas)"  "[ \"\$(kubectl get deployment vllm -n llm -o jsonpath='{.spec.replicas}')\" = '1' ] || [ \$(kubectl get pods -n llm -l app=vllm -o wide --no-headers | awk '{print \$7}' | sort -u | wc -l) -ge 2 ]"

echo
echo "Result: $PASS passed, $FAIL failed"
[ $FAIL -eq 0 ] && echo "🎉 Fleet simulated. Note your rebuild time — that number should shrink every time." \
                || echo "Fix ❌ — describe node / describe pod Events tell the scheduling story."
exit $FAIL
