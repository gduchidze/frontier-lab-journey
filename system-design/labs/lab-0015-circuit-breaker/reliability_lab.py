"""Lab 0015 — Circuit Breaker & Reliability Lab.

Three experiments that turn Lesson 0015's claims into numbers you have
seen with your own eyes. Run:  python3 reliability_lab.py

Everything is simulated — no network, no real outage. The "dependency"
is a function that fails on a schedule, and time is a discrete clock,
so runs are reproducible (seeded RNG) and finish in seconds.

Then do the exercises in README.md — they all involve editing the
CONFIG block below and predicting the output BEFORE re-running.
"""

from __future__ import annotations

import random
from collections import deque

# ---------------------------------------------------------------- CONFIG
# The exercises in README.md ask you to change these and predict results.

SEED = 15

# Experiment 1 — retry amplification
BASE_RPS = 100             # client demand, requests/second
DEP_CAPACITY = 150         # dependency capacity, attempts/second
FAIL_WINDOW = (3, 13)      # dependency fails FAIL_PROB of attempts in [start, end)
FAIL_PROB = 0.5            # failure probability during the window
LAYERS = 2                 # service layers that each retry independently
ATTEMPTS_PER_LAYER = 3     # attempts per layer (1 try + 2 retries)
RETRY_BUDGET_FRAC = 0.10   # budgeted policy: retries <= 10% of base requests
RETRY_JITTER = False       # E3: spread retries over the next 3 s instead of 1 s
SIM_SECONDS = 30

# Experiment 2 — circuit breaker
CALL_RPS = 50              # caller request rate
OUTAGE = (5.0, 15.0)       # dependency degraded in this window (seconds)
DEP_FAIL_PROB = 1.0        # failure prob during outage (1.0 = hard down; E2: try 0.5)
DEP_LATENCY_MS = 20.0      # healthy dependency latency
TIMEOUT_MS = 1000.0        # caller's timeout — the cost of every failed call
BREAKER_WINDOW = 20        # rolling window of calls used for the failure rate
BREAKER_THRESHOLD = 0.5    # trip when failure rate >= this over a full window
BREAKER_COOLDOWN_S = 2.0   # open -> half-open after this long
EXP2_SECONDS = 25

# Experiment 3 — load shedding
CAPACITY = 100             # server capacity, requests/second
RAMP_SECONDS = 20          # offered load ramps 0.5*C -> PEAK_MULT*C over this
PEAK_MULT = 2.0
ADMIT_FRAC = 0.90          # admission control: admit at most this * CAPACITY
PRIORITY_SHEDDING = False  # E4: shed "browse" first, protect "checkout"
CHECKOUT_FRAC = 0.20       # fraction of traffic that is checkout class
# -----------------------------------------------------------------------


# ============================================================ EXPERIMENT 1

def _mc_attempts_per_request(rng: random.Random, p_fail: float, n: int) -> tuple[float, int]:
    """Monte Carlo: attempts one client request causes at the bottom dependency
    when LAYERS layers each make up to ATTEMPTS_PER_LAYER attempts (nested)."""

    def inner(depth: int) -> tuple[bool, int]:
        attempts = 0
        for _ in range(ATTEMPTS_PER_LAYER):
            if depth == LAYERS:                    # bottom: hit the dependency
                attempts += 1
                if rng.random() >= p_fail:
                    return True, attempts
            else:
                ok, a = inner(depth + 1)
                attempts += a
                if ok:
                    return True, attempts
        return False, attempts

    total, worst = 0, 0
    for _ in range(n):
        _, a = inner(1)
        total += a
        worst = max(worst, a)
    return total / n, worst


