# Lab 17 — Ops Day: SLOs, Alerts, Chaos

Lesson: [0017-sre-inference.html](../../lessons/0017-sre-inference.html) · Time: ~2.5 h · **ADVANCED**

## Objectives

- `docs/slo.md` — 3 SLIs, targets, measurement queries
- `k8s/alerts.yaml` PrometheusRule: fast-burn TTFT alert (two windows) + `VLLMEngineDown` + `QueueBacklog`
- One alert driven Pending → Firing by real load
- Runbooks: `runbooks/high-ttft.md`, `runbooks/engine-down.md` (real commands for THIS stack)
- Chaos day under load, hypotheses written FIRST → `docs/chaos-day.md`
- One full blameless postmortem → `docs/postmortems/0001-*.md`

## Chaos menu (under steady k6 load, expectations before each)

1. `kubectl delete pod` an engine — expect router drop <5s, no 5xx
2. Delete the router pod — expect UI errors until Deployment restores (~10s?)
3. `docker pause llm-stack-worker` — the HUNG node. Expect… write it down first. This one surprises.
4. Delete the Prometheus pod — who noticed? What was blind while it restarted?

Unpause: `docker unpause llm-stack-worker`.

## Checkpoints — `./verify.sh`

- [ ] SLO doc with 3 SLIs + PromQL
- [ ] PrometheusRule loaded; alerts visible in Prometheus
- [ ] QueueBacklog (or TTFT burn) reached Firing during load (screenshot)
- [ ] Both runbooks in skeleton format with real commands
- [ ] chaos-day.md: ≥3 experiments, expected vs observed each
- [ ] One postmortem: timeline, impact, 5-whys, action items

## If stuck

| Symptom | Move |
|---|---|
| Rule not in Prometheus | PrometheusRule needs labels the operator selects (or the nil-uses-false flag from lab 07 covers rules too — check `kubectl get prometheusrule -A`) |
| Burn-rate math confusing | Start with QueueBacklog (simple gauge threshold), add burn-rate after it fires once |
| Alert never fires | Push past the lesson-9 knee — you measured exactly where it is |
| Paused node: nothing happens for ages | THAT'S the finding. Time it: NotReady after ~40s, eviction minutes later. Write it down |

## Stretch

Alertmanager → real notification (email/Slack webhook). The 3 AM pipe, end to end.
