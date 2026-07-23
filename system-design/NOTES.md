# Teaching Notes

## Learner profile
- Middle AI engineer, self-described "very bad" system design knowledge → fundamentals cannot be skipped, but pace is fast and every lesson goes one level deeper than intro material.
- Wants project-based learning + an **advanced** syllabus (explicit feedback 2026-07-22 — v1 roadmap rejected as too shallow).
- Target: Anthropic interview loop (see MISSION.md). Bias examples toward LLM-serving workloads from lesson 1.

## Spine project
Design — and prototype pieces of, in this repo — an **LLM inference platform**: gateway → router → batching scheduler → model workers → KV-cache manager, with RAG and eval pipelines bolted on in later phases. Every lesson attaches to it. Endgame: whiteboard "inference batching service @ 100k RPS" cold — Anthropic's most-reported prompt.

## Curriculum roadmap v2 (advanced, source-grounded)

Sources: [Primer] = System Design Primer · [AISD] = ombharatiya/ai-system-design-guide · [Mercari] = mercari ml-system-design-pattern · [DDIA] = Kleppmann 2nd ed. · [DMLS/AIE] = Chip Huyen · [vLLM] = Anatomy of vLLM blog

### Phase 0 — Engineering & ML foundations (lessons 0.1–0.10)
Added 2026-07-22 on user request. **Diagnostic-driven:** each lesson opens with a 5-question gate quiz — pass ≥4/5 and we skip to the next, logging a learning record. User is a working AI engineer; goal is gap-fill at senior bar, not a full CS degree. High-level treatment; depth only where system design phases will lean on it.

**Track A — Programming/CS at senior bar** [TYCS = teachyourselfcs.com]
- 0.1 **Data structures for systems** — hash tables, B-trees, heaps, tries; bloom filters, consistent hashing; big-O in practice (why p99 cares about resize/rehash). [TYCS, Primer]
- 0.2 **OS essentials** — processes vs threads, virtual memory & paging (direct prerequisite for PagedAttention in lesson 24), scheduling, cgroups/containers. [TYCS: OSTEP]
- 0.3 **Concurrency** — races, locks, deadlock; async I/O & event loops; thread pools; Python GIL implications for serving code. [OSTEP, Python docs]
- 0.4 **Networking** — TCP handshakes/flow control, HTTP/1.1 vs 2 vs 3 (QUIC), TLS, sockets, connection pooling; where latency actually comes from. [TYCS: Computer Networking Top-Down]
- 0.5 **Senior code craft (high level)** — API design, idempotency, testing strategy, profiling; reading production Python/Go. [existing repo practice]

**Track B — ML/DL/NLP high level** [Karpathy = nn-zero-to-hero; CS336 = Stanford Language Modeling from Scratch]
- 0.6 **ML foundations** — supervised/unsupervised, loss functions, gradient descent, bias–variance, regularization, train/val/test discipline, metrics (precision/recall/AUC). [DMLS ch1–3]
- 0.7 **DL foundations** — backprop from scratch, optimizers (SGD→Adam), normalization, why depth works; CNN/RNN one-paragraph history. [Karpathy videos 1–4]
- 0.8 **NLP evolution** — tokenization (BPE/SentencePiece), embeddings (word2vec → contextual), seq2seq, the attention breakthrough. [Karpathy makemore/GPT videos]
- 0.9 **Transformer anatomy** — self-attention math, multi-head, positional encodings, where K/V come from (feeds KV-cache lessons directly). [Karpathy "build GPT", CS336]
- 0.10 **Modern LLM stack (high level)** — pretraining → SFT → RLHF/RLVR reasoning models, scaling laws, decoding strategies (greedy/top-p/beam), GPU architecture (memory hierarchy, tensor cores). [CS336, AISD 01/03]

