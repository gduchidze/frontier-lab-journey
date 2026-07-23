"""Lab p0-08 — Build BPE.

Four experiments that turn Lesson p0-08's claims into things you've seen
with your own eyes: train a real byte-pair-encoding tokenizer from scratch,
round-trip text through it, compare char/word/subword granularities, and
measure the vocab-size vs sequence-length trade (plus what happens to a
language the tokenizer never saw).

Run:  python3 bpe_lab.py

Then do the exercises in README.md — they all involve editing the
CONFIG block below and predicting the output BEFORE re-running.
"""

from __future__ import annotations

import time
from collections import Counter

# ---------------------------------------------------------------- CONFIG
# The exercises in README.md ask you to change these and predict results.
NUM_MERGES = 200          # merges for the "main" tokenizer (experiments 1-3)
MERGES_TO_SHOW = 12       # how many learned merges to print in experiment 1
VOCAB_SWEEP = [0, 25, 50, 100, 200, 400]   # experiment 4 sweep
TOKENS_TO_SHOW = 24       # how many tokens of the encoding to print

TRAIN_TEXT = (
    "The tokenizer is the first system your text touches, and the last "
    "system anyone debugs. Before the model can predict anything, the input "
    "is split into tokens, and every token costs memory, compute, and money. "
    "The serving bill is a token bill. The latency budget is a token budget. "
    "The context window is a token window. When an engineer says the model "
    "is slow, the honest question is: how many tokens did you send, and how "
    "many tokens did it generate? "
    "A byte pair encoding tokenizer learns its vocabulary from data. It "
    "starts from characters, counts every adjacent pair, and merges the most "
    "frequent pair into a new token. Then it counts again, and merges again, "
    "thousands of times. Frequent words become single tokens. Rare words "
    "break into familiar pieces. Nothing is ever out of vocabulary, because "
    "in the worst case the tokenizer falls back to the characters it started "
    "from. "
    "This matters for serving because sequence length drives everything: "
    "attention cost, cache size, queueing time, and the price on the "
    "invoice. A bigger vocabulary means shorter sequences but a bigger "
    "embedding table. A smaller vocabulary means longer sequences but a "
    "smaller table. The trade is measurable, and in this lab you will "
    "measure it."
)

HELD_OUT_TEXT = (
    "Tokenizers memorize merges, not meanings. The word untokenizable never "
    "appears in training, yet the encoder still handles it by falling back "
    "to smaller familiar pieces, one merge at a time."
)

GEORGIAN_TEXT = (
    "ტოკენიზაცია პირველი ნაბიჯია, რომელსაც ენის მოდელი დგამს, და ის "
    "განსაზღვრავს, რამდენი დაჯდება ყოველი მოთხოვნა."
)
# -----------------------------------------------------------------------


def pair_counts(tokens: list[str]) -> Counter:
    counts: Counter = Counter()
    for a, b in zip(tokens, tokens[1:]):
        counts[(a, b)] += 1
    return counts


def merge_pair(tokens: list[str], pair: tuple[str, str]) -> list[str]:
    """Return a NEW token list with every occurrence of `pair` fused."""
    a, b = pair
    out: list[str] = []
    i = 0
    while i < len(tokens):
        if i < len(tokens) - 1 and tokens[i] == a and tokens[i + 1] == b:
            out.append(a + b)
            i += 2
        else:
            out.append(tokens[i])
            i += 1
    return out


def train_bpe(text: str, num_merges: int) -> tuple[list[tuple[tuple[str, str], int]], list[str]]:
    """Greedy BPE: repeatedly merge the most frequent adjacent pair.

    Returns (merges, final_tokens) where merges is an ordered list of
    ((left, right), frequency_at_merge_time).
    """
    tokens = list(text)
    merges: list[tuple[tuple[str, str], int]] = []
    for _ in range(num_merges):
        counts = pair_counts(tokens)
        if not counts:
            break
        pair, freq = counts.most_common(1)[0]
        if freq < 2:
            break  # nothing repeats — further merges would just memorize
        merges.append((pair, freq))
        tokens = merge_pair(tokens, pair)
    return merges, tokens


def encode(text: str, merges: list[tuple[tuple[str, str], int]]) -> list[str]:
    """Encoding = replay the learned merges, in training order."""
    tokens = list(text)
    for pair, _freq in merges:
        tokens = merge_pair(tokens, pair)
    return tokens


def decode(tokens: list[str]) -> str:
    return "".join(tokens)


def visible(token: str) -> str:
    return token.replace(" ", "␣")


def experiment_1_train() -> list[tuple[tuple[str, str], int]]:
    print("=" * 78)
    print(f"EXPERIMENT 1 — train BPE on the paragraph ({len(TRAIN_TEXT)} chars)")
    print("=" * 78)
    base_vocab = sorted(set(TRAIN_TEXT))
    merges, final_tokens = train_bpe(TRAIN_TEXT, NUM_MERGES)
    print(f"base vocabulary: {len(base_vocab)} unique characters")
    print(f"requested merges: {NUM_MERGES}   actually learned: {len(merges)} "
          f"(training stops when no pair repeats)\n")
    print(f"  {'step':>4}  {'pair':<16} {'freq':>4}   new token")
    for i, (pair, freq) in enumerate(merges[:MERGES_TO_SHOW], start=1):
        a, b = pair
        print(f"  {i:>4}  {visible(a)!r} + {visible(b)!r:<10} {freq:>4}   {visible(a + b)!r}")
    if len(merges) > MERGES_TO_SHOW:
        print(f"  ... {len(merges) - MERGES_TO_SHOW} more merges")
    vocab_size = len(base_vocab) + len(merges)
    print(f"\n  -> final vocab = {len(base_vocab)} chars + {len(merges)} merges "
          f"= {vocab_size} tokens")
    print(f"  -> training text: {len(TRAIN_TEXT)} chars -> {len(final_tokens)} tokens "
          f"({len(TRAIN_TEXT) / len(final_tokens):.2f} chars/token)\n")
    return merges


