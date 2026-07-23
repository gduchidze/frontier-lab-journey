# Lab p0-06 — Gradient Descent, Overfitting, and Metrics

Companion to [Lesson p0-06](../../lessons/p0-06-ml-foundations.html). Everything the lesson claimed, you now verify with your own runs. Rule of the lab: **predict before you run.** Write your prediction down; the gap between prediction and output is where the learning is.

```bash
python3 gradient_descent_lab.py
```

Three experiments: (1) gradient descent fits `y = a·x + b` and a learning-rate sweep from too-timid to divergent, (2) polynomial capacity vs held-out error — bias–variance as a table, with an L2 rescue, (3) precision/recall/F1 across thresholds plus AUC on overlapping score distributions.

## Exercises

All edits happen in the `CONFIG` block at the top of `gradient_descent_lab.py`.

### E1 — Find the cliff
The sweep shows `lr=0.4` converging and `lr=0.6` diverging. Predict where the cliff is, then add `0.45`, `0.5`, `0.55` to `LR_SWEEP` and re-run. Bonus: the lesson's update-factor formula `(1 − lr·curvature)` says divergence starts where the factor passes −1 — does your measured cliff agree?

### E2 — The loss floor
Predict: with `NOISE = 0.0`, what does the final loss at `lr=0.05` become? And with `NOISE = 2.0`? Check the printed "noise floor" line each time. Lesson: training loss is bounded below by irreducible noise — chasing zero loss on noisy labels *is* overfitting.

### E3 — Buy your way out of variance
Degree 9 on 10 points is a disaster (val MSE ~10⁸). Predict what happens to its val MSE when `N_TRAIN` goes 10 → 100 with everything else unchanged. Re-run. Which is cheaper here, regularization or data? Now set `RIDGE_LAMBDA = 10.0` with `N_TRAIN = 10`: why does the ridge row drift toward the degree-0 row?

### E4 — Price the threshold
Suppose a false positive costs 10× a false negative (blocking a legit user vs missing one abuser). Using experiment 3's table, pick the threshold that minimizes `10·FP + FN` — compute FP and FN counts from precision/recall at 500+500 examples. Then make the classes overlap more (`NEG_MEAN = 0.55`) and re-run: predict AUC and best F1 first.

### E5 — Stretch: mini-batch noise
Full-batch gradient descent uses all 40 points per step. Modify `gd_linear` to sample 4 random points per step (mini-batch SGD). Compare loss curves at the same `lr`: the mini-batch curve is noisier — why does it still converge, and what would you do to the learning rate late in training?

## Deliverable

A short note (5 lines) answering E1–E4: prediction vs observed, one sentence each. Bring it to the next session — wrong predictions are the most useful thing you can bring, and they become learning records.