def _storm(rng: random.Random, budgeted: bool) -> tuple[list[int], int, int]:
    """Per-second retry storm. Returns (offered per second, peak, recovery s).

    Failed attempts are retried next second (or spread over 3 s with jitter).
    Naive: each request may make ATTEMPTS_PER_LAYER**LAYERS total attempts.
    Budgeted: retries also need a token; tokens refill at 10% of base rate.
    """
    max_attempts = ATTEMPTS_PER_LAYER ** LAYERS
    pending: dict[int, list[int]] = {}             # second -> retries_left list
    offered_series: list[int] = []
    tokens = 0.0
    for t in range(SIM_SECONDS):
        batch = [max_attempts - 1] * BASE_RPS + pending.pop(t, [])
        offered_series.append(len(batch))
        tokens = min(tokens + BASE_RPS * RETRY_BUDGET_FRAC, BASE_RPS)
        overload = max(0, len(batch) - DEP_CAPACITY)
        for i, retries_left in enumerate(batch):
            in_window = FAIL_WINDOW[0] <= t < FAIL_WINDOW[1]
            failed = (in_window and rng.random() < FAIL_PROB) or i >= len(batch) - overload
            if failed and retries_left > 0:
                if budgeted:
                    if tokens < 1.0:
                        continue                   # budget exhausted: give up
                    tokens -= 1.0
                delay = rng.randint(1, 3) if RETRY_JITTER else 1
                pending.setdefault(t + delay, []).append(retries_left - 1)
    peak = max(offered_series)
    recovery = 0
    for t in range(FAIL_WINDOW[1], SIM_SECONDS):
        if offered_series[t] <= BASE_RPS * 1.05:
            recovery = t - FAIL_WINDOW[1]
            break
    return offered_series, peak, recovery


def experiment_1_retry_amplification(rng: random.Random) -> None:
    print("=" * 78)
    print(f"EXPERIMENT 1 — retry amplification: {LAYERS} layers x "
          f"{ATTEMPTS_PER_LAYER} attempts each, {FAIL_PROB:.0%} failure for "
          f"{FAIL_WINDOW[1] - FAIL_WINDOW[0]} s")
    print("=" * 78)

    print("  Part A — attempts at the bottom dependency, per client request:")
    print(f"  {'failure rate':>13}  {'mean attempts':>13}  {'worst case':>10}")
    for p in (FAIL_PROB, 1.0):
        mean, worst = _mc_attempts_per_request(rng, p, 20_000)
        print(f"  {p:>13.0%}  {mean:>13.2f}  {worst:>10}")
    print(f"  -> worst case = {ATTEMPTS_PER_LAYER}^{LAYERS} = "
          f"{ATTEMPTS_PER_LAYER ** LAYERS} attempts for ONE request during a full outage.\n")

    print("  Part B — the storm in time (dependency capacity "
          f"{DEP_CAPACITY}/s, base demand {BASE_RPS}/s):")
    naive_series, naive_peak, naive_rec = _storm(rng, budgeted=False)
    budget_series, budget_peak, budget_rec = _storm(rng, budgeted=True)
    print(f"  {'second':>6}  {'naive offered/s':>15}  {'budgeted offered/s':>18}")
    for t in range(1, SIM_SECONDS, 2):
        print(f"  {t:>6}  {naive_series[t]:>15}  {budget_series[t]:>18}")
    print(f"\n  {'policy':<14} {'peak load':>9}  {'multiplier':>10}  "
          f"{'recovery after window':>21}")
    for label, peak, rec in (("naive", naive_peak, naive_rec),
                             ("retry budget", budget_peak, budget_rec)):
        print(f"  {label:<14} {peak:>7}/s  {peak / BASE_RPS:>9.1f}x  {rec:>19} s")
    print("\n  -> naive retries turn a 50% brownout into an overload that OUTLIVES")
    print("     the failure window: the dependency must dig out from under the")
    print("     storm. The budget keeps offered load near capacity, so recovery")
    print("     is immediate. Retries are a loan against future capacity.\n")


# ============================================================ EXPERIMENT 2

