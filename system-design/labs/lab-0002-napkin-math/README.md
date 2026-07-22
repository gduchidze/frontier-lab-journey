# Lab 0002 — Napkin Math

Companion to [Lesson 0002](../../lessons/0002-back-of-envelope.html). The lesson gave you the estimation sequence and the two GPU formulas; this lab drills them until they are reflex. Rule of the lab: **predict before you run.** Write your prediction down; the gap between prediction and output is where the learning is.

```bash
python3 napkin_math.py --demo   # 3 fully worked solutions — study these first
python3 napkin_math.py          # the drill: 10 problems, graded live
```

Grading matches how an interviewer scores you: within 2× of truth = **sharp**, within 10× = **pass** (right order of magnitude), beyond = **miss** (you get the full walkthrough). Answers accept suffixes (`2k`, `3.5M`, `1.2B`) and scientific notation (`2e3`). The set is deterministic — same `SEED`, same 10 problems — so you can re-drill the exact set after studying your misses.

Keep the [Estimation Kit](../../reference/0002-estimation-kit.html) open on the first run. By the third run you should not need it.

## Exercises

All edits happen in the `CONFIG` block at the top of `napkin_math.py`.

### E1 — Baseline drill
Run `--demo`, but cover the solution lines and predict each answer from the prompt alone before uncovering. Then run the interactive drill and record your score. Interview bar: 8+/10 — with the extra discipline of saying every assumption out loud as you type.

### E2 — Does precision matter?
Predict: if you change `SECONDS_PER_DAY` from `1e5` back to the exact `86_400`, how many of the 10 truth values change, and does any change by enough to flip a *pass* into a *miss*? Write your guess, edit, re-run `--demo`, compare. Lesson: the 14% rounding error can never cross an order-of-magnitude boundary — that is exactly why the rounding is safe. Then restore.

### E3 — The tolerance is the message
Set `PASS_FACTOR = 2.0` (so only *sharp* counts) and re-drill the same seed. Predict your new score first. Now set it back and change `SEED` to any other value for a fresh set. Which problem *type* do you miss most across seeds? That type is your weak formula — copy it onto a flashcard.

### E4 — KV budget for YOUR gateway
Take the SLO sheet you wrote for the LLM inference gateway in Lesson 0001 and compute its capacity line by hand, then check with the script's formulas:

1. Pick a model (`8B` or `70B`) and an average context length (say 8k).
2. From your sustained RPS target and an assumed session duration, estimate concurrent sessions (e.g. 1,000 RPS × 0.2 s in-flight ≈ 200 concurrent).
3. KV demand = sessions × KV-per-session; divide by usable HBM per GPU to get GPU count. (Sanity anchor from the lesson: 200 × 8k sessions on the 8B model ≈ 220 GB KV ≈ 4 H100s.)
4. Cross-check by editing `MODELS`/`HBM_GB` to your chosen shape and reading the `sessions_per_gpu` and `gpus_for_fleet` walkthroughs.

Write the resulting GPU count on your SLO sheet — it is now a capacity plan, not just a wish list.

## Deliverable

A short note (5 lines): E1 score, E2 prediction vs observed, your weak formula from E3, and the GPU count from E4 with its two key assumptions. Bring it to the next session — wrong predictions are the most useful thing you can bring, and they become learning records.
