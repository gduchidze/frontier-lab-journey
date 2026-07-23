# Lab 0020 — Feed Fanout

Companion to [Lesson 0020](../../lessons/0020-news-feed.html). The lesson claims that fanout-on-write, fanout-on-read, and the hybrid sit on a cost curve with a minimum at a follower-count threshold. This lab makes you compute where that minimum is by hand-waving — then shows you where it actually is.

```bash
python3 fanout_lab.py                  # 10k-user power-law graph, all three strategies
python3 fanout_lab.py --threshold 100  # move the celebrity cutoff for the hybrid row
```

The script builds a 10,000-user social graph with a power-law follower distribution (`random.paretovariate` — a few accounts have thousands of followers, the median has ~7), fires 5,000 posts and 20,000 feed reads at it, and delivers the posts three ways. Fanout workers have finite capacity (3,000 inserts/tick), so a celebrity post creates a real backlog: `stale p99` is the head-of-line blocking from lesson §6, measured. The final table sweeps the celebrity threshold and prints a total-cost proxy (feed inserts + lists merged across all reads).

Everything is seeded (`SEED = 20`) — identical numbers every run until you edit the CONFIG block.

## Protocol

1. Write every prediction down BEFORE running. A prediction made after seeing the output is a memory, not a prediction.
2. One CONFIG change at a time; re-run; compare against your note.
3. The interesting findings are the mis-predictions — log those, not the confirmations.

## Exercises

### E1 — Predict the write amplification
Before the first run: the graph has ~10k users averaging ~20 followers, and 5,000 posts. Predict the fanout-on-write ratio `feed inserts ÷ posts`. Most people predict ≈ mean followers. Run and compare — the observed ratio is much higher. Why? (Hint: read the traffic-generation docstring — who posts most, and what does that do to the *effective* amplification? This is exactly why real feeds hurt more than their average suggests.)

### E2 — Read the trade, row by row
Cover the output. For each column — feed inserts, merge avg, merge p99, stale p99, mem cells — predict which strategy wins and which loses. Run and score yourself out of 15 cells. Then explain the two subtlest cells aloud: why is pull's `mem cells` so small, and why is hybrid's `stale p99` zero while push's is not?

### E3 — Sweep the threshold, predict the U-curve
Before looking at EXPERIMENT 3: sketch on paper the total-cost curve as the threshold goes 1 → 10,000. Mark where you expect the minimum (a specific threshold value from the SWEEP list) and predict the cost at both extremes relative to each other (is pure push cheaper or pricier than pure pull here?). Run and overlay reality on your sketch. Then reason about *why* the minimum sits where it does: pulling an author beats pushing them when their posts × followers exceeds the extra merges their followers' reads pay — which accounts satisfy that?

### E4 — Make the tail heavier
Set `ALPHA = 1.05` (heavier celebrity tail) and predict, before re-running: max follower count, push's `stale p99`, and which direction the U-curve's minimum threshold moves. Re-run and compare. Restore `ALPHA = 1.15` afterwards. Bonus: halve `FANOUT_CAPACITY` and predict which single cell of the strategy table degrades most.

## Deliverable

Your prediction-vs-observed notes for E1–E4 (a few honest lines each: what you predicted, what happened, why the gap). Bring them to the next session — the E1 gap and your E3 sketch are the two the teacher will ask about, because they are the two the interviewer will too.