class CircuitBreaker:
    """Closed / open / half-open. Failure rate over a rolling call window."""

    def __init__(self) -> None:
        self.state = "closed"
        self.window: deque[bool] = deque(maxlen=BREAKER_WINDOW)
        self.opened_at = 0.0
        self.transitions: list[tuple[float, str]] = []

    def _move(self, now: float, state: str) -> None:
        self.state = state
        self.transitions.append((now, state))

    def allow(self, now: float) -> bool:
        if self.state == "open":
            if now - self.opened_at >= BREAKER_COOLDOWN_S:
                self._move(now, "half-open")
                return True                        # the single probe
            return False
        return True                                # closed or half-open

    def record(self, now: float, ok: bool) -> None:
        if self.state == "half-open":
            if ok:
                self.window.clear()
                self._move(now, "closed")
            else:
                self.opened_at = now
                self._move(now, "open")
            return
        self.window.append(ok)
        if (len(self.window) == BREAKER_WINDOW
                and self.window.count(False) / BREAKER_WINDOW >= BREAKER_THRESHOLD):
            self.opened_at = now
            self._move(now, "open")


def _run_caller(use_breaker: bool) -> dict:
    rng = random.Random(SEED)
    breaker = CircuitBreaker() if use_breaker else None
    n_calls = int(CALL_RPS * EXP2_SECONDS)
    lat_out: list[float] = []                      # latencies during the outage
    errors = fast_fails = 0
    first_success_after = None
    for i in range(n_calls):
        now = i / CALL_RPS
        in_window = OUTAGE[0] <= now < OUTAGE[1]
        down = in_window and rng.random() < DEP_FAIL_PROB
        if breaker and not breaker.allow(now):
            fast_fails += 1
            errors += 1
            if in_window:
                lat_out.append(0.001)              # fail-fast: ~microseconds
            continue
        if down:                                   # call eats the full timeout
            errors += 1
            lat_out.append(TIMEOUT_MS)
            if breaker:
                breaker.record(now, ok=False)
        else:
            if in_window:
                lat_out.append(DEP_LATENCY_MS)
            if breaker:
                breaker.record(now, ok=True)
            if now >= OUTAGE[1] and first_success_after is None:
                first_success_after = now - OUTAGE[1]
    return {
        "errors": errors,
        "fast": fast_fails,
        "avg_ms": sum(lat_out) / len(lat_out) if lat_out else 0.0,
        "wasted_s": sum(ms for ms in lat_out if ms >= TIMEOUT_MS) / 1000.0,
        "recover_s": first_success_after if first_success_after is not None else -1.0,
        "transitions": breaker.transitions if breaker else [],
    }


def experiment_2_circuit_breaker() -> None:
    print("=" * 78)
    print(f"EXPERIMENT 2 — circuit breaker: dependency {DEP_FAIL_PROB:.0%} failing "
          f"{OUTAGE[0]:.0f}s-{OUTAGE[1]:.0f}s, caller timeout {TIMEOUT_MS:.0f} ms, "
          f"{CALL_RPS} calls/s")
    print("=" * 78)
    plain = _run_caller(use_breaker=False)
    with_b = _run_caller(use_breaker=True)
    print(f"  {'scenario':<18} {'errors':>7}  {'avg latency in outage':>21}  "
          f"{'caller-seconds wasted':>21}  {'recovery':>8}")
    for label, r in (("no breaker", plain), ("with breaker", with_b)):
        print(f"  {label:<18} {r['errors']:>7}  {r['avg_ms']:>18.1f} ms  "
              f"{r['wasted_s']:>19.1f} s  {r['recover_s']:>6.2f} s")
    print(f"\n  breaker state transitions ({len(with_b['transitions'])} total):")
    for t, state in with_b["transitions"][:8]:
        print(f"    t={t:5.2f}s  -> {state}")
    if len(with_b["transitions"]) > 8:
        print(f"    ... {len(with_b['transitions']) - 8} more")
    print("\n  -> without the breaker every call during the outage blocks for the")
    print("     full 1000 ms timeout — the caller 'spends' hundreds of seconds of")
    print("     thread time on a dependency that cannot answer. With the breaker,")
    print("     ~1 window of calls pays the timeout, then everything fails in")
    print("     microseconds, and a half-open probe recloses after recovery.\n")


# ============================================================ EXPERIMENT 3

