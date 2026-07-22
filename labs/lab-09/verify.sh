#!/usr/bin/env bash
# Lab 09 grader — load-testing artifacts
set -u
cd "$(dirname "$0")/../.."   # repo root
PASS=0; FAIL=0
ok()  { echo "  ✅ $1"; PASS=$((PASS+1)); }
bad() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
check(){ local d="$1"; shift; if eval "$@" >/dev/null 2>&1; then ok "$d"; else bad "$d"; fi; }

echo "Lab 09 — verifying…"
check "k6 installed"                        "command -v k6"
check "load_tests/chat.js exists"           "[ -f load_tests/chat.js ]"
check "chat.js parses (k6 inspect)"         "k6 inspect load_tests/chat.js"
check "thresholds defined"                  "grep -q thresholds load_tests/chat.js"
check "ramp stages defined"                 "grep -q stages load_tests/chat.js"
check "RESULTS.md exists"                   "[ -f load_tests/RESULTS.md ]"
check "RESULTS.md has ≥3 data rows"         "[ \$(grep -cE '^\|? *[0-9]' load_tests/RESULTS.md) -ge 3 ]"
check "bench result JSON saved"             "ls load_tests/*.json >/dev/null 2>&1 || ls /tmp/*serving*.json >/dev/null 2>&1 || ls /tmp/openai*.json >/dev/null 2>&1"

echo
echo "Result: $PASS passed, $FAIL failed"
[ $FAIL -eq 0 ] && echo "🎉 You have numbers. Final oral exam: where's the knee, and what would you buy to move it?" \
                || echo "Fix ❌ — record your runs in load_tests/RESULTS.md (rate | achieved | P50 TTFT | P90 TTFT | tok/s)."
exit $FAIL
