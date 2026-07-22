# Lab 18 — Cost Model + the Senior Capstone

Lesson: [0018-cost-capstone.html](../../lessons/0018-cost-capstone.html) · Time: ~3 h + defense · **ADVANCED FINAL**

## Objectives

- `docs/cost-model.md`: 3 scenarios (your CPU stack honestly costed · 2×A10 cloud · 70B-fp8 API-vs-self-host with computed breakeven)
- `docs/platform-design.md`: the full design prompt from the lesson, every section citing a prior artifact
- Mock interview defense with the teacher; doc revised after
- Portfolio shipped: README links every artifact; posted for external feedback

## Design prompt (paste into your doc header)

> Chat + API product. 3 models (0.8B, 8B, 70B). 5k peak RPS, mostly small models. Interactive tier P90 TTFT < 1.5s; batch tier overnight. 3 enterprise tenants need isolation. SOC2 on the horizon. CFO watches the GPU bill.

Required sections: Context & requirements → SLOs → Architecture (+2 rejected alternatives) → Capacity & cost model → Failure modes & blast radii → Security/tenancy → Rollout & operations → Open questions.

## Artifact cross-reference (the point of the whole course)

| Section | Cites |
|---|---|
| SLOs | docs/slo.md (lab 17) |
| Capacity | lesson-9 knee + docs/tuning-report.md (lab 15) |
| Architecture | docs/distributed-design.md (lab 16) |
| Tenancy | netpol + quota + attacker screenshot (lab 13) |
| Rollout | docs/model-rollout.md (lab 14) |
| Operations | runbooks/ + postmortem (lab 17) |
| Cost | docs/cost-model.md (this lab) |

## Checkpoints — `./verify.sh`

- [ ] cost-model.md: 3 scenarios, assumptions stated, breakeven computed
- [ ] platform-design.md: all 8 sections, ≥5 citations to prior artifacts
- [ ] README links design doc, tuning report, postmortem, benchmarks
- [ ] By hand: defense survived; revision committed; posted externally

## The defenses (schedule with teacher)

1. "Walk me through one interactive request, edge to token."
2. "Engine fleet OOMs at 2 AM. Go." (runbook, live)
3. "CFO cuts GPU budget 40%. What degrades, in what order, and who decides?"
4. "Why not the OpenAI API for everything?" (your breakeven math, out loud)

## Two weeks later — the real final

`kind delete cluster --name llm-stack`. Rebuild base + advanced from your docs only. Re-defend the design doc cold. Then update MISSION.md: mission complete, next mission?