def _shed_run(rng: random.Random, admit_cap: float | None) -> dict:
    """Per-second queue sim. admit_cap=None means no shedding (queue grows)."""
    queue = 0.0
    rejected = {"checkout": 0, "browse": 0}
    waits = {"checkout": [], "browse": []}
    rows = []
    for t in range(RAMP_SECONDS):
        offered = int(CAPACITY * (0.5 + (PEAK_MULT - 0.5) * t / (RAMP_SECONDS - 1)))
        n_checkout = int(offered * CHECKOUT_FRAC)
        n_browse = offered - n_checkout
        if admit_cap is None:
            adm_c, adm_b = n_checkout, n_browse
        else:
            cap = int(admit_cap)
            if PRIORITY_SHEDDING:
                adm_c = min(n_checkout, cap)
                adm_b = min(n_browse, cap - adm_c)
            else:                                  # shed uniformly at random
                admitted = min(offered, cap)
                adm_c = sum(1 for _ in range(admitted)
                            if rng.random() < CHECKOUT_FRAC)
                adm_b = admitted - adm_c
            rejected["checkout"] += n_checkout - adm_c
            rejected["browse"] += n_browse - adm_b
        wait_ms = queue / CAPACITY * 1000.0        # Little's law: W = L / mu
        waits["checkout"] += [wait_ms] * adm_c
        waits["browse"] += [wait_ms] * adm_b
        queue = max(0.0, queue + adm_c + adm_b - CAPACITY)
        rows.append((t, offered, int(queue), wait_ms))
    return {"rows": rows, "rejected": rejected, "waits": waits}


def _p99(xs: list[float]) -> float:
    return sorted(xs)[int(len(xs) * 0.99)] if xs else 0.0


def experiment_3_load_shedding(rng: random.Random) -> None:
    print("=" * 78)
    print(f"EXPERIMENT 3 — load shedding: capacity {CAPACITY}/s, offered load "
          f"ramps 0.5x -> {PEAK_MULT:.1f}x over {RAMP_SECONDS} s")
    print("=" * 78)
    unshed = _shed_run(rng, admit_cap=None)
    shed = _shed_run(rng, admit_cap=CAPACITY * ADMIT_FRAC)
    print(f"  {'second':>6}  {'offered/s':>9}  {'queue (unshed)':>14}  "
          f"{'wait ms (unshed)':>16}  {'wait ms (shed)':>14}")
    for i in range(0, RAMP_SECONDS, 3):
        t, offered, q, w = unshed["rows"][i]
        _, _, _, ws = shed["rows"][i]
        print(f"  {t:>6}  {offered:>9}  {q:>14}  {w:>16.0f}  {ws:>14.0f}")
    all_u = unshed["waits"]["checkout"] + unshed["waits"]["browse"]
    all_s = shed["waits"]["checkout"] + shed["waits"]["browse"]
    n_rej = sum(shed["rejected"].values())
    print(f"\n  {'policy':<20} {'p99 wait':>10}  {'rejected':>8}")
    print(f"  {'no shedding':<20} {_p99(all_u):>7.0f} ms  {0:>8}")
    print(f"  {'admit <= 0.9C':<20} {_p99(all_s):>7.0f} ms  {n_rej:>8}")
    if PRIORITY_SHEDDING:
        print(f"\n  per-class (priority shedding ON, checkout protected):")
        for cls in ("checkout", "browse"):
            print(f"    {cls:<9} p99 {_p99(shed['waits'][cls]):>6.0f} ms   "
                  f"rejected {shed['rejected'][cls]:>5}")
    last_q = unshed["rows"][-1][2]
    print(f"\n  -> Little's law: at the end the unshed queue holds {last_q} requests,")
    print(f"     so a new arrival waits {last_q}/{CAPACITY} = "
          f"{last_q / CAPACITY:.1f} s — and the queue is still GROWING.")
    print("     Shedding answers some users with a fast 503 so the rest get the")
    print("     latency they came for. Brownout beats blackout.\n")


def main() -> None:
    rng = random.Random(SEED)
    experiment_1_retry_amplification(rng)
    experiment_2_circuit_breaker()
    experiment_3_load_shedding(rng)
    print("Done. Now do the README exercises: predict, edit CONFIG, re-run, compare.")


if __name__ == "__main__":
    main()
