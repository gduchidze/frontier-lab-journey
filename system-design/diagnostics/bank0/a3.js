var PHASE0_BANK_A3 = [
  {
    topic: 'a3',
    q: 'What distinguishes a data race from a general race condition?',
    options: [
      'Unsynchronized concurrent access to shared memory where at least one access is a write',
      'Any timing-dependent ordering bug where outcome varies, even when every memory access is locked',
      'Two threads acquiring the exact same mutex simultaneously, causing corruption inside the critical section'
    ],
    answer: 0,
    explain: 'A data race is specifically unsynchronized memory access with at least one write; race conditions are the broader timing-dependence class.'
  },
  {
    topic: 'a3',
    q: 'Which is NOT one of the four necessary conditions for deadlock?',
    options: [
      'Circular wait among the competing threads',
      'Priority inversion between the competing threads',
      'Hold and wait while requesting more'
    ],
    answer: 1,
    explain: 'The four conditions are mutual exclusion, hold-and-wait, no preemption, and circular wait; priority inversion is a different pathology.'
  },
  {
    topic: 'a3',
    q: 'Thread A locks accounts[1] then accounts[2]; thread B locks accounts[2] then accounts[1]. Occasionally both hang forever. What is the cleanest fix?',
    options: [
      'Add a small sleep before the second acquisition so both threads rarely ever collide',
      'Wrap every account operation in one try/except and retry whenever any lock acquisition fails',
      'Impose a global lock ordering, always acquiring the lower account id before the higher'
    ],
    answer: 2,
    explain: 'Consistent global lock ordering breaks the circular-wait condition, which deterministically prevents this deadlock.'
  },
  {
    topic: 'a3',
    q: 'Two threads repeatedly detect contention, back off, retry, and collide again forever while consuming CPU. This is best described as what?',
    options: [
      'Deadlock',
      'Livelock',
      'Starvation'
    ],
    answer: 1,
    explain: 'Livelock means threads stay active and keep changing state but make no forward progress, unlike blocked deadlocked threads.'
  },
  {
    topic: 'a3',
    q: 'A Python service must fan out 500 concurrent HTTP calls to slow upstream APIs, each mostly waiting on the network. Which approach fits best?',
    options: [
      'Use asyncio with a single event loop, since waiting connections are cheap coroutines',
      'Use multiprocessing with 500 worker processes, since parallel requests need truly separate interpreters',
      'Use one dedicated thread per request, since Python threads bypass network waits entirely'
    ],
    answer: 0,
    explain: 'I/O-bound high-concurrency fan-out is exactly what asyncio is for; 500 processes waste memory and 500 threads add scheduler overhead.'
  },
  {
    topic: 'a3',
    q: 'A CPU-bound Python function takes 100ms of pure computation. You run 4 copies on 4 threads in CPython. Roughly how long until all finish?',
    options: [
      'About 100ms total',
      'About 200ms total',
      'About 400ms total'
    ],
    answer: 2,
    explain: 'The GIL lets only one thread execute Python bytecode at a time, so CPU-bound threads serialize to roughly 4 x 100ms.'
  },
  {
    topic: 'a3',
    q: 'An asyncio web app becomes unresponsive for all clients whenever one endpoint resizes a large image inline. Why?',
    options: [
      "The image bytes overflow the loop's internal buffer, forcing every pending socket closed",
      'CPU-bound work inside a coroutine blocks the single-threaded loop, so nothing else runs',
      'The GIL forces asyncio to pause every coroutine whenever any image library loads'
    ],
    answer: 1,
    explain: 'The event loop is cooperative and single-threaded; long synchronous CPU work starves every other task until it yields.'
  },
  {
    topic: 'a3',
    q: "Why is 'counter += 1' unsafe under concurrency even though it is one line of code?",
    options: [
      'It compiles to separate read, modify, write steps that can interleave between threads',
      'It allocates a new integer object, which the garbage collector may free early',
      'It only fails on multicore machines because single-core CPUs never interleave any instructions'
    ],
    answer: 0,
    explain: 'Increment is a read-modify-write sequence, not an atomic operation, so a context switch mid-sequence loses updates.'
  },
  {
    topic: 'a3',
    q: "Two web workers both run: 'if not user_exists(email): create_user(email)'. Occasionally duplicate users appear. What is the root cause?",
    options: [
      'The database driver silently retries failed inserts, so one request creates two rows',
      'The email comparison is case sensitive, so equal addresses hash into different buckets',
      'The check and insert are not atomic, so both requests pass the check'
    ],
    answer: 2,
    explain: 'This is a classic check-then-act (TOCTOU) race; fix it with a unique constraint or atomic upsert, not application-level checking.'
  },
  {
    topic: 'a3',
    q: 'A Python service must hash, compress, and transform large payloads, saturating all CPU cores. Which concurrency model actually delivers parallel speedup in CPython?',
    options: [
      'A multiprocessing pool, because separate processes each hold their own GIL and interpreter',
      'A large thread pool, because threads share memory and thus avoid serialization overhead',
      'An asyncio TaskGroup, because coroutines schedule compute across cores without any operating threads'
    ],
    answer: 0,
    explain: 'CPU-bound Python work needs multiple processes to escape the GIL; threads and coroutines still execute bytecode one at a time.'
  },
  {
    topic: 'a3',
    q: 'A low-priority thread never gets the lock because higher-priority threads keep winning it, while the system overall keeps progressing. What is this called?',
    options: [
      'Deadlock',
      'Starvation',
      'Livelock'
    ],
    answer: 1,
    explain: 'Starvation is indefinite denial of a resource to one thread under contention while the system as a whole makes progress.'
  },
  {
    topic: 'a3',
    q: 'A service handles requests that spend 200ms blocked on a downstream call. You need 400 requests/second throughput. Ignoring CPU time, roughly how many concurrent workers?',
    options: [
      'About 8 workers',
      'About 20 workers',
      'About 80 workers'
    ],
    answer: 2,
    explain: "Little's law: concurrency = throughput x latency = 400/s x 0.2s = 80 in-flight requests, so about 80 workers."
  },
  {
    topic: 'a3',
    q: 'Tasks spend 10ms on CPU and 90ms waiting on I/O. On an 8-core machine, what thread pool size roughly keeps all cores busy?',
    options: [
      'Exactly 8 threads',
      'Around 16 threads',
      'Around 80 threads'
    ],
    answer: 2,
    explain: 'Size roughly cores x (1 + wait/compute) = 8 x (1 + 90/10) = 80 threads to keep cores saturated.'
  },
  {
    topic: 'a3',
    q: 'Why do Python threads still speed up I/O-bound workloads despite the GIL?',
    options: [
      'The GIL is released during blocking system calls, letting other threads run meanwhile',
      'The GIL only applies to threads created before the interpreter finishes its startup',
      'The operating system automatically promotes waiting threads into separate processes with independent GILs'
    ],
    answer: 0,
    explain: 'CPython releases the GIL around blocking I/O, so threads overlap waits even though bytecode execution stays serialized.'
  },
  {
    topic: 'a3',
    q: 'A payment webhook is delivered at-least-once and sometimes arrives twice, double-charging customers. What is the standard fix?',
    options: [
      'Ask the provider to switch delivery to exactly-once mode, which eliminates duplicates upstream',
      'Make the handler idempotent by recording processed event ids and skipping already-seen ones',
      'Add a randomized delay before processing so duplicate deliveries land in different seconds'
    ],
    answer: 1,
    explain: 'Exactly-once delivery is not achievable over unreliable networks; idempotent handlers keyed on event id make retries safe.'
  },
  {
    topic: 'a3',
    q: 'Inside an asyncio handler you must call a legacy blocking database driver taking 50ms per query. What keeps the loop responsive?',
    options: [
      'Run the blocking call in an executor thread pool via loop.run_in_executor or to_thread',
      'Mark the driver function as async so awaiting it yields control back automatically',
      'Call time.sleep(0) right before the query so the event loop processes other tasks'
    ],
    answer: 0,
    explain: 'Wrapping a sync function in async does not make it non-blocking; offload it to a thread pool so the loop keeps scheduling.'
  },
  {
    topic: 'a3',
    q: 'Which strategy directly breaks the hold-and-wait condition for deadlock prevention?',
    options: [
      'Grant every thread a strictly increasing priority whenever it requests any additional lock',
      'Require each thread to acquire all needed locks atomically upfront or acquire none',
      'Let the scheduler forcibly kill any thread that holds one lock too long'
    ],
    answer: 1,
    explain: 'Acquiring all locks at once (or releasing everything and retrying) means no thread holds one lock while waiting for another.'
  },
  {
    topic: 'a3',
    q: 'A service keeps a 4GB in-memory read-only model and serves I/O-heavy requests with occasional brief CPU work. Why do threads beat fork-per-worker processes here?',
    options: [
      'Threads each receive their own private copy-on-write snapshot, keeping memory usage below processes',
      'Threads let the GIL parallelize the brief CPU bursts across every available core',
      "Threads share the model's address space, avoiding per-worker copies and costly serialization overhead"
    ],
    answer: 2,
    explain: 'Threads share one heap, so a large read-only structure exists once; processes would copy or serialize it per worker.'
  },
  {
    topic: 'a3',
    q: 'A CPython service spends 5ms holding the GIL on CPU and 95ms in I/O per request per thread. Roughly how many threads before the GIL caps throughput?',
    options: [
      'About 5 threads',
      'About 20 threads',
      'About 95 threads'
    ],
    answer: 1,
    explain: 'Each thread needs the GIL about 5 percent of the time, so around 100/5 = 20 threads saturate the single GIL-held core.'
  },
  {
    topic: 'a3',
    q: 'What does a mutex actually guarantee when correctly used around a critical section?',
    options: [
      'Mutual exclusion: at most one thread executes the protected section at any moment',
      'Fair ordering: threads always enter the protected section in their exact arrival order',
      'Deadlock freedom: any program using only correct mutexes can never permanently block itself'
    ],
    answer: 0,
    explain: 'A mutex guarantees exclusion only; fairness is unspecified in most implementations and deadlock remains possible with multiple locks.'
  }
];
