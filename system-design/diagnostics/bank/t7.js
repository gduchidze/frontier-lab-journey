// Phase 1 question bank - t7 · Caching patterns & failure modes
// 20 questions: 5 reused verbatim from phase1-questions.js + 15 new,
// grounded in lessons/0007-caching-deep.html.
var PHASE1_BANK_T7 = [

  // ---- Reused verbatim from phase1-questions.js ----
  { topic: 't7', q: "In cache-aside, what happens on a cache miss?",
    options: ["The cache fetches the value from database",
              "The application loads from database then caches",
              "The request fails until the cache warms"],
    answer: 1, explain: "Cache-aside puts the application in charge: check cache → miss → read DB → write cache → return. Three trips on a miss." },

  { topic: 't7', q: "Which write pattern risks losing data on cache node failure?",
    options: ["Write behind buffering writes before database persistence",
              "Write through persisting synchronously to the database",
              "Cache aside writing directly to the database"],
    answer: 0, explain: "Write-behind acknowledges before the DB write happens; a crash in that window loses acknowledged data." },

  { topic: 't7', q: "A hot key expires and 500 concurrent requests hammer the database. Name and fix?",
    options: ["Cache penetration, fixed by negative caching entries",
              "Hot partition, fixed by adding more shards",
              "Cache stampede, fixed by per-key request locking"],
    answer: 2, explain: "Stampede/dogpile: one waiter rebuilds the entry while the rest wait. TTL jitter and refresh-ahead also help." },

  { topic: 't7', q: "Repeated lookups of nonexistent keys always miss cache. Standard fix?",
    options: ["Cache the miss itself with short TTL",
              "Increase cache capacity until misses stop occurring",
              "Route nonexistent keys to a separate database"],
    answer: 0, explain: "Negative caching stores 'not found' briefly, absorbing the penetration pattern (often malicious or buggy clients)." },

  { topic: 't7', q: "Why does doubling cache size rarely double the hit rate?",
    options: ["Eviction algorithms slow down with larger caches",
              "Zipf skew concentrates hits in few keys",
              "Bigger caches suffer proportionally many more misses"],
    answer: 1, explain: "The head of the popularity curve is already cached; extra capacity buys only the long, cold tail. Diminishing returns." },

  // ---- New: recall ----
  { topic: 't7', q: "Which update pattern acknowledges a write only after cache and database are both updated synchronously?",
    options: ["Write through, writing both stores synchronously",
              "Write behind, flushing to database later",
              "Refresh ahead, renewing entries before expiry"],
    answer: 0, explain: "Write-through pays slower writes so the cache is never stale versus the database (DynamoDB DAX is the textbook example)." },

  { topic: 't7', q: "Which policy is a freshness bound on staleness rather than a space-management policy?",
    options: ["LRU recency-based eviction",
              "LFU frequency-based eviction",
              "TTL clock-based expiry"],
    answer: 2, explain: "TTL bounds how stale an entry can get; LRU/LFU decide what to throw out when space runs out, so real systems compose them." },

  { topic: 't7', q: "Walking the cache ladder top to bottom, which layer saves ~150 ms ocean crossings by serving content near users?",
    options: ["Reverse proxy at your own edge",
              "CDN nodes placed near the users",
              "Browser cache on the client device"],
    answer: 1, explain: "The CDN caches at the geographic edge, so requests never cross an ocean; the reverse proxy still sits in your own datacenter." },

  { topic: 't7', q: "What is the main cost of the refresh-ahead pattern?",
    options: ["Wasted load when predictions are wrong",
              "Data loss when cache nodes crash",
              "Slower writes paying both stores synchronously"],
    answer: 0, explain: "Refresh-ahead re-fetches entries before expiry, so a wrong prediction adds load for data nobody reads; data loss is write-behind's risk." },

  { topic: 't7', q: "Which caching granularity does the lesson call the workhorse, invalidating precisely at the cost of more round trips?",
    options: ["Full page caching of rendered responses",
              "Query caching keyed on raw strings",
              "Object caching keyed per domain object"],
    answer: 2, explain: "One key per domain object (user:8123, product:4711) invalidates precisely; batched multi-gets claw back the extra round trips." },

  // ---- New: scenario ----
  { topic: 't7', q: "After a deploy, thousands of keys get identical TTLs and all expire in the same instant, spiking the database fleet-wide. Name and fix?",
    options: ["Cache penetration, screened by a Bloom filter",
              "Hot-key overload, replicated with random key suffixes",
              "Cache avalanche, decorrelated with random TTL jitter"],
    answer: 2, explain: "This is cache avalanche, the fleet-wide stampede variant; jitter does not reduce total reloads, it decorrelates them in time." },

  { topic: 't7', q: "A viral post's key needs 1M ops/s but a single cache shard serves ~100k ops/s. What is the standard fix?",
    options: ["Cache the miss with short TTLs",
              "Replicate the key across suffixed copies",
              "Serialize all reads behind per-key locks"],
    answer: 1, explain: "Hot-key overload needs more than one home: append a small random suffix (post:99:{0..9}) and fan reads across the copies, as Netflix's EVCache does." },

  { topic: 't7', q: "A 90% read / 10% write workload on hot keys wants the highest read hit rate and accepts slower writes. Which pattern?",
    options: ["Write through keeping hot keys warm",
              "Write behind acknowledging before database persistence",
              "Cache aside evicting hot keys constantly"],
    answer: 0, explain: "Cache-aside invalidation evicts a hot key on every write and the next reader re-buys it; write-through keeps those keys warm (~75% vs ~68% in the lab)." },

  { topic: 't7', q: "A like-counter pipeline must absorb huge write bursts and can tolerate losing a few increments in a crash. Which pattern fits?",
    options: ["Write through, persisting every increment synchronously",
              "Write behind, batching asynchronous database flushes",
              "Refresh ahead, renewing counters before expiry"],
    answer: 1, explain: "Write-behind absorbs write bursts and batches DB I/O; its data-loss window is acceptable for like counters, never for balances." },

  { topic: 't7', q: "Prices may be up to 60 s stale while browsing, but checkout must never charge a stale price. What does the lesson recommend?",
    options: ["Use event driven invalidation on every page",
              "Shorten all browse TTLs until staleness disappears",
              "Tolerate staleness browsing; bypass cache at checkout"],
    answer: 2, explain: "Consistency budgets differ within one product: TTL-and-tolerate on the browse path, re-read the database on the money path." },

  { topic: 't7', q: "TTL jitter does not reduce the total number of cache reloads. What does it actually buy you?",
    options: ["It halves recompute cost per expiration",
              "It decorrelates expiries, spreading load spikes",
              "It guarantees one loader per key"],
    answer: 1, explain: "Jitter randomizes expiry times so hot keys never expire in the same instant; only per-key locking guarantees a single loader." },

  { topic: 't7', q: "Sessions must be shared across many stateless app servers. Where on the caching ladder do they belong?",
    options: ["Browser cache, controlled via HTTP headers",
              "App-layer cache like Redis or Memcached",
              "Database buffer pool, sized mostly automatically"],
    answer: 1, explain: "Sessions are per-user, so they are not shareable CDN content; the app-layer cache is exactly where the lesson's ladder puts objects and sessions." },

  // ---- New: numeric ----
  { topic: 't7', q: "A key serving 1,000 RPS expires and its recompute takes 200 ms. Roughly how many identical concurrent DB queries pile up?",
    options: ["Around 200 queries, a self-inflicted spike",
              "Around 1,000 queries, matching request rate",
              "Around 20 queries, quickly absorbed anyway"],
    answer: 0, explain: "1,000 RPS x 0.2 s of recompute window accumulates ~200 concurrent identical queries -- a 200x spike on your hottest data at peak traffic." },

  { topic: 't7', q: "A cache fronts 100,000 reads/s at a 99% hit rate. How many reads per second reach the database?",
    options: ["About 1,000 reads reach the database",
              "About 10,000 reads reach the database",
              "About 100 reads reach the database"],
    answer: 0, explain: "Only the 1% misses fall through: 100,000 x 0.01 = 1,000 reads/s, which is why hit rate is a capacity number as much as a latency number." },

  { topic: 't7', q: "Hits cost 0.5 ms and misses cost 8 ms. At a 90% hit rate, what is the effective read latency?",
    options: ["Roughly 4.25 ms per average read",
              "Roughly 0.75 ms per average read",
              "Roughly 1.25 ms per average read"],
    answer: 2, explain: "Effective latency = 0.9 x 0.5 + 0.1 x 8 = 1.25 ms -- the 5,000x memory-versus-network cliff is what makes each hit so cheap." }
];
