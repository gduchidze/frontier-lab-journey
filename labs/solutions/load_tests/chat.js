// Lab 09 — k6 scenario with SLO thresholds (CPU-realistic numbers)
// Run: kubectl port-forward -n llm svc/vllm-router 8080:80   then: k6 run chat.js
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 4 },   // ramp to 4 virtual users
    { duration: '2m', target: 4 },   // hold
    { duration: '30s', target: 0 },  // drain
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'],       // <1% errors
    http_req_duration: ['p(90)<30000'],   // P90 end-to-end < 30s on CPU
  },
};

const MODEL = __ENV.MODEL || 'Qwen/Qwen3.5-0.8B';
const BASE = __ENV.BASE_URL || 'http://localhost:8080';

export default function () {
  const res = http.post(
    `${BASE}/v1/chat/completions`,
    JSON.stringify({
      model: MODEL,
      messages: [{ role: 'user', content: 'Reply with one short sentence.' }],
      max_tokens: 32,
    }),
    { headers: { 'Content-Type': 'application/json' }, timeout: '120s' },
  );
  check(res, { 'status 200': (r) => r.status === 200 });
}
