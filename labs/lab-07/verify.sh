#!/usr/bin/env bash
# Lab 07 grader — monitoring stack + scraping
set -u
PASS=0; FAIL=0
ok()  { echo "  ✅ $1"; PASS=$((PASS+1)); }
bad() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
check(){ local d="$1"; shift; if eval "$@" >/dev/null 2>&1; then ok "$d"; else bad "$d"; fi; }

echo "Lab 07 — verifying…"
check "namespace monitoring exists"        "kubectl get ns monitoring"
check "prometheus pod Running"             "kubectl get pods -n monitoring -l app.kubernetes.io/name=prometheus --no-headers | grep -q Running"
check "grafana pod Running"                "kubectl get pods -n monitoring -l app.kubernetes.io/name=grafana --no-headers | grep -q Running"
check "servicemonitor vllm exists"         "kubectl get servicemonitor vllm -n llm"
check "vllm Service port named http"       "kubectl get svc vllm -n llm -o jsonpath='{.spec.ports[0].name}' | grep -qx http"

echo "  … querying Prometheus API"
PROM_SVC=$(kubectl get svc -n monitoring -o name | grep -E 'kube-prometheus.*-prometheus$' | head -1)
kubectl port-forward -n monitoring "$PROM_SVC" 19090:9090 >/dev/null 2>&1 &
PF=$!; sleep 4
if curl -s 'localhost:19090/api/v1/targets?state=active' | grep -q '"namespace":"llm"'; then
  ok "vLLM target registered in Prometheus"
else
  bad "vLLM target registered in Prometheus"
fi
if curl -s 'localhost:19090/api/v1/targets?state=active' | python3 -c "
import json,sys
d=json.load(sys.stdin)
ts=[t for t in d['data']['activeTargets'] if t.get('labels',{}).get('namespace')=='llm']
sys.exit(0 if ts and all(t['health']=='up' for t in ts) else 1)" 2>/dev/null; then
  ok "vLLM targets health = up"
else
  bad "vLLM targets health = up"
fi
if curl -s 'localhost:19090/api/v1/query?query=vllm:num_requests_running' | grep -q '"result":\[{'; then
  ok "vllm:num_requests_running has series"
else
  bad "vllm:num_requests_running has series (fire some traffic, wait 30s, retry)"
fi
kill $PF 2>/dev/null

echo
echo "Result: $PASS passed, $FAIL failed"
[ $FAIL -eq 0 ] && echo "🎉 Eyes on. Build the Grafana TTFT panel by hand + screenshot it — verify can't grade dashboards." \
                || echo "Fix ❌ — scrape-debugging checklist in reference/observability-cheatsheet.html, then teacher."
exit $FAIL