**Track C — Math fundamentals (high level, ML- and systems-facing)** [3B1B = 3Blue1Brown; MML = Mathematics for Machine Learning (Deisenroth, free PDF)]
- 0.11 **Linear algebra for transformers** — vectors, dot product as similarity (this IS embeddings/attention scores), matrix multiply geometry, eigen-intuition; counting matmul FLOPs (feeds GPU math in Phase 4). [3B1B Essence of Linear Algebra, MML ch2–4]
- 0.12 **Calculus & optimization** — derivatives, chain rule (backprop IS the chain rule), gradients, convexity high level, why learning rates matter. [3B1B Essence of Calculus, MML ch5–7]
- 0.13 **Probability & statistics** — distributions, Bayes, expectation/variance, sampling; softmax as a distribution, temperature; confidence intervals & significance (feeds A/B testing in lesson 20 and eval design in 31b). [MML ch6, Coursera prob/stats]
- 0.14 **Information theory + queueing math** — entropy, cross-entropy loss, perplexity; **Little's law (L = λW)**, utilization–latency curve, why queues explode near saturation (M/M/1 intuition). The queueing half is direct interview ammo for every capacity question. [MML; napkin-math]

### Phase 1 — Distributed systems core (lessons 1–9)
1. **Performance vocabulary + estimation kit** — latency/throughput/percentiles/SLOs; latency numbers every programmer should know; powers of two. [Primer appendix, DDIA ch1]
2. **Back-of-envelope drills** — QPS/storage/bandwidth math + GPU memory math (weights, activations, KV cache sizing). [Primer, AISD 04]
3. **Traffic edge** — DNS (routing methods), CDN push/pull, load balancing L4 vs L7, reverse proxy, stateless horizontal scaling, session externalization. [Primer §7–10]
4. **CAP & replication theory** — CP vs AP, weak/eventual/strong consistency, failover active-active/passive, availability math (9s, serial vs parallel). [Primer §4–6, DDIA ch5]
5. **RDBMS scaling** — ACID; master-slave & master-master replication + lag; federation; sharding (keys, hot spots, rebalancing, cross-shard joins); denormalization; SQL tuning/indexes (B-trees). [Primer §12, DDIA ch6–7]
6. **NoSQL taxonomy** — BASE; KV/document/wide-column/graph internals (Redis, Mongo, Cassandra/Bigtable, Neo4j); SQL-vs-NoSQL decision table. [Primer §12, DDIA ch2–3]
7. **Caching deep** — cache locations (client→CDN→layer→DB); cache-aside/write-through/write-behind/refresh-ahead; invalidation, staleness, thundering herd; row vs query vs object caching. [Primer §13]
8. **Asynchronism & communication** — message vs task queues (Kafka/RabbitMQ/SQS/Celery), backpressure (503 + exponential backoff), TCP vs UDP, RPC (gRPC/Protobuf) vs REST, idempotency. [Primer §14–15]
9. **Interview OS** — the 4-step framework (use cases/constraints → high-level → core components → scale), security checklist. First timed mini-design. [Primer interview approach]

