# Lab p0-08 — Build BPE

Companion to [Lesson p0-08](../../lessons/p0-08-nlp-evolution.html). You will train a real byte-pair-encoding tokenizer from scratch — the same algorithm (minus optimizations) behind GPT-2's and Llama's tokenizers — and measure every claim the lesson makes. Rule of the lab: **predict before you run.** Write your prediction down; the gap between prediction and output is where the learning is.

```bash
python3 bpe_lab.py
```

Four experiments: (1) train BPE on a paragraph and watch the merges it learns, (2) lossless encode/decode round trip on text the trainer never saw, (3) characters vs words vs BPE on the same text, (4) the vocab-size vs sequence-length trade — plus what happens to a language the tokenizer never met.

## Exercises

All edits happen in the `CONFIG` block at the top of `bpe_lab.py`.

### E1 — Guess the first merge
Before running at all: which adjacent character pair do you think is most frequent in English prose about tokens? Write down your guess for merges #1 and #2, then run and compare against experiment 1's table. (Hint: spaces are characters too.)

### E2 — Find the knee
Experiment 4 shows chars/token growing with merge count. Predict: at roughly how many merges does the training text cross **2.5 chars/token**? Edit `VOCAB_SWEEP` to bracket your guess (e.g. `[100, 130, 160]`), re-run, compare. Then explain the diminishing returns: why does merge #150 buy so much less than merge #15?

### E3 — Break the word model, not BPE
Append a sentence containing an invented word (e.g. `"The flurbogram exploded."`) to `HELD_OUT_TEXT`. Predict: how many tokens will your invented word cost in BPE, and what happens to it under word-level tokenization? Re-run experiments 2–3 and compare. This is the OOV problem that killed word-level vocabularies.

### E4 — Fix the fertility gap
Experiment 4 shows Georgian paying ~2× more tokens per character than English on this English-trained tokenizer. Predict what happens to the Georgian fertility if you append two or three Georgian sentences to `TRAIN_TEXT` and re-run. Then do it. This tiny experiment is exactly why multilingual models train tokenizers on multilingual corpora — and why some languages still pay more per request on real APIs.

### E5 — Stretch: don't merge across words
Real tokenizers (GPT-2 onward) pre-split text with a regex so merges never cross word boundaries. Add a pre-split step (e.g. split on `(?=\s)` using `re`), train per-chunk, and compare the top-12 merges to the current ones. Are the new merges more "word-like"? This is the difference between toy BPE and `tiktoken`.

## Deliverable

A short note (5 lines) answering E1–E4: prediction vs observed, one sentence each. Bring it to the next session — wrong predictions are the most useful thing you can bring, and they become learning records.
