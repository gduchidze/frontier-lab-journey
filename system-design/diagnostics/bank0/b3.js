var PHASE0_BANK_B3 = [
  {
    topic: 'b3',
    q: 'In BPE training, what operation is repeated to build the vocabulary?',
    options: [
      'Merge the most frequent adjacent symbol pair into one token',
      'Split the least frequent word into individual characters each iteration',
      'Delete the rarest token from vocabulary until size target reached'
    ],
    answer: 0,
    explain: 'BPE repeatedly merges the most frequent adjacent symbol pair, adding one new token per merge until the vocab budget is reached.'
  },
  {
    topic: 'b3',
    q: 'What distinguishes SentencePiece from a classic BPE pipeline that assumes pre-split words?',
    options: [
      'It only supports pure character vocabularies and never merges pairs',
      'It works on raw text, treating whitespace as a symbol',
      'It requires language-specific word tokenizers before any subword training runs'
    ],
    answer: 1,
    explain: 'SentencePiece trains directly on raw text and encodes whitespace as an ordinary symbol, so it needs no language-specific pre-tokenization.'
  },
  {
    topic: 'b3',
    q: 'In word2vec skip-gram training, what does the model learn to predict?',
    options: [
      'The next sentence given the whole current sentence',
      'A center word given its averaged context words',
      'Surrounding context words given a single center word'
    ],
    answer: 2,
    explain: 'Skip-gram trains a center word to predict each of its surrounding context words, which is what shapes the similarity geometry.'
  },
  {
    topic: 'b3',
    q: 'Why did additive attention (Bahdanau 2014) improve over vanilla seq2seq translation?',
    options: [
      'The decoder could look at all encoder states, weighted per output step',
      'It removed recurrence entirely, so the training parallelized across every sequence position',
      'It compressed the source sentence into a smaller, more efficient fixed vector'
    ],
    answer: 0,
    explain: 'Attention lets the decoder form a fresh weighted mix of all encoder states at each step instead of relying on one fixed vector.'
  },
  {
    topic: 'b3',
    q: 'What is the core difference between static and contextual word embeddings?',
    options: [
      'Static embeddings are trained on labels; contextual embeddings are fully unsupervised',
      'Static assigns one vector per word; contextual varies with surrounding text',
      'Static embeddings are always smaller; contextual embeddings always use more dimensions'
    ],
    answer: 1,
    explain: 'Word2vec-style models give each word type a single fixed vector, while contextual models produce a different vector per occurrence.'
  },
  {
    topic: 'b3',
    q: 'The famous king minus man plus woman result illustrates what property of word2vec spaces?',
    options: [
      'Vectors store exact dictionary definitions retrievable through arithmetic subtraction',
      'Consistent semantic relationships become roughly linear directions in space',
      'Every word pair maintains identical cosine distance after training'
    ],
    answer: 1,
    explain: 'Analogy arithmetic works because relations like gender or capital-of tend to correspond to roughly consistent vector offsets.'
  },
  {
    topic: 'b3',
    q: 'What fundamental assumption limits the expressive power of an n-gram language model?',
    options: [
      'Each word is always sampled independently of every other word',
      'Probabilities must always be estimated with neural networks over characters',
      'The next word depends only on a fixed-length recent window'
    ],
    answer: 2,
    explain: 'An n-gram model conditions only on the previous n-1 words, so any dependency longer than the window is invisible to it.'
  },
  {
    topic: 'b3',
    q: 'An LLM confidently miscounts occurrences of the letter r in strawberry. What is the most likely root cause?',
    options: [
      'The model sees subword tokens, so individual characters are never observed',
      'The attention heads of models simply cannot attend inside short words',
      'Counting always requires recurrence, and transformer architectures removed recurrence from modeling'
    ],
    answer: 0,
    explain: 'Strawberry arrives as one or two subword tokens, so the model never directly observes the letters it is asked to count.'
  },
  {
    topic: 'b3',
    q: 'A model multiplies small numbers fine but fails on 8-digit numbers. Which tokenizer property contributes most?',
    options: [
      'Large numbers exceed the context window, so digits get truncated',
      'Multiplication tokens were explicitly filtered from the pretraining data corpus',
      'Long numbers split into inconsistent multi-digit chunks, breaking digit alignment'
    ],
    answer: 2,
    explain: 'BPE chunks digits into irregular groups, so the same digit sequence tokenizes differently in different numbers and column alignment is lost.'
  },
  {
    topic: 'b3',
    q: 'You raise your tokenizer vocab from 32k to 256k. Which trade-off should you expect?',
    options: [
      'Sequences get longer, but every token now trains much faster',
      'Sequences shorten, but embedding parameters grow and rare tokens undertrain',
      'Sequences stay identical, but memory usage falls across all layers'
    ],
    answer: 1,
    explain: 'A larger vocab compresses text into fewer tokens but inflates the embedding and output matrices and leaves tail tokens undertrained.'
  },
  {
    topic: 'b3',
    q: 'An English-trained BPE tokenizer processes Georgian text. What happens to serving cost and quality?',
    options: [
      'Words fragment into many tiny tokens, inflating sequence length and API cost',
      'The tokenizer rejects all unknown scripts, so Georgian text is silently dropped',
      'Georgian compresses better than English text because rarer scripts get longer merges'
    ],
    answer: 0,
    explain: 'Byte-level fallback keeps the text representable, but out-of-distribution scripts shatter into many tokens, multiplying length and cost.'
  },
  {
    topic: 'b3',
    q: 'For which task would static word2vec-style embeddings likely suffice over contextual ones?',
    options: [
      'Keyword clustering for tag suggestions on short product titles',
      'Disambiguating polysemous words across long legal contracts and filings',
      'Resolving pronoun references across paragraphs in a novel chapter'
    ],
    answer: 0,
    explain: 'Short titles carry little disambiguating context anyway, so cheap static vectors capture the needed similarity signal.'
  },
  {
    topic: 'b3',
    q: 'A word2vec search system confuses river bank with financial bank documents. Why?',
    options: [
      'The training corpus lacked financial documents, so bank was unseen',
      'Static embeddings collapse every sense of bank into one vector',
      'Cosine similarity cannot compare vectors that come from different documents'
    ],
    answer: 1,
    explain: 'One vector must average all senses of bank, so both meanings land in the same neighborhood of the space.'
  },
  {
    topic: 'b3',
    q: 'A vanilla seq2seq translator handles short sentences well but degrades sharply on long ones. Why?',
    options: [
      'Longer sentences contain rarer words, which encoder-decoder models cannot embed',
      'The decoder vocabulary is capped, so long outputs get truncated',
      'The whole source must squeeze into one fixed-size context vector'
    ],
    answer: 2,
    explain: 'Without attention, the encoder must compress arbitrarily long sentences into one fixed-size vector, which saturates as length grows.'
  },
  {
    topic: 'b3',
    q: 'A trigram model assigns zero probability to a perfectly grammatical unseen phrase. What is this problem called?',
    options: [
      'Overfitting caused by excessive model capacity',
      'Sparsity, since most n-grams never appear',
      'Vanishing gradients across long recurrent sequences'
    ],
    answer: 1,
    explain: 'Most grammatical n-grams never occur in any finite corpus, so counts are zero and smoothing or backoff is required.'
  },
  {
    topic: 'b3',
    q: 'GPT-4 struggles to reverse the string lollipop. Karpathy attributes this mainly to what?',
    options: [
      'The word is one token, hiding its character-level internal structure',
      'Reversal requires right-to-left attention, which causal decoder masks strictly forbid',
      'String reversal never appears anywhere in any web training data'
    ],
    answer: 0,
    explain: 'Karpathy notes lollipop maps to very few tokens, so the model has no direct access to the character sequence to reverse.'
  },
  {
    topic: 'b3',
    q: 'A model has vocab 50,000 and embedding dimension 768. How many parameters does the token embedding matrix hold?',
    options: [
      'About 3.84 million',
      'About 384 million',
      'About 38.4 million'
    ],
    answer: 2,
    explain: 'The embedding matrix is vocab times dimension, and 50,000 x 768 equals 38.4 million parameters.'
  },
  {
    topic: 'b3',
    q: 'For typical English text with a GPT-style tokenizer, roughly how many tokens per word?',
    options: [
      'About 4.0 tokens',
      'About 1.3 tokens',
      'About 0.3 tokens'
    ],
    answer: 1,
    explain: 'English averages roughly 0.75 words per token with GPT-style BPE, which is about 1.3 tokens per word.'
  },
  {
    topic: 'b3',
    q: 'A language model reports perplexity 20 on a test set. What does that number mean intuitively?',
    options: [
      'On average it is as uncertain as choosing among 20 equally likely options',
      'It predicts the correct next token exactly 20 percent of the time overall',
      'It makes on average 20 wrong token predictions for every single correct one'
    ],
    answer: 0,
    explain: 'Perplexity is the exponentiated average negative log-likelihood, interpretable as the effective branching factor of the model uncertainty.'
  },
  {
    topic: 'b3',
    q: 'With a vocabulary of 10,000 words, how many possible trigrams must a trigram model potentially estimate?',
    options: [
      '10 to the eighth',
      '10 to the sixth',
      '10 to the twelfth'
    ],
    answer: 2,
    explain: 'A trigram table ranges over V cubed contexts, and 10,000 cubed is 10 to the twelfth, which is why sparsity is fatal.'
  }
];
