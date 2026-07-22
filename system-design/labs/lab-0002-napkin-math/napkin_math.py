"""Lab 0002 — Napkin Math.

An estimation drill harness for Lesson 0002. Two modes:

    python3 napkin_math.py          # interactive: 10 drills, graded live
    python3 napkin_math.py --demo   # non-interactive: 3 worked solutions

Grading is order-of-magnitude, like an interviewer: within 2x = sharp,
within 10x = pass, beyond that = miss. Deterministic: the same SEED
always produces the same 10 problems, so you can re-drill the exact set.

Then do the exercises in README.md — they all involve editing the
CONFIG block below and predicting the output BEFORE re-running.
"""

from __future__ import annotations

import random
import sys
from dataclasses import dataclass

# ---------------------------------------------------------------- CONFIG
# The exercises in README.md ask you to change these and predict results.
SEED = 2                    # change to get a different (still fixed) drill set
NUM_QUESTIONS = 10          # drills per interactive run
SECONDS_PER_DAY = 1e5       # napkin rounding of 86,400 (E2 asks you to un-round it)
DAYS_PER_YEAR = 365
SHARP_FACTOR = 2.0          # within 2x of truth  -> "sharp"
PASS_FACTOR = 10.0          # within 10x of truth -> "right order of magnitude"
HBM_GB = 80                 # H100 memory; KV gets what the weights leave over
BYTES_PER_PARAM = 2         # bf16
# model presets: name -> (params_billions, layers, kv_heads, head_dim)
MODELS = {
    "8B": (8, 32, 8, 128),
    "13B": (13, 40, 8, 128),
    "70B": (70, 80, 8, 128),
}
# -----------------------------------------------------------------------


@dataclass(frozen=True)
class Problem:
    prompt: str
    answer: float          # in `unit`
    unit: str
    steps: tuple[str, ...]  # worked solution, one line each


def fmt(x: float) -> str:
    """Human-friendly number: commas for big integers, 2 sig-ish digits otherwise."""
    if x >= 1000:
        return f"{x:,.0f}"
    if x >= 10:
        return f"{x:.0f}"
    return f"{x:.2f}".rstrip("0").rstrip(".")


# ------------------------------------------------------------- problems
# Each builder takes an rng and returns a Problem. Order matters only for
# --demo, which uses fixed indices into this bank.

def p_qps_from_dau(rng: random.Random) -> Problem:
    dau_m = rng.choice([1, 5, 10, 50])
    actions = rng.choice([5, 10, 20])
    per_day = dau_m * 1e6 * actions
    ans = per_day / SECONDS_PER_DAY
    return Problem(
        prompt=(f"{dau_m}M DAU, each user makes {actions} requests/day. "
                f"Average QPS?"),
        answer=ans, unit="QPS",
        steps=(
            f"requests/day = {dau_m}M x {actions} = {fmt(per_day)}",
            f"QPS = {fmt(per_day)} / {fmt(SECONDS_PER_DAY)} s/day = {fmt(ans)}",
        ),
    )


def p_peak_qps(rng: random.Random) -> Problem:
    avg = rng.choice([500, 2_000, 8_000])
    factor = rng.choice([2, 5, 10])
    ans = avg * factor
    return Problem(
        prompt=f"Average QPS is {fmt(avg)}; assume a {factor}x peak factor. Peak QPS?",
        answer=ans, unit="QPS",
        steps=(f"peak = {fmt(avg)} x {factor} = {fmt(ans)}",),
    )


def p_read_qps(rng: random.Random) -> Problem:
    writes = rng.choice([1_000, 2_000, 5_000])
    ratio = rng.choice([5, 10, 100])
    ans = writes * ratio
    return Problem(
        prompt=(f"{fmt(writes)} writes/s with a {ratio}:1 read/write ratio. "
                f"Read QPS?"),
        answer=ans, unit="QPS",
        steps=(f"reads = {fmt(writes)} writes/s x {ratio} = {fmt(ans)}",),
    )


def p_storage_day(rng: random.Random) -> Problem:
    items_m = rng.choice([100, 200, 1_000])   # millions/day
    item_b = rng.choice([100, 200, 500])
    total_b = items_m * 1e6 * item_b
    ans = total_b / 1e9
    return Problem(
        prompt=(f"{items_m}M items written/day at {item_b} bytes each. "
                f"Storage per day in GB?"),
        answer=ans, unit="GB/day",
        steps=(
            f"bytes/day = {items_m}M x {item_b} B = {fmt(total_b)} B",
            f"GB/day = {fmt(total_b)} / 1e9 = {fmt(ans)}",
        ),
    )


