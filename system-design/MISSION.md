# Mission: System Design for Anthropic AI Engineer Interviews

## Why
The user's real goal (stated 2026-07-22): become a frontier-lab-level AI engineer — the caliber hired by Anthropic, OpenAI, DeepMind. The Anthropic interview loop is the milestone that proves it. This workspace attacks the weakest pillar first: system design, because frontier-lab design rounds are infrastructure problems framed around AI workloads (e.g. "design an inference batching service at 100k RPS") and the user starts from weak fundamentals. Other pillars (elite practical coding, ML depth, research literacy, safety literacy) are tracked in MISSION.md's parent plan but live in future workspaces.

## Success looks like
- Can do back-of-envelope estimation (QPS, storage, bandwidth, GPU memory) in under 5 minutes for any prompt
- Can explain and correctly apply: load balancing, caching, replication, partitioning, queues, consistency trade-offs
- Can design classic systems cold: rate limiter, URL shortener, news feed, distributed search
- Can design AI-infra systems cold: LLM inference service (continuous batching, KV cache, PagedAttention), RAG at scale, training-data pipeline
- Can drive a 50-minute mock interview end-to-end: clarify → estimate → high-level design → deep dive → trade-offs

## Constraints
- Project-based learning preferred — concepts must attach to things built or designed, not just read
- Learner is a working engineer; lessons must be short and completable quickly
- Workspace confined to `system-design/` directory

## Out of scope
- Coding interview prep (algorithms/data structures)
- Frontend system design
- Deep ML theory (training math, architectures) — only the systems side of ML
