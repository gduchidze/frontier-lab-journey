"""Lab p0-06 — Gradient Descent, Overfitting, and Metrics.

Three experiments that turn Lesson p0-06's claims into things you have
seen with your own eyes. Run:  python3 gradient_descent_lab.py

Then do the exercises in README.md — they all involve editing the
CONFIG block below and predicting the output BEFORE re-running.
"""

from __future__ import annotations

import math
import random

# ---------------------------------------------------------------- CONFIG
# The exercises in README.md ask you to change these and predict results.
SEED = 7

# Experiment 1 — fit y = a*x + b by gradient descent
TRUE_A, TRUE_B = 3.0, -1.0    # the "truth" the model must recover
N_POINTS = 40                 # training examples
NOISE = 0.5                   # stddev of label noise (the floor of the loss)
LR = 0.05                     # learning rate for the loss-curve run
STEPS = 200                   # gradient steps
PRINT_EVERY = 20              # loss-curve print interval
LR_SWEEP = [0.001, 0.05, 0.4, 0.6]   # E1 asks you to extend this

# Experiment 2 — polynomial overfitting on a handful of points
N_TRAIN = 10                  # training points (tiny on purpose)
N_VAL = 30                    # held-out points
POLY_NOISE = 0.15             # label noise around sin(2*pi*x)
DEGREES = [0, 1, 3, 5, 9]     # polynomial capacities to try
RIDGE_LAMBDA = 1e-3           # L2 strength for the regularized degree-9 fit

# Experiment 3 — precision/recall threshold sweep on classifier scores
N_POS, N_NEG = 500, 500       # positives / negatives in the eval set
POS_MEAN, NEG_MEAN = 0.65, 0.35   # mean score of each class (overlap!)
SCORE_STD = 0.15              # score spread for both classes
THRESHOLDS = [round(0.1 * t, 2) for t in range(1, 10)]
# -----------------------------------------------------------------------


# ------------------------------------------------ experiment 1 helpers
def make_linear_data(rng: random.Random) -> tuple[list[float], list[float]]:
    xs = [rng.uniform(0.0, 2.0) for _ in range(N_POINTS)]
    ys = [TRUE_A * x + TRUE_B + rng.gauss(0.0, NOISE) for x in xs]
    return xs, ys


def mse_linear(a: float, b: float, xs: list[float], ys: list[float]) -> float:
    return sum((a * x + b - y) ** 2 for x, y in zip(xs, ys)) / len(xs)


def gd_linear(xs: list[float], ys: list[float], lr: float, steps: int):
    """Plain full-batch gradient descent on MSE. Returns (a, b, loss, status, trace)."""
    a = b = 0.0
    n = len(xs)
    trace: list[tuple[int, float, float, float]] = []
    for step in range(steps):
        grad_a = sum(2.0 * (a * x + b - y) * x for x, y in zip(xs, ys)) / n
        grad_b = sum(2.0 * (a * x + b - y) for x, y in zip(xs, ys)) / n
        a -= lr * grad_a
        b -= lr * grad_b
        loss = mse_linear(a, b, xs, ys)
        if not math.isfinite(loss) or loss > 1e12:
            return a, b, loss, "DIVERGED", trace
        if step % PRINT_EVERY == 0 or step == steps - 1:
            trace.append((step, loss, a, b))
    return a, b, mse_linear(a, b, xs, ys), "converging", trace


def experiment_1_gradient_descent(rng: random.Random) -> None:
    print("=" * 78)
    print(f"EXPERIMENT 1 — gradient descent fits y = a*x + b   "
          f"(truth: a={TRUE_A}, b={TRUE_B}, noise={NOISE})")
    print("=" * 78)
    xs, ys = make_linear_data(rng)
    print(f"loss curve at lr={LR} (loss floor should approach noise^2 = {NOISE**2:.2f}):\n")
    a, b, loss, status, trace = gd_linear(xs, ys, LR, STEPS)
    for step, l, aa, bb in trace:
        print(f"  step {step:>4}   loss={l:10.4f}   a={aa:7.3f}   b={bb:7.3f}")
    print(f"\n  -> learned a={a:.3f}, b={b:.3f} vs truth a={TRUE_A}, b={TRUE_B}. "
          f"Loss cannot beat the noise floor.\n")

    print("learning-rate sweep (same data, same step budget):\n")
    print(f"  {'lr':>8}  {'status':<11} {'final loss':>12}  {'a':>8}  {'b':>8}")
    for lr in LR_SWEEP:
        a, b, loss, status, _ = gd_linear(xs, ys, lr, STEPS)
        loss_txt = f"{loss:12.4f}" if loss < 1e9 else f"{loss:12.2e}"
        print(f"  {lr:>8}  {status:<11} {loss_txt}  {a:8.3f}  {b:8.3f}")
    print("\n  -> too small: barely moves in the budget. Too big: each step "
          "overshoots and the loss EXPLODES.\n")


# ------------------------------------------------ experiment 2 helpers
def true_fn(x: float) -> float:
    return math.sin(2.0 * math.pi * x)


def poly_features(x: float, degree: int) -> list[float]:
    t = 2.0 * x - 1.0            # rescale [0,1] -> [-1,1] for conditioning
    return [t ** k for k in range(degree + 1)]


