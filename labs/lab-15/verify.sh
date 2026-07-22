#!/usr/bin/env bash
# Lab 15 grader — tuning study artifacts
set -u
cd "$(dirname "$0")/../.."
PASS=0; FAIL=0
ok()  { echo "  ✅ $1"; PASS=$((PASS+1)); }
bad() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
check(){ local d="$1"; shift; if eval "$@" >/dev/null 2>&1; then ok "$d"; else bad "$d"; fi; }

echo "Lab 15 — verifying…"
check "≥5 bench result JSONs"            "[ \$(ls load_tests/tuning/*.json 2>/dev/null | wc -l) -ge 5 ]"
check "tuning-report.md exists"          "[ -f docs/tuning-report.md ]"
check "report states the workload"       "grep -qiE 'workload|input.len|128' docs/tuning-report.md"
check "run table ≥5 data rows"           "[ \$(grep -cE '^\|.*[0-9]' docs/tuning-report.md) -ge 5 ]"
check "covers max-num-seqs sweep"        "grep -qi 'max-num-seqs' docs/tuning-report.md"
check "covers prefix caching"            "grep -qi 'prefix' docs/tuning-report.md"
check "has conclusions section"          "grep -qiE 'conclusion|finding' docs/tuning-report.md"
check "has GPU transfer section"         "grep -qiE 'h100|gpu|fp8' docs/tuning-report.md"

echo
echo "Result: $PASS passed, $FAIL failed"
[ $FAIL -eq 0 ] && echo "🎉 A real tuning report. This document interviews better than most resumes." \
                || echo "Fix ❌ — the report is the deliverable; runs without the writeup don't count."
exit $FAIL
