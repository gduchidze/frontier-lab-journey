var PHASE0_BANK_B4 = [
  {
    topic: 'b4',
    q: 'In self-attention, what does the Q (query) projection produce for each token?',
    options: [
      'A query vector used to score other positions',
      'A value vector that stores content for output',
      'A gating vector that filters the MLP activations'
    ],
    answer: 0,
    explain: 'W_Q maps each token\'s hidden state to a query that is dotted against keys to score relevance.'
  },
  {
    topic: 'b4',
    q: 'Why are the raw QK^T scores divided by sqrt(head_dim) before the softmax?',
    options: [
      'To make attention weights sum exactly to one',
      'To keep dot-product variance controlled before the softmax',
      'To reduce memory used by the score matrix'
    ],
    answer: 1,
    explain: 'Without scaling, dot products grow with head_dim and saturate the softmax, killing gradients.'
  },
  {
    topic: 'b4',
    q: 'The softmax over attention scores is normalized across which dimension?',
    options: [
      'Across the head dimension for each key',
      'Across the batch dimension for each query',
      'Across the key positions for each query'
    ],
    answer: 2,
    explain: 'Each query row becomes a probability distribution over all key positions it may attend to.'
  },
  {
    topic: 'b4',
    q: 'What breaks if a decoder is trained without the causal mask?',
    options: [
      'Tokens attend to future targets, leaking the answer',
      'Gradients vanish because attention scores become too small',
      'Positional encodings collide because indices repeat every layer'
    ],
    answer: 0,
    explain: 'Without masking, each position can read the very token it must predict, making training trivial and inference useless.'
  },
  {
    topic: 'b4',
    q: 'Why does multi-head attention use several heads instead of one full-width head?',
    options: [
      'More heads always increase total parameters per layer',
      'Heads attend to different patterns in parallel subspaces',
      'Heads reduce the quadratic attention cost to linear'
    ],
    answer: 1,
    explain: 'Splitting d_model into head_dim = d_model / heads keeps parameter count the same while letting heads specialize.'
  },
  {
    topic: 'b4',
    q: 'A model has d_model = 4096 and 32 attention heads. What is head_dim?',
    options: [
      'It equals 32',
      'It equals 256',
      'It equals 128'
    ],
    answer: 2,
    explain: 'head_dim = d_model / num_heads = 4096 / 32 = 128.'
  },
  {
    topic: 'b4',
    q: 'During autoregressive decode, which tensors actually grow as the context gets longer?',
    options: [
      'The MLP weight matrices grow as more tokens arrive',
      'The cached key and value tensors grow per token',
      'The token embedding table grows as more tokens arrive'
    ],
    answer: 1,
    explain: 'All weights are fixed; only the KV cache gains one K and one V entry per layer per new token.'
  },
  {
    topic: 'b4',
    q: 'Why does caching K and V make autoregressive decoding much cheaper?',
    options: [
      'Past keys and values never change, so recomputing them wastes work',
      'Queries for past tokens are needed at every new decode step',
      'Softmax outputs get stored, so attention weights never need any recomputation'
    ],
    answer: 0,
    explain: 'K and V for a token depend only on that token\'s hidden state, so under causal masking they are reusable forever.'
  },
  {
    topic: 'b4',
    q: 'For a given token, where do its K and V vectors come from?',
    options: [
      'From attention scores computed at the previous layer',
      'From the positional encoding added after each block',
      'From linear projections of that token\'s hidden state'
    ],
    answer: 2,
    explain: 'K = W_K x and V = W_V x are per-token linear maps of the same hidden state that produced Q.'
  },
  {
    topic: 'b4',
    q: 'What goes wrong if you remove positional encodings from a transformer entirely?',
    options: [
      'The residual stream stops carrying gradients backward properly',
      'Attention becomes permutation invariant, so word order vanishes',
      'The softmax saturates because scores become too large'
    ],
    answer: 1,
    explain: 'Self-attention is a set operation; without injected position information the model cannot distinguish token order.'
  },
  {
    topic: 'b4',
    q: 'What distinguishes RoPE from learned absolute position embeddings?',
    options: [
      'RoPE rotates Q and K, encoding relative offsets',
      'RoPE adds trained vectors directly to token embeddings',
      'RoPE removes any need for the causal mask'
    ],
    answer: 0,
    explain: 'RoPE applies position-dependent rotations to queries and keys so attention scores depend on relative distance.'
  },
  {
    topic: 'b4',
    q: 'In a pre-norm transformer block (GPT-2 style), where does layer norm sit?',
    options: [
      'After the residual addition at each block output',
      'Only once, applied after the final decoder layer',
      'Before each sublayer, inside the residual branch input'
    ],
    answer: 2,
    explain: 'Pre-norm normalizes the input to the attention and MLP sublayers, which stabilizes training of deep stacks.'
  },
  {
    topic: 'b4',
    q: 'What do residual connections primarily provide in a deep transformer stack?',
    options: [
      'They halve computation by skipping alternate transformer layers',
      'They give gradients an identity path through depth',
      'They store activations so backward passes save memory'
    ],
    answer: 1,
    explain: 'Each block learns a refinement added to the stream while gradients flow unimpeded through the skip path.'
  },
  {
    topic: 'b4',
    q: 'What is the role of the MLP (feed-forward) block in a transformer layer?',
    options: [
      'Per-token nonlinear transformation that mixes no positions',
      'Cross-token mixing replacing attention in alternate layers',
      'Learned normalization applied across the batch dimension'
    ],
    answer: 0,
    explain: 'The MLP processes each position independently, typically expanding to 4x d_model and projecting back down.'
  },
  {
    topic: 'b4',
    q: 'Doubling the context length n multiplies the attention score matrix memory by what factor?',
    options: [
      'By 2x',
      'By 8x',
      'By 4x'
    ],
    answer: 2,
    explain: 'The score matrix is n x n per head, so its memory grows quadratically with sequence length.'
  },
  {
    topic: 'b4',
    q: 'A model has 32 layers, d_model = 4096, fp16 cache. How many KV cache bytes per token?',
    options: [
      '512 KiB',
      '256 KiB',
      '128 KiB'
    ],
    answer: 0,
    explain: '2 tensors (K and V) x 4096 dims x 2 bytes x 32 layers = 524288 bytes = 512 KiB per token.'
  },
  {
    topic: 'b4',
    q: 'Quadrupling sequence length n multiplies the QK^T score computation FLOPs by what factor?',
    options: [
      'By 4x',
      'By 16x',
      'By 64x'
    ],
    answer: 1,
    explain: 'Score FLOPs scale as n^2 in sequence length, so 4x the length costs 16x the compute.'
  },
  {
    topic: 'b4',
    q: 'In a standard block with 4x MLP expansion, which part holds the most parameters?',
    options: [
      'The attention projections, roughly 4 d_model squared',
      'The layer norms, roughly 2 d_model each',
      'The MLP weights, roughly 8 d_model squared'
    ],
    answer: 2,
    explain: 'The MLP up and down projections total about 8 d_model^2 versus about 4 d_model^2 for attention QKVO.'
  },
  {
    topic: 'b4',
    q: 'With a KV cache in place, each decode step computes attention using what?',
    options: [
      'One new query against all cached keys',
      'All past queries against one cached key',
      'One new query against one newest key'
    ],
    answer: 0,
    explain: 'Only the newest token\'s Q is formed each step, and it attends over every cached K and V.'
  },
  {
    topic: 'b4',
    q: 'What role does the V (value) projection play in the attention output?',
    options: [
      'V decides which positions each query attends to',
      'V carries the content that attention weights combine',
      'V rescales scores before the softmax normalization step'
    ],
    answer: 1,
    explain: 'The output is a weighted sum of value vectors; Q and K set the weights, V supplies the content.'
  }
];