def p_storage_year(rng: random.Random) -> Problem:
    gb_day = rng.choice([10, 40, 100])
    ans = gb_day * DAYS_PER_YEAR / 1000
    return Problem(
        prompt=f"A service writes {gb_day} GB/day. Storage per year in TB?",
        answer=ans, unit="TB/year",
        steps=(f"TB/year = {gb_day} GB x {DAYS_PER_YEAR} / 1,000 = {fmt(ans)}",),
    )


def p_bandwidth(rng: random.Random) -> Problem:
    gb_day = rng.choice([10, 40, 100, 1_000])
    ans = gb_day * 1e9 / SECONDS_PER_DAY / 1e6
    return Problem(
        prompt=(f"{fmt(gb_day)} GB flows through per day. "
                f"Average bandwidth in MB/s?"),
        answer=ans, unit="MB/s",
        steps=(
            f"bytes/s = {fmt(gb_day)} GB x 1e9 / {fmt(SECONDS_PER_DAY)} s",
            f"MB/s = that / 1e6 = {fmt(ans)}",
        ),
    )


def p_weights_mem(rng: random.Random) -> Problem:
    name = rng.choice(list(MODELS))
    params_b = MODELS[name][0]
    ans = params_b * BYTES_PER_PARAM
    return Problem(
        prompt=(f"{name} model in bf16 ({BYTES_PER_PARAM} bytes/param). "
                f"Weights memory in GB?"),
        answer=ans, unit="GB",
        steps=(f"weights = {params_b}e9 params x {BYTES_PER_PARAM} B = {fmt(ans)} GB",),
    )


def p_kv_per_token(rng: random.Random) -> Problem:
    name = rng.choice(list(MODELS))
    _, layers, kv_heads, head_dim = MODELS[name]
    ans = 2 * layers * kv_heads * head_dim * BYTES_PER_PARAM / 1e6
    return Problem(
        prompt=(f"{name} model: {layers} layers, {kv_heads} kv_heads, "
                f"head_dim {head_dim}, bf16. KV cache per token in MB?"),
        answer=ans, unit="MB/token",
        steps=(
            f"KV/token = 2 x {layers} x {kv_heads} x {head_dim} x {BYTES_PER_PARAM} B",
            f"         = {fmt(2 * layers * kv_heads * head_dim * BYTES_PER_PARAM)} B "
            f"= {fmt(ans)} MB",
        ),
    )


def p_kv_per_session(rng: random.Random) -> Problem:
    name = rng.choice(list(MODELS))
    _, layers, kv_heads, head_dim = MODELS[name]
    ctx = rng.choice([4_096, 8_192])
    per_tok = 2 * layers * kv_heads * head_dim * BYTES_PER_PARAM
    ans = per_tok * ctx / 1e9
    return Problem(
        prompt=(f"{name} model (KV = {fmt(per_tok / 1e6)} MB/token), "
                f"context {fmt(ctx)} tokens. KV cache per session in GB?"),
        answer=ans, unit="GB/session",
        steps=(f"KV/session = {fmt(per_tok / 1e6)} MB x {fmt(ctx)} tokens = {fmt(ans)} GB",),
    )


def p_sessions_per_gpu(rng: random.Random) -> Problem:
    name = rng.choice(["8B", "13B"])   # 70B does not fit one GPU: see lesson
    params_b, layers, kv_heads, head_dim = MODELS[name]
    ctx = rng.choice([4_096, 8_192])
    weights_gb = params_b * BYTES_PER_PARAM
    free_gb = HBM_GB - weights_gb
    session_gb = 2 * layers * kv_heads * head_dim * BYTES_PER_PARAM * ctx / 1e9
    ans = free_gb / session_gb
    return Problem(
        prompt=(f"One {HBM_GB} GB GPU, {name} model in bf16, "
                f"{fmt(ctx)}-token sessions. Concurrent sessions?"),
        answer=ans, unit="sessions",
        steps=(
            f"weights = {params_b} x {BYTES_PER_PARAM} = {weights_gb} GB "
            f"-> free = {HBM_GB} - {weights_gb} = {fmt(free_gb)} GB",
            f"KV/session = 2 x {layers} x {kv_heads} x {head_dim} x "
            f"{BYTES_PER_PARAM} B x {fmt(ctx)} = {fmt(session_gb)} GB",
            f"sessions = {fmt(free_gb)} / {fmt(session_gb)} = {fmt(ans)}",
        ),
    )


