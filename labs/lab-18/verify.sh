#!/usr/bin/env bash
# Lab 18 grader — capstone artifacts
set -u
cd "$(dirname "$0")/../.."
PASS=0; FAIL=0
ok()  { echo "  ✅ $1"; PASS=$((PASS+1)); }
bad() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
check(){ local d="$1"; shift; if eval "$@" >/dev/null 2>&1; then ok "$d"; else bad "$d"; fi; }

CM=docs/cost-model.md
PD=docs/platform-design.md
echo "Lab 18 — verifying…"
check "cost-model.md exists"               "[ -f $CM ]"
check "3 scenarios present"                "grep -qi 'a10' $CM && grep -qiE 'cpu|mac|local' $CM && grep -qiE 'api|breakeven' $CM"
check "assumptions stated"                 "grep -qi 'assum' $CM"
check "breakeven computed"                 "grep -qiE 'breakeven|crossover' $CM"
check "platform-design.md exists"          "[ -f $PD ]"
for s in "slo" "architect" "capacity" "failure" "tenan|security" "rollout" "open question"; do
  check "design doc section: $s"           "grep -qiE '$s' $PD"
done
check "rejected alternatives documented"   "grep -qiE 'reject|alternative|considered' $PD"
check "≥5 citations to prior artifacts"    "[ \$(grep -cE 'docs/|runbooks/|tuning-report|distributed-design|model-rollout|slo\.md' $PD) -ge 5 ]"
check "README links design doc"            "grep -q 'platform-design' README.md"
check "README links tuning report"         "grep -q 'tuning-report' README.md"
check "README links a postmortem"          "grep -qi 'postmortem' README.md"

echo
echo "Result: $PASS passed, $FAIL failed"
if [ $FAIL -eq 0 ]; then
  echo "🏆 SENIOR CAPSTONE ARTIFACTS COMPLETE."
  echo "Remaining, human-only: the defense, the external post, and the 2-week cold rebuild."
else
  echo "Fix ❌ — the design doc IS the take-home interview. Finish it properly."
fi
exit $FAIL
