var PHASE0_BANK_C3 = [
  {
    topic: 'c3',
    q: 'Two events A and B are independent exactly when:',
    options: [
      'P(A and B) equals P(A) times P(B)',
      'P(A and B) equals P(A) plus P(B)',
      'P(A or B) equals P(A) minus P(B)'
    ],
    answer: 0,
    explain: 'Independence means the joint probability factorizes into the product of the marginals, so knowing B tells you nothing about A.'
  },
  {
    topic: 'c3',
    q: 'The conditional probability P(A|B) is best read as:',
    options: [
      'probability of B occurring given A occurred',
      'probability of A occurring given B occurred',
      'probability of A and B occurring jointly'
    ],
    answer: 1,
    explain: 'P(A|B) restricts attention to the world where B happened and asks how likely A is there.'
  },
  {
    topic: 'c3',
    q: 'A disease affects 1 percent of people. A test catches 99 percent of cases but false-positives on 5 percent of healthy people. Roughly what fraction of positive tests are true cases?',
    options: [
      'about 99 percent',
      'about 17 percent',
      'about 50 percent'
    ],
    answer: 1,
    explain: 'Per 10000 people there are 99 true positives versus 495 false positives, so 99/594 is roughly 17 percent.'
  },
  {
    topic: 'c3',
    q: 'An engineer sees a 95 percent accurate alert fire and concludes there is a 95 percent chance of a real incident. What are they ignoring?',
    options: [
      'The variance of the alerting system',
      'The independence of repeated alert events',
      'The base rate of real incidents'
    ],
    answer: 2,
    explain: 'When real incidents are rare, most positives are false alarms regardless of accuracy; this is classic base-rate neglect.'
  },
  {
    topic: 'c3',
    q: 'What is the expected value of a single fair six-sided die roll?',
    options: [
      '3.5',
      '3.0',
      '4.0'
    ],
    answer: 0,
    explain: 'The average of 1 through 6 is 21/6 = 3.5, even though 3.5 itself can never be rolled.'
  },
  {
    topic: 'c3',
    q: 'Variance measures which property of a random variable?',
    options: [
      'Its most likely single outcome value',
      'Its long-run average outcome over trials',
      'Its average squared deviation from mean'
    ],
    answer: 2,
    explain: 'Variance is E[(X - mean)^2], quantifying how spread out outcomes are around the expectation.'
  },
  {
    topic: 'c3',
    q: 'Service latencies are mostly fast but show a long tail of occasional very slow requests. Which distribution models this shape best?',
    options: [
      'Normal',
      'Lognormal',
      'Uniform'
    ],
    answer: 1,
    explain: 'Latencies are positive and right-skewed with heavy tails, which a lognormal captures and a symmetric normal does not.'
  },
  {
    topic: 'c3',
    q: 'In a cache, a handful of keys receive most requests while millions of keys are rarely touched. Which distribution describes this popularity pattern?',
    options: [
      'Zipf',
      'Normal',
      'Uniform'
    ],
    answer: 0,
    explain: 'Popularity follows a Zipf power law where the k-th most popular item gets roughly 1/k of the top item traffic.'
  },
  {
    topic: 'c3',
    q: 'In a normal distribution, roughly what fraction of values fall within one standard deviation of the mean?',
    options: [
      'about 68 percent',
      'about 50 percent',
      'about 95 percent'
    ],
    answer: 0,
    explain: 'The 68-95-99.7 rule gives about 68 percent within one sigma and 95 percent within two.'
  },
  {
    topic: 'c3',
    q: 'The law of large numbers says that as sample size grows:',
    options: [
      'every individual outcome becomes easier to predict',
      'the true mean moves toward observed samples',
      'the sample average converges to true mean'
    ],
    answer: 2,
    explain: 'Averages stabilize toward the true expectation as n grows, while individual outcomes stay just as random.'
  },
  {
    topic: 'c3',
    q: 'Why does a softmax output count as a valid probability distribution?',
    options: [
      'Entries are integers and sum to one',
      'Entries are nonnegative and sum to one',
      'Entries are independent and multiply to one'
    ],
    answer: 1,
    explain: 'Exponentiation makes every entry positive and the normalizing denominator forces the entries to sum to one.'
  },
  {
    topic: 'c3',
    q: 'You raise an LLM sampling temperature from 0.7 to 1.5. What happens to the token distribution?',
    options: [
      'It flattens, making rare tokens likelier',
      'It sharpens, making top tokens dominant',
      'It collapses, keeping only one token'
    ],
    answer: 0,
    explain: 'Dividing logits by a larger temperature shrinks their differences, so softmax spreads probability mass toward unlikely tokens.'
  },
  {
    topic: 'c3',
    q: 'As temperature approaches zero, softmax sampling behaves most like:',
    options: [
      'uniform random choice over all tokens',
      'weighted sampling proportional to raw logits',
      'greedy argmax selection of top token'
    ],
    answer: 2,
    explain: 'Dividing logits by a tiny temperature exaggerates gaps until nearly all probability sits on the single highest-logit token.'
  },
  {
    topic: 'c3',
    q: 'You win 10 dollars on heads and lose 4 dollars on tails with a fair coin. What is the expected value per flip?',
    options: [
      '6 dollars',
      '3 dollars',
      '5 dollars'
    ],
    answer: 1,
    explain: 'Expected value is 0.5 * 10 + 0.5 * (-4) = 3 dollars per flip.'
  },
  {
    topic: 'c3',
    q: 'Quadrupling your sample size does roughly what to the width of a confidence interval?',
    options: [
      'Halves it',
      'Quarters it',
      'Doubles it'
    ],
    answer: 0,
    explain: 'Interval width shrinks with the square root of n, so four times the data buys only half the width.'
  },
  {
    topic: 'c3',
    q: 'A 95 percent confidence interval is best understood as saying:',
    options: [
      '95 percent of data points fall inside it',
      'repeated intervals would cover the truth 95 percent',
      'the true parameter is random within the interval'
    ],
    answer: 1,
    explain: 'The 95 percent describes the long-run coverage of the interval-building procedure, not the data spread or a random parameter.'
  },
  {
    topic: 'c3',
    q: 'A PM checks the A/B test dashboard daily and stops the experiment the moment p drops below 0.05. What is the problem?',
    options: [
      'Daily checks reduce the sample size',
      'Stopping early guarantees a false negative',
      'Repeated peeking inflates false positive rates'
    ],
    answer: 2,
    explain: 'Each peek is another chance for noise to cross the threshold, so the real false positive rate climbs far above 5 percent.'
  },
  {
    topic: 'c3',
    q: 'A p-value of 0.03 is best described as:',
    options: [
      'the chance of such extreme data assuming null holds',
      'the chance the null hypothesis itself is actually true',
      'the chance the experiment result will replicate again later'
    ],
    answer: 0,
    explain: 'A p-value conditions on the null being true and measures how surprising the observed data would be under it.'
  },
  {
    topic: 'c3',
    q: 'An A/B test shows a 2 percent conversion lift with only 50 users per arm. What is the right takeaway?',
    options: [
      'The lift is real; ship the variant',
      'The sample is too small to conclude',
      'The control group must have been biased'
    ],
    answer: 1,
    explain: 'With 50 users per arm the noise dwarfs a 2 percent effect, so the observed lift is statistically meaningless.'
  },
  {
    topic: 'c3',
    q: 'A fair coin lands heads twice in a row. What is the probability the next flip is heads?',
    options: [
      '0.25',
      '0.75',
      '0.50'
    ],
    answer: 2,
    explain: 'Independent flips have no memory, so past heads do not change the next flip probability at all.'
  }
];