### Phase 2 — Software architecture & reliability (lessons 10–17) [ADDED 2026-07-23: broader-SWE rebalance]
10. **Monolith → microservices** — decomposition criteria, service discovery (Consul/etcd/Zookeeper), API gateway vs BFF, when microservices are the wrong answer. [Primer §11, DDIA]
11. **API design deep** — REST semantics done right, versioning, pagination (cursor vs offset), idempotency keys, webhooks; gRPC vs GraphQL vs REST decision table. [Primer §15]
12. **Storage engine internals** — B-tree vs LSM-tree (read vs write amplification), WAL, compaction; object vs block vs file storage (S3 model). [DDIA ch3]
13. **Streams & events** — Kafka model (partitions, consumer groups, offsets, log compaction), event-driven architecture, event sourcing + CQRS, exactly-once revisited. [DDIA ch11]
14. **Distributed transactions & coordination** — sagas, outbox pattern, 2PC and why it's avoided; consensus high level (Raft), leader election, distributed locks + fencing tokens. [DDIA ch8–9]
15. **Reliability patterns** — timeouts, retry budgets, circuit breakers, bulkheads, load shedding, graceful degradation, chaos engineering. [AWS Builders' Library, Release It! patterns]
16. **Observability & ops** — structured logs, metrics (RED/USE), distributed tracing, SLI/SLO/error budgets, alerting philosophy, incident response. [Google SRE book]
17. **Security & multi-tenancy** — OAuth2/OIDC/JWT, mTLS, secrets management, rate limiting as security control, tenant isolation models. [Primer §16]

### Phase 3 — Classic design reps (lessons 18–28, each a timed 50-min rep)
18. **API rate limiter** — token/sliding window, distributed counters, Redis. [Primer Qs]
19. **Pastebin + TinyURL** — ID generation incl. Snowflake, read-heavy caching. [Primer solutions]
20. **Twitter timeline/news feed** — fanout-on-write vs read, celebrity problem. [Primer solutions]
21. **Chat system (WhatsApp)** — WebSockets, presence, delivery receipts, message ordering, offline queues. [Primer Qs]
22. **File sync (Dropbox)** — chunking, dedup, delta sync, conflict resolution. [Primer Qs]
23. **Notification system + distributed scheduler** — multi-channel fanout, dedup, cron at scale. [Primer Qs]
24. **Web crawler** — frontier, politeness, dedup, DFS/BFS at scale. [Primer solutions]
25. **Distributed KV store / query cache** — consistent hashing, LRU, replication. [Primer solutions]
26. **Distributed search, 1B docs** — inverted indexes, sharded ranking, merge — reported Anthropic prompt. [Primer Qs + real-world architectures]
27. **Payment system** — idempotency, double-entry ledger, reconciliation, exactly-once money movement. [classic senior rep]
28. **Scaling to millions of users on AWS** — capstone evolution rep. [Primer solutions]

### Phase 4 — ML system design patterns (lessons 29–33)
29. **ML serving patterns** — web-single, sync vs async vs batch, prep-pred split, microservice vertical/horizontal; antipatterns (online-bigsize, all-in-one). [Mercari serving, DMLS ch7]
30. **Data & training infra** — feature pipelines, data/model versioning, batch & pipeline training, param/arch search; antipatterns (training-code-in-serving, too-many-pipes). [Mercari training/operation, DMLS ch4–6]
31. **Prediction ops** — prediction cache & data cache, circuit breaker, multi-stage prediction, condition/parameter-based serving, model-in-image vs model-load. [Mercari serving/operation]
32. **ML QA in prod** — shadow A/B, online A/B, load testing, prediction logs/monitoring, drift detection; offline-only antipattern. [Mercari QA, DMLS ch8–9]
33. **Rep: recommendation engine (50M users) or fraud detection (100 ms hybrid ML+rules)**. [AISD case studies 11, 14]

### Phase 5 — LLM inference & GPU infra (lessons 34–40) ← Anthropic core
34. **Inference anatomy** — prefill vs decode, TTFT/TPOT, why decode is memory-bound. [vLLM, AISD 01/04]
35. **KV cache economics** — sizing math, cache growth vs batch size, prefix caching. [vLLM, DigitalOcean KV article]
36. **Continuous batching + PagedAttention** — iteration-level scheduling, block tables, preemption; vLLM engine loop. [vLLM]
37. **Streaming token delivery** — SSE vs WebSockets vs gRPC streams, 100k concurrent connections, tokenizer-service placement. [interviewing.io, vLLM]
38. **Model routing & cost** — AI gateways, fallback/rate limiting, quantization, speculative decoding, distillation, token FinOps. [AISD 11-03/04, case study 19]
39. **THE REP: inference batching service @ 100k RPS** — full 50-min design; token-generation variant. [Exponent + everything above]
40. **Distributed training + multi-tenant GPU scheduling** — data/tensor/pipeline parallelism, checkpointing, LoRA hot-swap, fair-share/preemption/quotas. [AISD case study 17, reported Anthropic topic]

### Phase 6 — AI application systems (lessons 41–45)
41. **RAG at production scale** — chunking, vector DBs, hybrid search, reranking, contextual retrieval, millions-of-docs scaling. [AISD 06]
42. **Agentic systems infra** — tool use/MCP, durable execution, memory tiers, loop engineering. [AISD 07/08]
43. **Multi-tenant & security for AI** — tenant isolation defense-in-depth, permission-aware retrieval, sandboxing. [AISD 12, case studies 08/15/16]
44. **Eval pipeline design** — large-scale evaluation as batch/stream system: orchestration, result storage, judge fanout. [reported Anthropic prompt class]
45. **Safety/red-teaming workflow design** — human-in-the-loop review queues, sampling, escalation, audit trails. [reported Anthropic prompt class]

### Phase 7 — Interview execution (lessons 46+)
46. **50-min protocol drills** — clarify → estimate → high-level → deep-dive → trade-offs; driving without guidance (Anthropic staff bar). [Exponent]
47+. **Mock rotation** through AISD 116-question bank + Primer question list; one case study dissection per session.

## Mastery protocol (how the user turns coverage into skill)
1. **Lesson → quiz → project step** (this course): builds fluency.
2. **Spaced retrieval**: each session opens with 3 recall questions from 2+ lessons back (teacher generates from learning records). Builds storage strength.
3. **Written reps**: after each Phase 2+ lesson, user writes the full design solo (Excalidraw/paper, 35 min) BEFORE reading the reference solution. Compare, log deltas as learning records.
4. **Speak out loud**: from lesson 10 onward, every rep is narrated aloud — the graded skill is driving a conversation, not drawing boxes.
5. **Mocks**: minimum 2 human mock interviews before onsite (interviewing.io or peer). The single highest-leverage step per every source surveyed.
6. **Case-study diet**: 1 production case study dissection per week from AISD 16-case list (read → close → redraw from memory).

## Reported Anthropic question bank (accumulate here)
- Inference batching: single GPU, ≤100 inputs/batch, synchronous callers — receive, batch, process, route responses back to correct users (most-reported, in multiple variants)
- Token-generation service @ 100k RPS
- Distributed search over 1B documents
- Rate limiter; distributed KV store (classic warm-ups)
- LLM serving stack end-to-end; tokenizer batching; multi-tenant GPU scheduling
- Eval pipelines; AI safety / red-teaming workflows

## Full Anthropic loop map (context — this workspace covers axis 2 only)
Five stages, ~4–6 weeks: recruiter call → technical screen (coding + ML fundamentals) → onsite. AI tools prohibited in live rounds. Axes tested:
1. **Practical coding (Python)** — realistic work samples, NOT leetcode: build/debug real components under time, clean code, testing instincts. → out of scope here; separate prep track if user asks.
2. **System design** — THIS workspace.
3. **ML fundamentals (conversational)** — largely covered by Phase 0 Track B gates.
4. **Prompt engineering & model intuition** — context windows, few-shot, CoT, debugging hallucinations/refusals. Partly covered by AISD §05; user's day job helps.
5. **AI safety/alignment literacy** — RLHF, Constitutional AI, deployment risk spotting, why-safety-matters articulation. Primary sources: Anthropic's Constitutional AI paper, Core Views essay, RSP. NOT covered here; cheap to prep, high signal at this company specifically.
6. **Behavioral/values** — reported Q: "a time you did something that conflicted with your own values." Story bank needed. Not covered here.

## Preferences observed
- 2026-07-22: v1 syllabus rejected — wants advanced depth + heavy research per topic. Keep lessons short but content dense; assume fast learner.
- Project-based; prefers direct research over agent delegation (rejected subagent spawn).
- 2026-07-23: ~~Georgian version of every lesson~~ **PAUSED later same day** — user: English first, Georgian later. KA exists for 0001 (+ any agents finished before the stop order). Convention when resumed: `NNNN-<slug>.ka.html`, cross-linked kickers, tech terms English with Georgian gloss.
- 2026-07-23: **Depth over brevity (supersedes "keep lessons short")** — user asked for "full knowledge": comprehensive detailed English lessons, 7–10 sections, tables, worked examples, failure modes, closing "Interview talking points" section.
- 2026-07-23: **Broaden as SOFTWARE engineering, less AI-centric** — primary examples must be classic systems (e-commerce, social, payments, logistics); AI/LLM at most one short subsection per lesson. Roadmap restructured: new Phase 2 (software architecture & reliability, lessons 10–17), Phase 3 classic reps expanded to 11 (chat, Dropbox, notifications, payments added); AI phases moved to 4–6; interview execution now Phase 7. Total ≈ 47 lessons + Phase 0.
- 2026-07-23: **"Doing > theory" — every lesson MUST ship a practical lab.** Convention: `labs/lab-NNNN-<slug>/` with runnable stdlib-Python (or real infra later) + README of predict-edit-rerun exercises; lesson links the lab; lab deliverable = prediction-vs-observed notes, which seed learning records. Lab 0001 (measure the tail) retrofitted to lesson 0001. Phase 1 lab ideas: L2 estimation → napkin-math checker script; L3 load balancing → toy LB with health checks in front of 3 local HTTP servers; L4 replication → simulate replication lag; L5–7 → SQLite/Redis-style experiments; L8 → queue + backpressure simulation with 503s.

## ADHD accommodations (disclosed 2026-07-23 — shapes ALL future lesson/session design)
User has attention deficit. Rules:
- **Micro-blocks, not marathons**: 2h day = 4 × 25-min pomodoros with 5-min movement breaks; never design a task assuming 2h unbroken focus.
- **Lab FIRST, lesson second**: start each session by RUNNING the lab (action hooks attention), read the lesson after the first run when curiosity is primed. Reverse of the default order.
- **Minimum viable session** on bad days: 15-min recall + one quiz = chain unbroken. Never "catch up" with double sessions.
- **Fast feedback everywhere**: quizzes immediately after each section when possible; labs already predict→run→compare.
- **10-minute rule**: stuck >10 min → ask the teacher, don't grind. Grinding kills the next session too.
- **One tab, phone away, same hour daily** (habit anchor beats willpower).
- Split lesson consumption: read/lab/quiz can be separate sittings same day.
- Keep future lessons' sections SHORT even in "comprehensive" mode — depth via more sections, not longer ones.

## Diagnostics (built 2026-07-23)
Component: `assets/diagnostic.js` — per-topic verdicts appear as soon as a topic's block is complete; progress persists in localStorage; copy-paste summary for teacher. Verdicts: GAP <50% / SHAKY 50–79% / STRONG ≥80%.
- **Phase 1**: `diagnostics/phase1-diagnostic.html` — 180 Qs (20 × 9 topics), banks in `diagnostics/bank/t1..t9.js` (5 original + 15 new each; recall/scenario/numeric mix). Validated: word counts equal, answers 63/63/54, no dupes.
- **Phase 0**: `diagnostics/phase0-diagnostic.html` — 280 Qs (20 × 14 topics: a1–a5 CS, b1–b5 ML/DL/NLP, c1–c4 math), banks in `diagnostics/bank0/`. **This replaces the per-lesson gate quizzes**: STRONG topic = skipped, log a learning record; SHAKY = targeted mini-lesson on missed items; GAP = full lesson + primary source. Deep-dive links point to external canonical resources (no local Phase 0 lessons yet — author only for GAP/SHAKY topics, on demand).
Flow both phases: one topic per sitting (ADHD fit) → paste summary → teacher plans deep-dives → retake later as floor-check.

## Pace & schedule (set 2026-07-23)
User capacity: **2 h/day × 6 days = 12 h/week.** Target: full coverage in ~14 weeks (±2).
- Wk 1: Phase 0 gates (fail → lesson) · Wk 2–4: Phase 1 (lessons+labs, ~3/wk) · Wk 5–6: Phase 2 · Wk 7–9: Phase 3 reps (~4/wk) · Wk 10: Phase 4 · Wk 11–12: Phase 5 · Wk 13: Phase 6 · Wk 14+: Phase 7 drills + 2 human mocks.
- Daily shape: 15 min spaced recall (teacher fires 3 Qs from ≥2 lessons back) → 75–90 min lesson+lab (or timed rep) → 15–20 min quiz + project step + notes.
- Day 6 = review day: failed quiz items, glossary sweep, 1 case study, 15-min behaviour drill (from behaviour/ workspace, starts ~wk 8).
- Rep-day shape (Phase 3+): 10 min recall → 40 min solo timed design ALOUD → 40 min compare vs reference + deltas → 30 min next-lesson read.

## Working notes
- Workspace strictly `system-design/`. Root-level MISSION.md/lessons/ belong to another workspace — do not touch.
- Quiz answers: equal word counts per question.
- Lesson 0001 (performance vocabulary + estimation kit) written and delivered; quiz + SLO sheet pending user completion.
- Phase 0 added 2026-07-22. Timeline impact: +3–5 weeks if taken in full; gate quizzes expected to skip 30–60% for a working AI engineer (Track B especially). Phase 0 runs BEFORE continuing Phase 1 lesson 2 — but lesson 0001 stands. Suggested order: 0.1→0.10 gates first, full lessons only where a gate fails.
