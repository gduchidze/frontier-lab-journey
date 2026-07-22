#!/usr/bin/env bash
# Lab 11 — advertise a fake extended resource example.com/gpu: 2 on worker2.
# Kubelet restarts wipe status patches; re-run if the resource vanishes.
set -euo pipefail
NODE="${1:-llm-stack-worker2}"

kubectl proxy --port=8001 >/dev/null 2>&1 &
PROXY_PID=$!
sleep 2

curl -s --header "Content-Type: application/json-patch+json" \
  --request PATCH \
  --data '[{"op":"add","path":"/status/capacity/example.com~1gpu","value":"2"}]' \
  "http://127.0.0.1:8001/api/v1/nodes/${NODE}/status" >/dev/null

kill $PROXY_PID 2>/dev/null

echo "Node ${NODE} now advertises:"
kubectl get node "${NODE}" -o jsonpath='{.status.capacity.example\.com/gpu}'
echo " × example.com/gpu"
