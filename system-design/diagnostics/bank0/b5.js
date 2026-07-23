var PHASE0_BANK_B5 = [
  {
    topic: 'b5',
    q: 'In the modern LLM training pipeline, what is the standard ordering of stages?',
    options: [
      'Pretraining, then supervised fine-tuning, then preference-based RLHF alignment',
      'RLHF alignment, then pretraining, then supervised fine-tuning afterwards',
      'Supervised fine-tuning, then pretraining, then reward-model based RLHF'
    ],
    answer: 0,
    explain: 'Models are first pretrained on next-token prediction, then SFT teaches instruction following, then RLHF aligns outputs with human preferences.'
  },
  {
    topic: 'b5',
    q: 'What objective drives the pretraining stage of a modern LLM?',
    options: [
      'Predicting human preference scores between responses',
      'Predicting the next token over text',
      'Classifying documents into curated quality tiers'
    ],
    answer: 1,
    explain: 'Pretraining is next-token prediction at massive scale, typically over trillions of tokens of web-scale text.'
  },
  {
    topic: 'b5',
    q: 'Why does RLHF train a separate reward model instead of asking humans to score every RL sample?',
    options: [
      'Reward models eliminate the need for any human labels',
      'Reward models make the policy gradient exactly unbiased always',
      'Human labeling cannot scale to millions of RL samples'
    ],
    answer: 2,
    explain: 'A reward model learned from a limited set of human preference comparisons provides cheap scalable feedback for millions of RL rollouts.'
  },
  {
    topic: 'b5',
    q: 'What distinguishes RLVR, used for training reasoning models, from classic RLHF?',
    options: [
      'Rewards come from automatically checkable correctness signals',
      'Rewards come from a learned human-preference model',
      'Rewards come from larger pretraining data quantities'
    ],
    answer: 0,
    explain: 'RLVR uses verifiable rewards like unit tests or exact math answers, which resist reward hacking and suit reasoning domains.'
  },
  {
    topic: 'b5',
    q: 'According to the Chinchilla result, how should you spend a fixed training compute budget?',
    options: [
      'Make the model as large as compute allows',
      'Scale parameters and training tokens up roughly together',
      'Keep parameters fixed and only add more data'
    ],
    answer: 1,
    explain: 'Chinchilla showed compute-optimal training scales parameters and tokens proportionally, roughly twenty tokens per parameter.'
  },
  {
    topic: 'b5',
    q: 'You are building an API that extracts structured JSON from invoices and must return identical output for identical input. Which decoding setup fits?',
    options: [
      'Greedy decoding with temperature effectively at zero',
      'Top-p sampling with temperature set to 1.2',
      'Beam search with high temperature random restarts'
    ],
    answer: 0,
    explain: 'Deterministic extraction wants greedy or temperature-zero decoding so the argmax token is always chosen.'
  },
  {
    topic: 'b5',
    q: 'A creative-writing assistant produces bland, repetitive stories under greedy decoding. What change most directly helps?',
    options: [
      'Lower the temperature until outputs become fully deterministic',
      'Switch to beam search with a wider beam',
      'Sample with top-p and a higher temperature setting'
    ],
    answer: 2,
    explain: 'Greedy and beam search both favor high-probability bland text; nucleus sampling with higher temperature restores diversity.'
  },
  {
    topic: 'b5',
    q: 'A chatbot keeps looping the same phrase mid-response. Which decoding-level explanation is most plausible?',
    options: [
      'The context window overflowed and truncated the system prompt',
      'Low-temperature greedy-like decoding fell into a repetition loop attractor',
      'The KV cache ran out of GPU memory capacity'
    ],
    answer: 1,
    explain: 'Near-greedy decoding can lock into high-probability repetition loops; adding sampling or repetition penalties breaks them.'
  },
  {
    topic: 'b5',
    q: 'You lower temperature from 1.0 to 0.2. What happens to the output token distribution?',
    options: [
      'It flattens out, spreading probability toward rarer tokens',
      'It sharpens, concentrating probability on top tokens heavily',
      'It stays unchanged because temperature only affects training'
    ],
    answer: 1,
    explain: 'Dividing logits by a temperature below one sharpens the softmax, concentrating mass on the most likely tokens.'
  },
  {
    topic: 'b5',
    q: 'Roughly how does KV-cache memory for one sequence grow as you extend the context during decoding?',
    options: [
      'Linearly with the number of tokens',
      'Quadratically with the number of tokens',
      'Constant regardless of the sequence length'
    ],
    answer: 0,
    explain: 'The KV cache stores keys and values per token per layer, so memory grows linearly while attention compute is what grows quadratically.'
  },
  {
    topic: 'b5',
    q: 'A 14 GB model runs single-stream decoding on a GPU with 1400 GB/s memory bandwidth. Roughly what tokens-per-second ceiling does bandwidth imply?',
    options: [
      'Around 10 tokens per second',
      'Around 1000 tokens per second',
      'Around 100 tokens per second'
    ],
    answer: 2,
    explain: 'Each decoded token streams all 14 GB of weights from HBM, so 1400 divided by 14 gives roughly 100 tokens per second.'
  },
  {
    topic: 'b5',
    q: 'You double a prompt from 4k to 8k tokens. Roughly how does self-attention compute for the prefill change?',
    options: [
      'It grows about four times',
      'It grows about two times',
      'It stays essentially the same'
    ],
    answer: 0,
    explain: 'Full self-attention compares every token with every other token, so compute scales quadratically and doubling length quadruples it.'
  },
  {
    topic: 'b5',
    q: 'Decoding at batch size 1 leaves your GPU compute units mostly idle. What is happening and what helps?',
    options: [
      'Compute bound; use a smaller model to reduce FLOPs needed',
      'Memory-bandwidth bound; batch more requests to reuse each weight load',
      'Latency bound; raise the clock speed of the GPU cores'
    ],
    answer: 1,
    explain: 'Small-batch decoding is bandwidth bound on weight loads; batching amortizes each load across many tokens, shifting toward compute bound.'
  },
  {
    topic: 'b5',
    q: 'How do HBM and on-chip SRAM differ on a modern GPU?',
    options: [
      'SRAM is larger but slower; HBM is small and fast',
      'HBM and SRAM are equally fast but differently priced tiers',
      'HBM is large but slower; SRAM is tiny and fast'
    ],
    answer: 2,
    explain: 'GPUs pair tens of gigabytes of relatively slow HBM with megabytes of very fast on-chip SRAM, which kernels like FlashAttention exploit.'
  },
  {
    topic: 'b5',
    q: 'What are tensor cores on modern NVIDIA GPUs specialized for?',
    options: [
      'Scheduling threads across streaming multiprocessors efficiently',
      'Dense low-precision matrix multiply accumulate operations',
      'Moving data quickly between HBM tiers'
    ],
    answer: 1,
    explain: 'Tensor cores execute small matrix multiply-accumulates in low precision, providing most of a GPU usable FLOPs for transformers.'
  },
  {
    topic: 'b5',
    q: 'Your assistant must answer questions about internal docs that change daily and must cite sources. Which approach fits best?',
    options: [
      'RAG retrieving fresh documents into the prompt',
      'Full fine-tuning on a snapshot of docs',
      'LoRA fine-tuning repeated weekly on document dumps'
    ],
    answer: 0,
    explain: 'Fast-changing knowledge with citation requirements favors retrieval; fine-tuning bakes in stale facts and cannot cite sources.'
  },
  {
    topic: 'b5',
    q: 'You need the model to consistently follow a strict proprietary output style, you have one small GPU, and knowledge freshness is irrelevant. What do you pick?',
    options: [
      'Full fine-tuning of all parameters',
      'RAG over a style guide',
      'LoRA adapters on the model'
    ],
    answer: 2,
    explain: 'Style and format behavior is exactly what fine-tuning teaches well, and LoRA delivers it within small GPU memory budgets.'
  },
  {
    topic: 'b5',
    q: 'How does LoRA reduce the cost of fine-tuning a large model?',
    options: [
      'It quantizes all weights to four bits during training updates',
      'It trains small low-rank matrices while freezing the original weights',
      'It prunes unimportant layers so fewer parameters need gradient computation'
    ],
    answer: 1,
    explain: 'LoRA freezes base weights and learns low-rank update matrices, cutting trainable parameters and optimizer memory dramatically.'
  },
  {
    topic: 'b5',
    q: 'A team wants a slightly friendlier tone from a strong hosted model and has no training data. What should they try first?',
    options: [
      'Prompt engineering with a system prompt',
      'Collect preferences and run RLHF training',
      'LoRA fine-tune an open weights model'
    ],
    answer: 0,
    explain: 'Prompting is the cheapest and fastest lever; escalate to fine-tuning only when prompting demonstrably fails.'
  },
  {
    topic: 'b5',
    q: 'Beam search shines in machine translation but often hurts open-ended chat. Why?',
    options: [
      'Beam search cannot run efficiently on modern GPU tensor cores',
      'Beam search ignores the probabilities the model assigns to tokens',
      'Likelihood maximization suits constrained outputs but yields degenerate open-ended text'
    ],
    answer: 2,
    explain: 'Beam search optimizes sequence likelihood, which works when one right answer exists but produces bland repetitive text in open-ended generation.'
  }
];
