#!/usr/bin/env bash
# Lab 17 grader — SRE artifacts
set -u
cd "$(dirname "$0")/../.."
PASS=0; FAIL=0
ok()  { echo "  ✅ $1"; PASS=$((PASS+1)); }
bad() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
check(){ local d="$1"; shift; if eval "$@" >/dev/null 2>&1; then ok "$d"; else bad "$d"; fi; }

echo "Lab 17 — verifying…"
check "slo.md with PromQL"                "[ -f docs/slo.md ] && grep -q 'vllm:' docs/slo.md"
check "PrometheusRule applied"            "kubectl get prometheusrule -A --no-headers | grep -q ."
check "TTFT/burn alert defined"           "kubectl get prometheusrule -A -o json | grep -qiE 'ttft|burn|time_to_first_token'"
check "engine-down alert defined"         "kubectl get prometheusrule -A -o json | grep -qiE 'enginedown|up == 0|up==0'"
check "queue alert defined"               "kubectl get prometheusrule -A -o json | grep -qi 'waiting'"
check "runbook: high-ttft"                "[ -f runbooks/high-ttft.md ] && grep -qi mitigat runbooks/high-ttft.md"
check "runbook: engine-down"              "[ -f runbooks/engine-down.md ]"
check "chaos-day.md ≥3 experiments"       "[ -f docs/chaos-day.md ] && [ \$(grep -ciE 'expect' docs/chaos-day.md) -ge 3 ]"
check "postmortem exists"                 "ls docs/postmortems/0001-*.md"
check "postmortem has action items"       "grep -qi 'action' docs/postmortems/0001-*.md"

echo "  … alert state (informational)"
PROM_SVC=$(kubectl get svc -n monitoring -o name | grep -E 'prometheus$' | head -1)
if [ -n "$PROM_SVC" ]; then
  kubectl port-forward -n monitoring "$PROM_SVC" 19090:9090 >/dev/null 2>&1 &
  PF=$!; sleep 3
  curl -s 'localhost:19090/api/v1/rules' | grep -qi 'firing\|pending' && ok "some alert has fired/pended (history counts)" || echo "  ℹ️  no alert currently pending/firing — fine if you screenshotted the drill"
  kill $PF 2>/dev/null
fi

echo
echo "Result: $PASS passed, $FAIL failed"
[ $FAIL -eq 0 ] && echo "🎉 You can run this thing. The postmortem doc is a hiring signal — polish it." \
                || echo "Fix ❌ — every miss is a 3 AM regret prevented now."
exit $FAIL
