#!/usr/bin/env bash
# Lab 16 grader — distributed design doc
set -u
cd "$(dirname "$0")/../.."
PASS=0; FAIL=0
ok()  { echo "  ✅ $1"; PASS=$((PASS+1)); }
bad() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
check(){ local d="$1"; shift; if eval "$@" >/dev/null 2>&1; then ok "$d"; else bad "$d"; fi; }

D=docs/distributed-design.md
echo "Lab 16 — verifying…"
check "design doc exists"                  "[ -f $D ]"
check "70B sizing with arithmetic"         "grep -qi '70' $D && grep -qE '[0-9]+ ?(GB|GiB)' $D"
check "KV-per-token math shown"            "grep -qiE 'kv.{0,20}(token|per)' $D"
check "fp8 section names new constraint"   "grep -qi 'fp8' $D"
check "405B multi-node layout"             "grep -qi '405' $D"
check "TP discussed"                       "grep -qiE 'tensor.parallel|TP' $D"
check "PP discussed"                       "grep -qiE 'pipeline|PP' $D"
check "KV offload / LMCache mapped"        "grep -qiE 'lmcache|offload' $D"
check "P/D vs DP decision present"         "grep -qiE 'disaggregat' $D"
check "blast radius / failure analysis"    "grep -qiE 'blast|failure' $D"

echo
echo "Result: $PASS passed, $FAIL failed"
[ $FAIL -eq 0 ] && echo "🎉 Doc complete. Now the part that matters: ask the teacher to attack it." \
                || echo "Fix ❌ — each miss is a section interviewers WILL probe."
exit $FAIL
