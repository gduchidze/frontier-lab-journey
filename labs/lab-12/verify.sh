#!/usr/bin/env bash
# Lab 12 grader — edge, TLS, streaming annotations
set -u
PASS=0; FAIL=0
ok()  { echo "  ✅ $1"; PASS=$((PASS+1)); }
bad() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
check(){ local d="$1"; shift; if eval "$@" >/dev/null 2>&1; then ok "$d"; else bad "$d"; fi; }

echo "Lab 12 — verifying…"
check "ingress-nginx controller Ready"      "kubectl get pods -n ingress-nginx -l app.kubernetes.io/component=controller --no-headers | grep -q Running"
check "/etc/hosts has llm.local entries"    "grep -q 'chat.llm.local' /etc/hosts && grep -q 'api.llm.local' /etc/hosts"
check "chat host serves UI (http)"          "[ \"\$(curl -s -o /dev/null -w '%{http_code}' -m 10 http://chat.llm.local)\" = '200' ]"
check "api host serves router (http)"       "curl -s -m 10 http://api.llm.local/v1/models | grep -q '\"id\"'"
check "read-timeout annotation set"         "kubectl get ingress -A -o json | grep -q 'proxy-read-timeout'"
check "buffering-off annotation set"        "kubectl get ingress -A -o json | grep -q 'proxy-buffering'"
check "cert-manager Running"                "kubectl get pods -n cert-manager --no-headers | grep -q Running"
check "ClusterIssuer Ready"                 "kubectl get clusterissuer -o json | grep -q '\"status\":\"True\"'"
check "Certificates Ready"                  "! kubectl get certificate -A --no-headers 2>/dev/null | grep -vq True"
check "HTTPS answers on api host"           "curl -sk -m 10 https://api.llm.local/v1/models | grep -q '\"id\"'"

echo
echo "Result: $PASS passed, $FAIL failed"
[ $FAIL -eq 0 ] && echo "🎉 Real edge. Do the buffering on/off stream demo and narrate it — that's the interview story." \
                || echo "Fix ❌ — curl -v and controller logs (kubectl logs -n ingress-nginx) show the hop that breaks."
exit $FAIL