def p_gpus_for_fleet(rng: random.Random) -> Problem:
    sessions = rng.choice([200, 500, 1_000])
    session_gb = rng.choice([1.1, 2.7])
    usable_gb = 64  # napkin: ~64 GB usable for KV per GPU after an 8B model
    total = sessions * session_gb
    ans = total / usable_gb
    return Problem(
        prompt=(f"{fmt(sessions)} concurrent sessions x {session_gb} GB KV each; "
                f"{usable_gb} GB usable/GPU. GPUs needed?"),
        answer=ans, unit="GPUs",
        steps=(
            f"total KV = {fmt(sessions)} x {session_gb} GB = {fmt(total)} GB",
            f"GPUs = {fmt(total)} / {usable_gb} GB = {fmt(ans)} (round up)",
        ),
    )


BANK = [
    p_qps_from_dau,
    p_peak_qps,
    p_read_qps,
    p_storage_day,
    p_storage_year,
    p_bandwidth,
    p_weights_mem,
    p_kv_per_token,
    p_kv_per_session,
    p_sessions_per_gpu,
    p_gpus_for_fleet,
]

DEMO_INDICES = (0, 6, 9)   # QPS from DAU, weights memory, sessions per GPU


# -------------------------------------------------------------- grading

SUFFIXES = {"k": 1e3, "m": 1e6, "b": 1e9, "g": 1e9, "t": 1e12}


def parse_answer(raw: str) -> float | None:
    """Accept '2000', '2,000', '2e3', '2k', '3.5M', '1.2B'. None if unparseable."""
    text = raw.strip().lower().replace(",", "").replace(" ", "")
    if not text:
        return None
    scale = 1.0
    if text[-1] in SUFFIXES:
        scale = SUFFIXES[text[-1]]
        text = text[:-1]
    try:
        return float(text) * scale
    except ValueError:
        return None


def grade(guess: float, truth: float) -> str:
    if guess <= 0 or truth <= 0:
        return "miss"
    ratio = max(guess / truth, truth / guess)
    if ratio <= SHARP_FACTOR:
        return "sharp"
    if ratio <= PASS_FACTOR:
        return "pass"
    return "miss"


# ---------------------------------------------------------------- modes

def print_solution(prob: Problem, indent: str = "  ") -> None:
    for step in prob.steps:
        print(f"{indent}{step}")
    print(f"{indent}=> answer: {fmt(prob.answer)} {prob.unit}")


def run_demo() -> None:
    rng = random.Random(SEED)
    print("=" * 78)
    print("DEMO — three worked problems (study these, then run without --demo)")
    print("=" * 78)
    for shown, idx in enumerate(DEMO_INDICES, start=1):
        prob = BANK[idx](rng)
        print(f"\nProblem {shown}: {prob.prompt}")
        print_solution(prob)
    print("\nGrading in drill mode: within "
          f"{SHARP_FACTOR:.0f}x = sharp, within {PASS_FACTOR:.0f}x = pass.")
    print("Run  python3 napkin_math.py  to drill the full set of "
          f"{NUM_QUESTIONS}.")


def run_drill() -> None:
    rng = random.Random(SEED)
    order = [BANK[i % len(BANK)] for i in range(NUM_QUESTIONS)]
    rng.shuffle(order)
    print("=" * 78)
    print(f"NAPKIN MATH DRILL — {NUM_QUESTIONS} problems, seed {SEED}")
    print("Answer in the unit shown. Suffixes ok: 2k, 3.5M, 1.2B. Enter = reveal.")
    print(f"Scoring: within {SHARP_FACTOR:.0f}x = sharp (1 pt), "
          f"within {PASS_FACTOR:.0f}x = pass (1 pt), else miss.")
    print("=" * 78)
    score = 0
    for qi, builder in enumerate(order, start=1):
        prob = builder(rng)
        print(f"\nQ{qi}/{NUM_QUESTIONS} [{prob.unit}] {prob.prompt}")
        try:
            raw = input("  your answer> ")
        except EOFError:
            print("\n  (stdin closed — revealing remaining solution and stopping)")
            print_solution(prob)
            break
        guess = parse_answer(raw)
        if guess is None:
            print("  revealed:")
            print_solution(prob, indent="    ")
            continue
        verdict = grade(guess, prob.answer)
        if verdict == "sharp":
            score += 1
            print(f"  SHARP — truth is {fmt(prob.answer)} {prob.unit}, "
                  f"you were within {SHARP_FACTOR:.0f}x.")
        elif verdict == "pass":
            score += 1
            print(f"  PASS — right order of magnitude "
                  f"(truth: {fmt(prob.answer)} {prob.unit}).")
        else:
            print(f"  MISS — truth is {fmt(prob.answer)} {prob.unit}. Walkthrough:")
            print_solution(prob, indent="    ")
    print(f"\nScore: {score}/{NUM_QUESTIONS}. "
          "Interview bar: 8+ with every assumption stated out loud.")


def main() -> None:
    if "--demo" in sys.argv[1:]:
        run_demo()
    else:
        run_drill()


if __name__ == "__main__":
    main()