def experiment_2_round_trip(merges: list[tuple[tuple[str, str], int]]) -> None:
    print("=" * 78)
    print("EXPERIMENT 2 — encode/decode round trip on text the trainer NEVER saw")
    print("=" * 78)
    tokens = encode(HELD_OUT_TEXT, merges)
    restored = decode(tokens)
    assert restored == HELD_OUT_TEXT, "round trip must be lossless"
    print(f"held-out text: {len(HELD_OUT_TEXT)} chars -> {len(tokens)} tokens, "
          f"round trip lossless: {restored == HELD_OUT_TEXT}\n")
    shown = "|".join(visible(t) for t in tokens[:TOKENS_TO_SHOW])
    print(f"  first {TOKENS_TO_SHOW} tokens: {shown}...")
    unseen = "untokenizable"
    unseen_tokens = encode(unseen, merges)
    print(f"\n  the unseen word {unseen!r} becomes {len(unseen_tokens)} tokens: "
          f"{'|'.join(unseen_tokens)}")
    print("  -> no <UNK>, no crash: BPE falls back to smaller pieces. "
          "Nothing is out of vocabulary.\n")


def experiment_3_granularities(merges: list[tuple[tuple[str, str], int]]) -> None:
    print("=" * 78)
    print("EXPERIMENT 3 — characters vs words vs BPE on the same held-out text")
    print("=" * 78)
    char_vocab = len(set(TRAIN_TEXT))
    word_vocab_set = set(TRAIN_TEXT.split())
    held_words = HELD_OUT_TEXT.split()
    oov = [w for w in held_words if w not in word_vocab_set]
    bpe_vocab = char_vocab + len(merges)
    bpe_tokens = len(encode(HELD_OUT_TEXT, merges))
    print(f"  {'scheme':<12} {'vocab size':>10} {'held-out tokens':>16}   coverage")
    print(f"  {'character':<12} {char_vocab:>10} {len(HELD_OUT_TEXT):>16}   every string, ever")
    print(f"  {'word':<12} {len(word_vocab_set):>10} {len(held_words):>16}   "
          f"{len(oov)} words are OOV -> <UNK>")
    print(f"  {'BPE':<12} {bpe_vocab:>10} {bpe_tokens:>16}   every string, ever")
    print(f"\n  OOV words the word-level model cannot represent: "
          f"{', '.join(repr(w) for w in oov[:6])} ...")
    print("  -> BPE sits between the extremes: bounded vocab AND no OOV, "
          "with sequences ~2-3x shorter than characters.\n")


def experiment_4_vocab_trade() -> None:
    print("=" * 78)
    print("EXPERIMENT 4 — vocab size vs sequence length (the trade you pay for)")
    print("=" * 78)
    base = len(set(TRAIN_TEXT))
    print(f"  {'merges':>6} {'vocab':>6} {'train tokens':>13} {'chars/token':>12} "
          f"{'held-out tokens':>16}")
    for m in VOCAB_SWEEP:
        merges, final_tokens = train_bpe(TRAIN_TEXT, m)
        held = len(encode(HELD_OUT_TEXT, merges))
        print(f"  {len(merges):>6} {base + len(merges):>6} {len(final_tokens):>13} "
              f"{len(TRAIN_TEXT) / len(final_tokens):>12.2f} {held:>16}")
    print("\n  -> more merges = bigger vocab = shorter sequences, with "
          "diminishing returns.\n")

    merges, _ = train_bpe(TRAIN_TEXT, NUM_MERGES)
    en_fertility = len(encode(HELD_OUT_TEXT, merges)) / len(HELD_OUT_TEXT)
    ka_fertility = len(encode(GEORGIAN_TEXT, merges)) / len(GEORGIAN_TEXT)
    print("  Fertility check — tokens per character, same tokenizer:")
    print(f"    English held-out : {en_fertility:.2f} tokens/char")
    print(f"    Georgian sentence: {ka_fertility:.2f} tokens/char "
          f"({ka_fertility / en_fertility:.1f}x more tokens per char)")
    print("  -> a language absent from tokenizer training pays ~"
          f"{ka_fertility / en_fertility:.0f}x more tokens for the same text: "
          "more latency, more KV cache, a bigger bill.\n")


def main() -> None:
    start = time.perf_counter()
    merges = experiment_1_train()
    experiment_2_round_trip(merges)
    experiment_3_granularities(merges)
    experiment_4_vocab_trade()
    print(f"Done in {time.perf_counter() - start:.2f}s. "
          "Now do the README exercises: predict, edit CONFIG, re-run, compare.")


if __name__ == "__main__":
    main()