def solve_linear_system(A: list[list[float]], b: list[float]) -> list[float]:
    """Gaussian elimination with partial pivoting (stdlib-only ridge solver)."""
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(M[r][col]))
        M[col], M[pivot] = M[pivot], M[col]
        p = M[col][col] if abs(M[col][col]) > 1e-300 else 1e-300
        for r in range(col + 1, n):
            f = M[r][col] / p
            for c in range(col, n + 1):
                M[r][c] -= f * M[col][c]
    w = [0.0] * n
    for r in range(n - 1, -1, -1):
        s = M[r][n] - sum(M[r][c] * w[c] for c in range(r + 1, n))
        w[r] = s / (M[r][r] if abs(M[r][r]) > 1e-300 else 1e-300)
    return w


def fit_poly(xs: list[float], ys: list[float], degree: int, lam: float = 0.0) -> list[float]:
    """Least squares via normal equations: (X^T X + lam*I) w = X^T y."""
    feats = [poly_features(x, degree) for x in xs]
    d = degree + 1
    A = [[sum(f[r] * f[c] for f in feats) + (lam if r == c else 0.0)
          for c in range(d)] for r in range(d)]
    b = [sum(f[r] * y for f, y in zip(feats, ys)) for r in range(d)]
    return solve_linear_system(A, b)


def poly_mse(w: list[float], xs: list[float], ys: list[float]) -> float:
    degree = len(w) - 1
    total = 0.0
    for x, y in zip(xs, ys):
        pred = sum(wi * f for wi, f in zip(w, poly_features(x, degree)))
        total += (pred - y) ** 2
    return total / len(xs)


def experiment_2_bias_variance(rng: random.Random) -> None:
    print("=" * 78)
    print(f"EXPERIMENT 2 — bias-variance made visible   "
          f"(truth: sin(2*pi*x) + noise, {N_TRAIN} train / {N_VAL} val points)")
    print("=" * 78)
    xtr = sorted(rng.uniform(0.0, 1.0) for _ in range(N_TRAIN))
    ytr = [true_fn(x) + rng.gauss(0.0, POLY_NOISE) for x in xtr]
    xva = sorted(rng.uniform(0.0, 1.0) for _ in range(N_VAL))
    yva = [true_fn(x) + rng.gauss(0.0, POLY_NOISE) for x in xva]

    print(f"\n  {'model':<22} {'train MSE':>12} {'val MSE':>12}   verdict")
    rows: list[tuple[str, float, float]] = []
    for deg in DEGREES:
        w = fit_poly(xtr, ytr, deg)
        rows.append((f"degree {deg}", poly_mse(w, xtr, ytr), poly_mse(w, xva, yva)))
    w = fit_poly(xtr, ytr, 9, lam=RIDGE_LAMBDA)
    rows.append((f"degree 9 + L2({RIDGE_LAMBDA})",
                 poly_mse(w, xtr, ytr), poly_mse(w, xva, yva)))

    best_val = min(v for _, _, v in rows)
    for name, tr, va in rows:
        if va > 10 * best_val and tr < 0.5 * va:
            verdict = "OVERFIT (variance)"
        elif tr > 0.15 and va > 0.15:
            verdict = "underfit (bias)"
        else:
            verdict = "fits"
        star = "  <- best val" if va == best_val else ""
        va_txt = f"{va:12.4f}" if va < 1e6 else f"{va:12.2e}"
        print(f"  {name:<22} {tr:12.4f} {va_txt}   {verdict}{star}")
    print("\n  -> train error ALWAYS improves with capacity; held-out error is "
          "U-shaped. L2 tames the degree-9 monster.\n")


# ------------------------------------------------ experiment 3 helpers
def experiment_3_metrics(rng: random.Random) -> None:
    print("=" * 78)
    print(f"EXPERIMENT 3 — precision/recall threshold sweep   "
          f"(scores: pos~N({POS_MEAN},{SCORE_STD}), neg~N({NEG_MEAN},{SCORE_STD}))")
    print("=" * 78)
    pos = [rng.gauss(POS_MEAN, SCORE_STD) for _ in range(N_POS)]
    neg = [rng.gauss(NEG_MEAN, SCORE_STD) for _ in range(N_NEG)]

    print(f"\n  {'thresh':>7} {'precision':>10} {'recall':>8} {'F1':>7}   trade")
    for th in THRESHOLDS:
        tp = sum(1 for s in pos if s >= th)
        fp = sum(1 for s in neg if s >= th)
        fn = N_POS - tp
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = (2 * precision * recall / (precision + recall)
              if precision + recall else 0.0)
        if recall > 0.95 and precision < 0.85:
            note = "catch all, flag junk"
        elif precision > 0.95 and recall < 0.85:
            note = "trust flags, miss cases"
        else:
            note = "balanced-ish"
        print(f"  {th:>7} {precision:>10.3f} {recall:>8.3f} {f1:>7.3f}   {note}")

    # AUC by rank statistic: P(random positive scores above random negative)
    scored = sorted([(s, 1) for s in pos] + [(s, 0) for s in neg])
    rank_sum = sum(rank for rank, (_, is_pos) in enumerate(scored, start=1) if is_pos)
    auc = (rank_sum - N_POS * (N_POS + 1) / 2) / (N_POS * N_NEG)
    print(f"\n  AUC = {auc:.3f}   (probability a random positive outranks a "
          f"random negative; 0.5 = coin flip)")
    print("  -> precision and recall move in OPPOSITE directions as the "
          "threshold slides. Picking the threshold\n     is a product decision "
          "(cost of FP vs FN), not an ML decision.\n")


def main() -> None:
    rng = random.Random(SEED)
    experiment_1_gradient_descent(rng)
    experiment_2_bias_variance(rng)
    experiment_3_metrics(rng)
    print("Done. Now do the README exercises: predict, edit CONFIG, re-run, compare.")


if __name__ == "__main__":
    main()
