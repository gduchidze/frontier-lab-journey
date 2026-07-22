# System Design Resources

## Knowledge

- [Book: _Designing Data-Intensive Applications_, 2nd ed. — Kleppmann & Riccomini (2026)](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/)
  The canonical distributed-systems text; 2nd edition updated Feb 2026 with AI/ML and cloud-native content. Use for: replication, partitioning, consistency, transactions, percentiles/tail latency.
- [Repo: System Design Primer — Donne Martin](https://github.com/donnemartin/system-design-primer)
  Most community-validated free resource (~330k stars). Use for: quick topic overviews, back-of-envelope numbers, practice problem index.
- [Book: _AI Engineering_ — Chip Huyen (2025)](https://github.com/chiphuyen/aie-book)
  Most-read O'Reilly book of 2025; systems side of building on foundation models. Use for: inference optimization, evals, RAG architecture, latency metrics (TTFT/TPOT).
- [Book: _Designing Machine Learning Systems_ — Chip Huyen (2022)](https://github.com/chiphuyen/dmls-book)
  Stanford CS 329S in book form. Use for: ML pipelines, feature/training infra, monitoring, data distribution shift.
- [Article: "Inside vLLM: Anatomy of a High-Throughput LLM Inference System" — vLLM blog (2025)](https://blog.vllm.ai/2025/09/05/anatomy-of-vllm.html)
  Primary source on how a real inference engine works. Use for: continuous batching, PagedAttention, scheduler design — directly maps to Anthropic's most-reported prompt.
- [Guide: Anthropic System Design Interview (2026) — Exponent](https://www.tryexponent.com/blog/anthropic-system-design-interview)
  Interview-format intel. Use for: round structure (50–55 min, conversation-driven), reported question bank, evaluation bar.
- [Article: "How KV Caching Slashes LLM Inference Costs at Scale" — DigitalOcean](https://www.digitalocean.com/community/conceptual-articles/how-kv-caching-slashes-llm-inference-costs-at-scale)
  Accessible KV-cache explainer with cost framing. Use for: first pass on KV cache before reading the vLLM anatomy post.
- [Repo: AI System Design Guide — ombharatiya](https://github.com/ombharatiya/ai-system-design-guide)
  User-supplied. 19-section AI-infra curriculum: RAG, agents, inference optimization, gateways, evals, security, plus 116 interview questions, 9 whiteboard exercises, and 20 production case studies (current to June 2026). Use for: Phases 4–6 — question bank, case-study dissections, AI-gateway/FinOps/eval topics.
- [Site: ML System Design Pattern — Mercari](https://mercari.github.io/ml-system-design-pattern/)
  User-supplied. Named pattern catalog for ML serving/training/QA/operations (sync/async/batch serving, prediction cache, circuit breaker, shadow A/B, model-in-image vs model-load) including antipatterns. Use for: Phase 3 — the vocabulary for ML-serving architecture answers.

- [Video series: Essence of Linear Algebra / Essence of Calculus — 3Blue1Brown](https://www.3blue1brown.com/)
  The canonical visual-intuition series. Use for: Phase 0 lessons 0.11–0.12 — watch before reading anything symbolic.
- [Book: _Mathematics for Machine Learning_ — Deisenroth, Faisal, Ong (free PDF)](https://mml-book.github.io/book/mml-book.pdf)
  Cambridge UP, legally free ([site](https://mml-book.com/)). Use for: Phase 0 Track C reference — linear algebra ch2–4, calculus ch5, probability ch6.
- [Curriculum: Teach Yourself Computer Science — Bradfield](https://teachyourselfcs.com/)
  The canonical self-study CS map (OSTEP for OS, Top-Down for networking, etc.). Use for: Phase 0 Track A — pick the single recommended book per gap, ignore the rest.
- [Course: Neural Networks: Zero to Hero — Andrej Karpathy](https://karpathy.ai/zero-to-hero.html)
  Backprop → GPT built from scratch in code ([repo](https://github.com/karpathy/nn-zero-to-hero)). Use for: Phase 0 Track B lessons 0.7–0.9 — the fastest trusted route to transformer intuition.
- [Course: CS336 Language Modeling from Scratch — Stanford](https://cs336.stanford.edu/)
  Full LLM pipeline: data, transformer construction, training, eval, deployment. Use for: Phase 0 lesson 0.10 and as deep-dive backup for Phase 4 systems lessons.
- [Blog: Engineering at Anthropic](https://www.anthropic.com/engineering)
  Primary source — written by the people who will interview you. Key posts: [Building Effective AI Agents](https://www.anthropic.com/engineering/building-effective-agents) (routing, tool design, workflow vs agent trade-offs), agent SDK internals, eval-infrastructure noise. Use for: Phase 5 — and for speaking Anthropic's own vocabulary (workflows vs agents, simple-first composition) in the interview.
- [Repo: napkin-math — sirupsen](https://github.com/sirupsen/napkin-math)
  Estimation drill deck by a Shopify principal engineer: costs, throughputs, and practice problems. Use for: lesson 2 back-of-envelope drills beyond the Primer's static table.
- [Guide: A Senior Engineer's Guide to the System Design Interview — interviewing.io](https://interviewing.io/guides/system-design-interview)
  Free, written by real interviewers; the best treatment of *how to drive the conversation* at senior/staff bar. Use for: Phase 6 execution skills, communication calibration.
- [Guide: Anthropic System Design Interviews — IGotAnOffer](https://igotanoffer.com/en/advice/anthropic-system-design-interview)
  Aggregated candidate reports. Use for: question-bank refresh, confirming the mix of classic + ML-inference prompts (rate limiter, KV store, LLM serving stack, tokenizer batching, multi-tenant GPU scheduling).

## Wisdom (Communities)

- [r/ExperiencedDevs](https://reddit.com/r/ExperiencedDevs)
  High-signal, moderated. Use for: real interview debriefs, architecture discussion sanity checks.
- [vLLM GitHub Discussions](https://github.com/vllm-project/vllm/discussions)
  Practitioners running production inference. Use for: testing understanding of batching/KV-cache trade-offs against real deployments.
- Mock interviews with peers (Pramp-style or colleague trades)
  Use for: practicing driving the 50-minute conversation — the skill Anthropic actually grades.

## Gaps

- Distributed search at billion-doc scale: Primer's query-cache solution + real-world architecture papers (Bigtable, GFS) partially cover it; still want one dedicated inverted-index-at-scale writeup before lesson 15.
- No mock-interview partner identified yet.
