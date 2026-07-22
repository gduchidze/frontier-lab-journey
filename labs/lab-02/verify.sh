#!/usr/bin/env bash
# Lab 02 grader — run after deploy, before break-it steps
set -u
PASS=0; FAIL=0
ok()  { echo "  ✅ $1"; PASS=$((PASS+1)); }
bad() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
check(){ local d="$1"; shift; if eval "$@" >/dev/null 2>&1; then ok "$d"; else bad "$d"; fi; }

C='{.spec.template.spec.containers[0]}'
echo "Lab 02 — verifying…"
check "namespace 'llm' exists"                    "kubectl get ns llm"
check "deployment 'hello' in llm"                 "kubectl get deployment hello -n llm"
check "2 ready replicas"                          "[ \"\$(kubectl get deployment hello -n llm -o jsonpath='{.status.readyReplicas}')\" = '2' ]"
check "startupProbe defined"                      "kubectl get deployment hello -n llm -o jsonpath=\"$C{.startupProbe}\" | grep -q httpGet"
check "readinessProbe defined"                    "kubectl get deployment hello -n llm -o jsonpath=\"$C{.readinessProbe}\" | grep -q httpGet"
check "livenessProbe defined"                     "kubectl get deployment hello -n llm -o jsonpath=\"$C{.livenessProbe}\" | grep -q httpGet"
check "resource requests set"                     "kubectl get deployment hello -n llm -o jsonpath=\"$C{.resources.requests}\" | grep -q cpu"
check "resource limits set"                       "kubectl get deployment hello -n llm -o jsonpath=\"$C{.resources.limits}\" | grep -q memory"
check "configmap 'hello-config' exists"           "kubectl get configmap hello-config -n llm"
check "configmap volume mounted"                  "kubectl get deployment hello -n llm -o jsonpath='{.spec.template.spec.volumes}' | grep -q hello-config"
check "service 'hello' has endpoints"             "[ -n \"\$(kubectl get endpoints hello -n llm -o jsonpath='{.subsets[*].addresses[*].ip}')\" ]"

echo
echo "Result: $PASS passed, $FAIL failed"
if [ $FAIL -eq 0 ]; then
  echo "🎉 Manifests solid. Now go break them (lesson steps 3–4) — that's the real lab."
else
  echo "Fix ❌ items, or ask your teacher with this output + your k8s/lab2.yaml."
fi
exit $FAIL
