var PHASE0_BANK_A5 = [
  {
    topic: 'a5',
    q: 'A public REST API needs a breaking change to a response field. What is the standard way to ship it?',
    options: [
      'Release a new API version and migrate consumers gradually',
      'Change the field in place and notify consumers afterward',
      'Add the change behind a header only some use'
    ],
    answer: 0,
    explain: 'Breaking changes go into a new version so existing consumers keep working while they migrate on their own schedule.'
  },
  {
    topic: 'a5',
    q: 'A payments client sometimes retries a POST /charges call after a network timeout. What prevents double charging?',
    options: [
      'Rate limit the endpoint so retries get rejected quickly',
      'Require an idempotency key so retries return the original',
      'Switch the endpoint to PUT so retries are safe'
    ],
    answer: 1,
    explain: 'An idempotency key lets the server recognize a retry and return the first result instead of charging again.'
  },
  {
    topic: 'a5',
    q: 'Which pagination approach stays stable when rows are inserted or deleted while a client pages through results?',
    options: [
      'Offset pagination, because page numbers are always deterministic',
      'Random sampling, because ordering no longer matters anymore',
      'Cursor pagination, because it keys off stable positions'
    ],
    answer: 2,
    explain: 'Cursors anchor to a stable sort key, so concurrent inserts and deletes do not shift or duplicate pages the way offsets do.'
  },
  {
    topic: 'a5',
    q: 'A client sends a well-formed request for an order that does not exist. Which status code should the API return?',
    options: [
      '404, since the requested resource cannot be found',
      '500, since the lookup failed inside the server',
      '200, with an error message inside the body'
    ],
    answer: 0,
    explain: 'A missing resource is a client-addressable condition, so 404 is correct; 500 means server fault and 200-with-error hides failures from tooling.'
  },
  {
    topic: 'a5',
    q: 'You want to add a new optional field to a JSON response consumed by many teams. What should you check first?',
    options: [
      'Whether the field name follows internal naming conventions',
      'Whether any consumer\'s parser rejects unknown extra fields',
      'Whether the field needs a brand new endpoint'
    ],
    answer: 1,
    explain: 'Additive fields are usually safe, but a strict deserializer that fails on unknown fields turns an additive change into a breaking one.'
  },
  {
    topic: 'a5',
    q: 'In the testing pyramid, why are unit tests placed at the wide base rather than end-to-end tests?',
    options: [
      'They are fast, cheap, and pinpoint failures precisely',
      'They exercise the full stack more realistically overall',
      'They are required before code review can happen'
    ],
    answer: 0,
    explain: 'Unit tests run in milliseconds and localize failures, so you can afford many of them; slower, broader tests belong higher up in smaller numbers.'
  },
  {
    topic: 'a5',
    q: 'An integration test fails roughly once in twenty CI runs and passes on retry. What is the senior move?',
    options: [
      'Add automatic retries so the pipeline stays green',
      'Delete the test because flaky tests erode trust',
      'Quarantine it, then diagnose the underlying race condition'
    ],
    answer: 2,
    explain: 'Retries and deletion both bury the signal; quarantining keeps CI trustworthy while you hunt down the real nondeterminism.'
  },
  {
    topic: 'a5',
    q: 'You are unit testing business logic that calls a third-party payment gateway. What should you mock?',
    options: [
      'Nothing, because real calls give the truest signal',
      'The gateway boundary, keeping your own logic real',
      'Everything, including your own domain objects and helpers'
    ],
    answer: 1,
    explain: 'Mock at the external boundary you do not own; over-mocking your own code couples tests to implementation details.'
  },
  {
    topic: 'a5',
    q: 'A team\'s suite is 80 percent end-to-end tests and CI takes 90 minutes. What should they do?',
    options: [
      'Push most coverage down into unit and integration layers',
      'Buy faster CI machines so the suite finishes sooner',
      'Run end-to-end tests nightly and remove the rest entirely'
    ],
    answer: 0,
    explain: 'An inverted pyramid is the root cause; moving coverage to cheaper layers fixes both speed and flakiness rather than masking them with hardware.'
  },
  {
    topic: 'a5',
    q: 'A request handler shows 900 ms wall time but only 40 ms CPU time. What does that indicate?',
    options: [
      'The handler is CPU bound and needs algorithmic optimization',
      'The handler mostly waits on I/O or downstream calls',
      'The profiler is broken and the numbers are meaningless'
    ],
    answer: 1,
    explain: 'A large wall-to-CPU gap means time is spent waiting, not computing, so look at I/O, locks, and downstream latency.'
  },
  {
    topic: 'a5',
    q: 'Average latency is fine but users complain about slowness. Which measurement most likely reveals their experience?',
    options: [
      'Mean latency computed over a full day window',
      'Total throughput measured during the peak traffic hour',
      'Tail percentiles like p99 broken down per endpoint'
    ],
    answer: 2,
    explain: 'Averages hide the slow tail; p99 per endpoint exposes the worst experiences that real users actually feel and report.'
  },
  {
    topic: 'a5',
    q: 'A teammate wants to rewrite a helper in a faster language because it \'feels slow\'. What do you ask for first?',
    options: [
      'A profile showing the helper actually dominates runtime',
      'A benchmark of the new language\'s raw speed',
      'A design document describing the proposed rewrite plan'
    ],
    answer: 0,
    explain: 'Measure before optimizing; if the helper is not a real hotspot, the rewrite buys risk without any user-visible benefit.'
  },
  {
    topic: 'a5',
    q: 'During review you find a SQL query built by string concatenation from user input. How do you treat it?',
    options: [
      'Nitpick: suggest cleanup in a future refactoring pass',
      'Blocker: injection risk must be fixed before merge',
      'Comment: approve now and file a tracking ticket'
    ],
    answer: 1,
    explain: 'SQL injection is a security vulnerability, and security defects are exactly the class of finding that blocks a merge.'
  },
  {
    topic: 'a5',
    q: 'A correct, tested PR uses a variable naming style you personally dislike but the codebase allows. What do you do?',
    options: [
      'Request changes until the names match your preference',
      'Block merge and escalate to the style committee',
      'Approve it, optionally leaving a non-blocking style note'
    ],
    answer: 2,
    explain: 'Personal preference is not a merge blocker; reserve blocking for correctness, security, and maintainability problems.'
  },
  {
    topic: 'a5',
    q: 'Why do production services prefer structured logs over free-form text log lines?',
    options: [
      'Machines can query fields without brittle regex parsing',
      'Structured logs compress better and save storage costs',
      'Free-form text cannot capture stack traces at all'
    ],
    answer: 0,
    explain: 'Key-value fields make logs queryable and aggregatable by tooling, which free-form strings only support through fragile parsing.'
  },
  {
    topic: 'a5',
    q: 'A caught exception is logged as just \'operation failed\'. What context should a senior insist on adding?',
    options: [
      'The full request body including any user credentials',
      'Identifiers, parameters, and the original error, minus secrets',
      'A stack trace only, since messages rarely help'
    ],
    answer: 1,
    explain: 'Useful error logs carry correlating identifiers, relevant inputs, and the wrapped cause, while still keeping secrets out.'
  },
  {
    topic: 'a5',
    q: 'You must ship a risky change to a checkout flow used by millions. How do you deploy it?',
    options: [
      'Deploy at 3 AM when traffic is lowest',
      'Deploy fully but keep the old code commented',
      'Behind a flag, ramping gradually while watching metrics'
    ],
    answer: 2,
    explain: 'A feature flag with a gradual ramp limits blast radius and gives you an instant kill switch that redeployment cannot match.'
  },
  {
    topic: 'a5',
    q: 'During a canary rollout, error rate on canary pods hits 2 percent versus 0.1 percent on baseline. What happens next?',
    options: [
      'Roll back the canary and investigate before proceeding',
      'Continue the rollout since 2 percent is small',
      'Restart the canary pods and watch it again'
    ],
    answer: 0,
    explain: 'A 20x error-rate regression against baseline is exactly the signal canaries exist to catch; halt and diagnose before wider exposure.'
  },
  {
    topic: 'a5',
    q: 'Your API rejects requests during a downstream outage. Which response best helps well-behaved clients recover?',
    options: [
      '401 so clients re-authenticate and try once more',
      '503 plus a Retry-After header signaling backoff timing',
      '200 with a body explaining the temporary failure'
    ],
    answer: 1,
    explain: 'A 503 with Retry-After tells clients the failure is temporary and when to back off, enabling correct automated retry behavior.'
  },
  {
    topic: 'a5',
    q: 'A refactor makes a long-standing unit test fail, though manual checks say the feature works. What first?',
    options: [
      'Update the test\'s assertions to match new output',
      'Skip the test temporarily and ship the refactor',
      'Determine whether the test or refactor encodes intent'
    ],
    answer: 2,
    explain: 'First decide whether the test documents required behavior or an implementation detail; blindly updating or skipping can erase a real regression.'
  }
];
