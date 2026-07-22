#!/usr/bin/env bash
# Lab 14 grader — GitOps loop
set -u
cd "$(dirname "$0")/../.."
PASS=0; FAIL=0
ok()  { echo "  ✅ $1"; PASS=$((PASS+1)); }
bad() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
check(){ local d="$1"; shift; if eval "$@" >/dev/null 2>&1; then ok "$d"; else bad "$d"; fi; }

echo "Lab 14 — verifying…"
check "argocd pods Running"                 "kubectl get pods -n argocd --no-headers | grep -q Running"
check "Application exists"                  "kubectl get application -n argocd --no-headers | grep -q ."
APP=$(kubectl get application -n argocd -o name | head -1)
check "Application Synced"                  "kubectl get $APP -n argocd -o jsonpath='{.status.sync.status}' | grep -qx Synced"
check "Application Healthy"                 "kubectl get $APP -n argocd -o jsonpath='{.status.health.status}' | grep -qx Healthy"
check "automated sync enabled"              "kubectl get $APP -n argocd -o jsonpath='{.spec.syncPolicy.automated}' | grep -q ."
check "selfHeal enabled"                    "kubectl get $APP -n argocd -o jsonpath='{.spec.syncPolicy.automated.selfHeal}' | grep -qx true"
check "git: a revert commit exists"         "git log --oneline -20 | grep -qi revert"
check "model-rollout design doc"            "[ -f docs/model-rollout.md ]"
check "rollout doc covers abort criteria"   "grep -qi 'abort' docs/model-rollout.md"

echo
echo "Result: $PASS passed, $FAIL failed"
[ $FAIL -eq 0 ] && echo "🎉 The cluster follows git. Your deploy tool is now a pull request." \
                || echo "Fix ❌ — Argo UI's diff view shows exactly what disagrees with git."
exit $FAIL
