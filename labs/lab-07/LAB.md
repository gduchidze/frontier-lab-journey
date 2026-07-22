# Lab 07 — Observability: Prometheus + Grafana

Lesson: [0007-observability.html](../../lessons/0007-observability.html) · Time: ~2 h

## Before you start

```bash
kubectl get deploy -n llm | grep -E 'vllm|router'   # stack from lab 06 up
```

## Objectives

- kube-prometheus-stack (release `kps`) in namespace `monitoring` — with the ServiceMonitor-selector flag
- ServiceMonitor scraping vLLM engines (named port `http`!)
- Targets UP in Prometheus; the 3 PromQL patterns run; Grafana dashboard: imported + one hand-built P90 TTFT panel
- Load-and-watch drill narrated out loud

## Checkpoints — `./verify.sh`

- [ ] monitoring pods all Running
- [ ] ServiceMonitor `vllm` exists
- [ ] Prometheus reports vLLM targets **UP**
- [ ] `vllm:num_requests_running` queryable via Prometheus API
- [ ] By hand: Grafana dashboard saved with a live TTFT panel (screenshot it for the portfolio)

## If stuck

| Symptom | Likely cause | Move |
|---|---|---|
| Install hangs / pods Pending | RAM squeeze (this chart is heavy) | Scale engines to 1 for install, back to 2 after |
| Target absent from /targets | Selector/port-name mismatch | Walk the [scrape-debugging checklist](../../reference/observability-cheatsheet.html) top to bottom |
| Target DOWN, `connection refused` | Wrong port name → wrong port scraped | Service port must be `name: http`, ServiceMonitor `port: http` |
| Query returns nothing | No traffic since scrape start | Fire the traffic loop, wait 2 scrape intervals (30 s) |
| Grafana login fails | Different admin password | `kubectl get secret -n monitoring kps-grafana -o jsonpath='{.data.admin-password}' \| base64 -d` |
| Grafana panel "No data" but Prometheus has it | Wrong datasource selected | Pick the provisioned Prometheus datasource explicitly |

## Stretch (optional)

1. Add a router ServiceMonitor too — the router exports per-engine stats; compare its view with the engines' own.
2. Alert rule: `PrometheusRule` firing when `sum(vllm:num_requests_waiting) > 10` for 2 min. Watch it fire during lab 09.
3. In Grafana Explore, find the scrape itself: `up{namespace="llm"}` — the meta-metric every on-call starts from.

## Leave behind

Everything. Labs 09–10 read these dashboards live.
