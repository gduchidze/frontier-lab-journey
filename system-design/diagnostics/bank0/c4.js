var PHASE0_BANK_C4 = [
  {
    topic: 'c4',
    q: 'What is the entropy of a single fair coin flip?',
    options: ['Exactly 1 bit', 'Exactly 2 bits', 'Exactly 0.5 bits'],
    answer: 0,
    explain: 'A fair coin has two equally likely outcomes, so H = log2(2) = 1 bit of average surprise per flip.'
  },
  {
    topic: 'c4',
    q: 'A coin lands heads 90 percent of the time. How does its entropy compare to a fair coin?',
    options: ['Higher, outcomes more surprising', 'Lower, outcomes more predictable', 'Equal, both involve randomness'],
    answer: 1,
    explain: 'Skewing probability toward one outcome makes results more predictable, so the biased coin has less entropy than the fair coin maximum of 1 bit.'
  },
  {
    topic: 'c4',
    q: 'In information theory, what does the entropy of a distribution measure?',
    options: ['The total number of possible distinct outcomes', 'The average surprise, in bits, per outcome', 'The maximum probability assigned to any outcome'],
    answer: 1,
    explain: 'Entropy is the expected surprise of a draw, equivalently the average number of bits needed to encode outcomes optimally.'
  },
  {
    topic: 'c4',
    q: 'Why does minimizing cross-entropy loss make a language model a good next-token predictor?',
    options: ['It forces every token to get equal probability mass', 'It shrinks the vocabulary until few choices remain possible', 'It rewards assigning high probability to actual observed tokens'],
    answer: 2,
    explain: 'Cross-entropy is minimized when the model puts probability mass on the tokens that really occur, which is exactly what good prediction means.'
  },
  {
    topic: 'c4',
    q: 'How do cross-entropy H(p,q) and entropy H(p) relate for a fixed true distribution p?',
    options: ['Cross-entropy equals entropy plus the KL divergence term', 'Cross-entropy is always strictly smaller than the entropy', 'Cross-entropy and entropy are always exactly equal quantities'],
    answer: 0,
    explain: 'H(p,q) = H(p) + KL(p||q), so cross-entropy exceeds entropy by exactly the divergence between the true and model distributions.'
  },
  {
    topic: 'c4',
    q: 'What does KL divergence KL(p||q) intuitively measure?',
    options: ['A symmetric geometric distance between the two distributions', 'The raw sample count needed to distinguish them', 'Extra bits paid when modeling p using q'],
    answer: 2,
    explain: 'KL(p||q) is the average extra bits wasted by encoding data from p with a code built for q, and it is not symmetric.'
  },
  {
    topic: 'c4',
    q: 'A language model reports perplexity 20 on a test set. What does that mean intuitively?',
    options: ['It predicts exactly 20 tokens correctly per generated sentence', 'It hesitates as if choosing uniformly among 20 options', 'Its vocabulary is effectively limited to 20 distinct tokens'],
    answer: 1,
    explain: 'Perplexity = exp(cross-entropy) is an effective branching factor: the model is on average as uncertain as a uniform pick among 20 tokens.'
  },
  {
    topic: 'c4',
    q: 'Training reduces a model perplexity from 40 to 20. What actually improved?',
    options: ['Its effective branching factor per token halved from 40', 'Its raw accuracy exactly doubled on every evaluation token', 'Its cross-entropy loss dropped by exactly one half nat'],
    answer: 0,
    explain: 'Halving perplexity means the model is now as uncertain as choosing among 20 options instead of 40, a cross-entropy drop of ln(2) nats, not a doubling of accuracy.'
  },
  {
    topic: 'c4',
    q: 'What is the entropy of a uniform distribution over 8 equally likely outcomes?',
    options: ['3 bits', '8 bits', '64 bits'],
    answer: 0,
    explain: 'For a uniform distribution over n outcomes entropy is log2(n), and log2(8) = 3 bits.'
  },
  {
    topic: 'c4',
    q: 'During LM training the cross-entropy loss steadily falls. What is happening under the hood?',
    options: ['The model is memorizing token frequencies and ignoring context', 'The vocabulary is shrinking so predictions get automatically easier', 'The model assigns growing probability to each true token'],
    answer: 2,
    explain: 'Falling cross-entropy means the model is putting more probability on the tokens that actually appear next, i.e. becoming a better predictor.'
  },
  {
    topic: 'c4',
    q: 'A service handles 100 requests per second and each request spends 0.2 seconds in the system. What is the average number of requests in flight?',
    options: ['10', '20', '500'],
    answer: 1,
    explain: 'Little\'s law gives L = lambda x W = 100 x 0.2 = 20 requests in the system on average.'
  },
  {
    topic: 'c4',
    q: 'A system averages 50 in-flight requests while sustaining 200 requests per second. What is the average time each request spends in the system?',
    options: ['250 milliseconds', '400 milliseconds', '100 milliseconds'],
    answer: 0,
    explain: 'Rearranging Little\'s law, W = L / lambda = 50 / 200 = 0.25 seconds, or 250 milliseconds.'
  },
  {
    topic: 'c4',
    q: 'An M/M/1 server processes 100 requests per second and arrivals average 90 per second. Roughly what is the average time in system?',
    options: ['10 milliseconds', '11 milliseconds', '100 milliseconds'],
    answer: 2,
    explain: 'For M/M/1, W = 1 / (mu - lambda) = 1 / (100 - 90) = 0.1 seconds, ten times the bare 10 ms service time.'
  },
  {
    topic: 'c4',
    q: 'Why does average wait time explode as utilization pushes past 90 percent?',
    options: ['Servers physically slow down when running near full load', 'Little slack remains, so bursts pile into growing queues', 'Network bandwidth saturates long before the CPUs ever do'],
    answer: 1,
    explain: 'Wait scales like 1 / (1 - utilization), so near saturation there is almost no spare capacity to drain bursts and queues balloon.'
  },
  {
    topic: 'c4',
    q: 'An M/M/1 system runs at mu 100 and lambda 90, waiting about 100 ms. Capacity doubles to mu 200. What is the new approximate wait?',
    options: ['9 milliseconds', '50 milliseconds', '45 milliseconds'],
    answer: 0,
    explain: 'W = 1 / (200 - 90) = 1/110 of a second, about 9 ms; doubling capacity cut wait by over 10x, not merely in half.'
  },
  {
    topic: 'c4',
    q: 'Why is queue depth a better early warning signal than latency percentiles?',
    options: ['Queue depth is far cheaper to compute continuously', 'Latency percentiles are statistically meaningless under heavy load', 'Depth grows the moment arrivals outpace service rate'],
    answer: 2,
    explain: 'Queue depth rises the instant demand exceeds capacity, while percentile latency dashboards lag until enough slow requests have already completed.'
  },
  {
    topic: 'c4',
    q: 'In capacity planning terms, what does overprovisioning headroom actually buy you?',
    options: ['Higher utilization of every server you own', 'Low queueing delay when traffic bursts arrive', 'Guaranteed zero downtime during any hardware failure'],
    answer: 1,
    explain: 'Headroom keeps utilization on the flat part of the utilization-latency curve, so bursts are absorbed instead of queued; you are paying money for latency.'
  },
  {
    topic: 'c4',
    q: 'A service at 95 percent utilization shows fine median latency but a terrible p99. Why?',
    options: ['Tail requests hit bursts where queueing delay dominates service', 'The p99 metric always misbehaves regardless of system load', 'Garbage collection pauses only ever affect the slowest percentile'],
    answer: 0,
    explain: 'Near saturation most requests still sail through, but the unlucky ones arriving during bursts wait behind long queues, blowing up the tail.'
  },
  {
    topic: 'c4',
    q: 'You need 500 requests per second of throughput and each request takes 100 milliseconds. What is the minimum number of concurrent workers?',
    options: ['5', '50', '500'],
    answer: 1,
    explain: 'By Little\'s law the required concurrency is L = lambda x W = 500 x 0.1 = 50 workers busy at once.'
  },
  {
    topic: 'c4',
    q: 'Which queue-depth alerting condition best signals real saturation?',
    options: ['Any single momentary spike above the average', 'Queue depth briefly exceeding one during bursts', 'Sustained growth showing arrivals persistently outpacing service'],
    answer: 2,
    explain: 'Transient spikes are normal burst absorption; a queue that keeps growing means arrival rate exceeds service rate and the system is saturated.'
  }
];
