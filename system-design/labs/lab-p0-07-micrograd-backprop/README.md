# Lab p0-07 — Micrograd Backprop

Companion to [Lesson p0-07](../../lessons/p0-07-dl-foundations.html). You will run a complete scalar autograd engine — a ~60-line clone of [Karpathy's micrograd](https://github.com/karpathy/micrograd) — and verify every central claim of the lesson with your own numbers. Rule of the lab: **predict before you run.** Write the prediction down; the gap between prediction and output is where the learning is.

```bash
python3 micrograd_lab.py
```

Four experiments: (1) autograd vs finite-difference gradient check, (2) XOR training with plain SGD — watch the plateau, (3) SGD vs momentum vs Adam race from identical initial weights, (4) gradient magnitudes through 8 layers as a function of init scale (vanishing/exploding made visible).

## Exercises

All edits happen in the `CONFIG` dict at the top of `micrograd_lab.py`.

### E1 — Break the gradient check
Predict: what happens to the `abs error` column if `GRAD_CHECK_H` goes from `1e-6` to `1e-1`? And to `1e-12`? (Two different failure mechanisms: truncation error vs floating-point cancellation.) Run both, compare, restore.

### E2 — Learning-rate cliff
With plain SGD, predict the training curve at `LR_SGD = 1.0`, then `3.0`. Converge faster, oscillate, or diverge? Run each. Then find (roughly) the largest LR that still converges. This cliff is why LR is the single most-tuned hyperparameter in deep learning.

### E3 — Handicap Adam
Predict: if `TARGET_LOSS` tightens to `0.001`, do the three optimizers keep their ranking from experiment 3? Does the *gap* between SGD and Adam grow or shrink? Run and compare. Then try `HIDDEN = 2` — which optimizer suffers most from the smaller network?

### E4 — Find the stable scale
Experiment 4 says stable init scale ≈ `sqrt(3/width)`. Set `WIDTH = 32` and predict the new stable scale *before* computing it. Add your predicted value to `INIT_SCALES`, run, and check that `|input grad|` stays near 1 while the other scales vanish/explode. This formula is Xavier/He initialization in miniature.

### E5 — Stretch: the accumulation bug
In `experiment_2_train_xor`, comment out the `p.grad = 0.0` line and predict what the loss curve does. Run it. This exact bug — gradients accumulate across steps unless explicitly zeroed — is one of the most common real-world PyTorch mistakes (`optimizer.zero_grad()`). Explain *why* the engine's `+=` in `_backward` makes zeroing necessary.

## Deliverable

A short note (5 lines) answering E1–E4: prediction vs observed, one sentence each. Bring it to the next session — wrong predictions are the most useful thing you can bring, and they become learning records.
