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

### Phase 2 — Classic design reps (lessons 10–16, each a timed 50-min rep)
10. **API rate limiter** — token/sliding window, distributed counters, Redis. [Primer Qs]
11. **Pastebin + TinyURL** — ID generation incl. Snowflake, read-heavy caching. [Primer solutions]
12. **Twitter timeline/news feed** — fanout-on-write vs read, celebrity problem. [Primer solutions]
13. **Web crawler** — frontier, politeness, dedup, DFS/BFS at scale. [Primer solutions]
14. **Distributed KV store / query cache** — consistent hashing, LRU, replication. [Primer solutions]
15. **Distributed search, 1B docs** — inverted indexes, sharded ranking, merge — reported Anthropic prompt. [Primer Qs + real-world architectures]
16. **Scaling to millions of users on AWS** — capstone evolution rep. [Primer solutions]

### Phase 3 — ML system design patterns (lessons 17–21)
17. **ML serving patterns** — web-single, sync vs async vs batch, prep-pred split, microservice vertical/horizontal; antipatterns (online-bigsize, all-in-one). [Mercari serving, DMLS ch7]
18. **Data & training infra** — feature pipelines, data/model versioning, batch & pipeline training, param/arch search; antipatterns (training-code-in-serving, too-many-pipes). [Mercari training/operation, DMLS ch4–6]
19. **Prediction ops** — prediction cache & data cache, circuit breaker, multi-stage prediction, condition/parameter-based serving, model-in-image vs model-load. [Mercari serving/operation]
20. **ML QA in prod** — shadow A/B, online A/B, load testing, prediction logs/monitoring, drift detection; offline-only antipattern. [Mercari QA, DMLS ch8–9]
21. **Rep: recommendation engine (50M users) or fraud detection (100 ms hybrid ML+rules)**. [AISD case studies 11, 14]

### Phase 4 — LLM inference & GPU infra (lessons 22–27) ← Anthropic core
22. **Inference anatomy** — transformer forward pass at serving time, prefill vs decode, TTFT/TPOT, why decode is memory-bound. [vLLM, AISD 01/04]
23. **KV cache economics** — sizing math, quadratic recompute avoided, cache growth vs batch size, prefix caching. [vLLM, DigitalOcean KV article]
24. **Continuous batching + PagedAttention** — iteration-level scheduling, block tables, fragmentation, preemption; vLLM engine loop (schedule→step→postprocess). [vLLM]
25. **Model routing & cost** — AI gateways, fallback/rate limiting (LiteLLM-style), quantization, speculative decoding, distillation pipelines, token FinOps. [AISD 11-03/04, case study 19]
26. **THE REP: inference batching service @ 100k RPS** — full 50-min design; also token-generation service variant. [Exponent guide + everything above]
27. **Distributed training & multi-tenant fine-tuning** — data/tensor/pipeline parallelism basics, checkpointing, LoRA hot-swap platforms (280-tenant case). [AISD case study 17, DDIA batch ch]

### Phase 5 — AI application systems (lessons 28–31)
28. **RAG at production scale** — chunking, vector DBs (Pinecone/Qdrant/Milvus trade-offs), hybrid search, reranking (cross-encoder, ColBERT late-interaction), contextual retrieval, multimodal RAG, millions-of-docs scaling. [AISD 06]
29. **Agentic systems infra** — tool use/MCP, durable execution (exactly-once, replay, Temporal), memory tiers L1–L3, loop engineering & token budgets. [AISD 07/08]
30. **Multi-tenant & security** — RBAC/ABAC, tenant isolation defense-in-depth, permission-aware retrieval (2M docs case), sandboxing computer-use agents. [AISD 12, case studies 08/15/16]
31. **Evals & observability** — LLM judges, RAG eval, eval-gated CI/CD (block PRs on quality regression), monitoring/tracing. [AISD 14/18, case study 18]

### Phase 4b — additions from gap research 2026-07-22
27b. **Streaming token delivery** — SSE vs WebSockets vs gRPC streams, connection state at 100k concurrent, tokenizer-service placement/batching. [interviewing.io, vLLM]
27c. **Multi-tenant GPU scheduling** — fair-share vs priority queues, preemption, tenant isolation on shared GPUs, quota/admission control. [reported Anthropic topic]

### Phase 5b — Anthropic-specific system classes
31b. **Eval pipeline design** — large-scale model evaluation as a batch/stream system: job orchestration, result storage, judge-model fanout. [reported Anthropic prompt class]
31c. **Safety/red-teaming workflow design** — human-in-the-loop review queues, sampling strategies, escalation, audit trails. [reported Anthropic prompt class — unique to Anthropic, low coverage elsewhere]

### Phase 6 — Interview execution (lessons 32+)
32. **50-min protocol drills** — clarify → estimate → high-level → deep-dive → trade-offs; driving without guidance (Anthropic staff bar). [Exponent]
33+. **Mock rotation** through AISD 116-question bank + 9 whiteboard exercises; one case study dissection per session from the 20 worked architectures.

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

## Working notes
- Workspace strictly `system-design/`. Root-level MISSION.md/lessons/ belong to another workspace — do not touch.
- Quiz answers: equal word counts per question.
- Lesson 0001 (performance vocabulary + estimation kit) written and delivered; quiz + SLO sheet pending user completion.
- Phase 0 added 2026-07-22. Timeline impact: +3–5 weeks if taken in full; gate quizzes expected to skip 30–60% for a working AI engineer (Track B especially). Phase 0 runs BEFORE continuing Phase 1 lesson 2 — but lesson 0001 stands. Suggested order: 0.1→0.10 gates first, full lessons only where a gate fails.
