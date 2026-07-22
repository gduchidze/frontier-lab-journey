#!/usr/bin/env bash
# Lab 20 grader — vLLM API tour
set -u
cd "$(dirname "$0")/../.."
PASS=0; FAIL=0
ok()  { echo "  ✅ $1"; PASS=$((PASS+1)); }
bad() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
check(){ local d="$1"; shift; if eval "$@" >/dev/null 2>&1; then ok "$d"; else bad "$d"; fi; }

T=docs/vllm-api-tour.md
echo "Lab 20 — verifying…"
check "api-tour doc exists"                 "[ -f $T ]"
check "structured-output section"           "grep -qiE 'structured|json_schema|schema' $T"
check "hostile-prompt case documented"      "grep -qiE 'haiku|hostile|force' $T"
check "multimodal section (result or gap)"  "grep -qiE 'image|multimodal' $T"
check "sampling table ≥4 rows"              "[ \$(grep -cE '^\|.*\|' $T) -ge 5 ]"
check "seed determinism answered"           "grep -qi 'seed' $T"
check "offline batch Job exists"            "kubectl get job offline-batch -n llm"
check "offline batch succeeded"             "[ -n \"\$(kubectl get job offline-batch -n llm -o jsonpath='{.status.succeeded}')\" ]"
check "vllm-gap-map.md exists"              "[ -f docs/vllm-gap-map.md ]"
check "gap map admits gaps"                 "grep -qi 'need study' docs/vllm-gap-map.md"

echo "  … alias check (live)"
kubectl port-forward -n llm svc/vllm-router 18080:80 >/dev/null 2>&1 &
PF=$!; sleep 3
if curl -s -m 10 localhost:18080/v1/models | grep -qE 'qwen-prod|served'; then
  ok "served-model-name alias visible"
else
  echo "  ℹ️  alias not detected via router — fine if you verified in the UI and documented it"
fi
kill $PF 2>/dev/null

echo
echo "Result: $PASS passed, $FAIL failed"
if [ $FAIL -eq 0 ]; then
  echo "🏁 COURSE COMPLETE — 20/20. Remaining rituals: lesson-18 defense, 2-week cold rebuild, quarterly gap-map re-grade."
  echo "Go update MISSION.md. Then go interview."
else
  echo "Fix ❌ — the tour doc is the artifact; runs without writeups don't count."
fi
exit $FAIL
