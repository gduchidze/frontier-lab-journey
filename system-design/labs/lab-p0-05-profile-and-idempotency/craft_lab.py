"""Lab p0-05 — Profile It, Then Make It Safe to Retry.

Three experiments that turn "senior code craft" from advice into numbers:
  1. Profiling: find the real hotspot (string concat vs join), measure the
     quadratic blow-up, and read cProfile output like a senior.
  2. Idempotency: a retry storm against a payment endpoint — count duplicate
     charges with and without an idempotency key.
  3. Retry amplification: naive retries multiply load on a struggling server;
     backoff + retry budgets tame it.

Run:  python3 craft_lab.py
Then do the README exercises: predict, edit CONFIG, re-run, compare.
"""

from __future__ import annotations

import cProfile
import io
import pstats
import random
import time

# ---------------------------------------------------------------- CONFIG
# The exercises in README.md ask you to change these and predict results.
CONCAT_SIZES = [4_000, 16_000, 64_000]  # lines appended in experiment 1
PROFILE_SIZE = 30_000        # input size for the cProfile demo
N_CLIENTS = 200              # clients attempting one payment each (exp 2)
RESPONSE_LOSS_PROB = 0.30    # chance the SUCCESS RESPONSE is lost in transit
MAX_RETRIES = 3              # client retries after a lost response
FAILURE_RATE = 0.5           # fraction of requests a degraded server fails (exp 3)
RETRY_ATTEMPTS = [1, 2, 3, 4]  # total attempts per request (1 = no retry)
RETRY_BUDGET = 1.1           # retries allowed as a fraction of base load (SRE style)
SEED = 12
# -----------------------------------------------------------------------


# ============================== EXPERIMENT 1 — profiling ==============================

class SlowReport:
    """The classic accidental O(n^2): immutable strings copied on every +=.

    (On an object attribute the copy ALWAYS happens. A bare local `out += s`
    is sometimes rescued by a CPython refcount trick — never rely on it.)
    """

    def __init__(self) -> None:
        self.body = ""

    def add_line(self, line: str) -> None:
        self.body += line  # copies the whole report each call


def build_report_slow(n: int) -> str:
    report = SlowReport()
    for i in range(n):
        report.add_line("x")
    return report.body


def build_report_fast(n: int) -> str:
    """O(n): accumulate in a list, join once."""
    parts = []
    for i in range(n):
        parts.append("x")
    return "".join(parts)


def timed(fn, *args) -> float:
    t0 = time.perf_counter()
    fn(*args)
    return (time.perf_counter() - t0) * 1000.0


def experiment_1_profile() -> None:
    print("=" * 78)
    print("EXPERIMENT 1 — profile first, optimize second (times in ms)")
    print("=" * 78)
    print(f"{'n chars':>10} {'concat +=':>12} {'join':>10} {'ratio':>8}   scaling check")
    prev_slow = None
    for n in CONCAT_SIZES:
        slow = timed(build_report_slow, n)
        fast = timed(build_report_fast, n)
        note = ""
        if prev_slow is not None and prev_slow > 0:
            note = f"concat grew {slow / prev_slow:4.1f}x for 4x input"
        ratio = slow / fast if fast > 0 else float("inf")
        print(f"{n:>10,} {slow:>12.2f} {fast:>10.2f} {ratio:>7.0f}x   {note}")
        prev_slow = slow
    print("\n  -> += on strings re-copies everything: 4x input ≈ 16x time (O(n^2)).")
    print("  -> 'It felt slow' is a guess. Below is what a profiler SAYS:\n")

    prof = cProfile.Profile()
    prof.enable()
    build_report_slow(PROFILE_SIZE)
    build_report_fast(PROFILE_SIZE)
    prof.disable()
    buf = io.StringIO()
    stats = pstats.Stats(prof, stream=buf).sort_stats("cumulative")
    stats.print_stats(6)
    for line in buf.getvalue().splitlines():
        if line.strip():
            print("   " + line)
    print("\n  -> read 'cumtime' top-down: the hotspot names itself. Never optimize")
    print("     without this view — seniors profile, juniors guess.\n")


# ============================== EXPERIMENT 2 — idempotency ==============================

class PaymentServer:
    """Charges cards. Optionally deduplicates via idempotency keys."""

    def __init__(self, use_keys: bool):
        self.use_keys = use_keys
        self.charges: list[str] = []          # side effects (money moved!)
        self.seen: dict[str, str] = {}        # idempotency key -> stored response

    def charge(self, client_id: str, key: str) -> str:
        if self.use_keys and key in self.seen:
            return self.seen[key]             # replay stored response, NO new charge
        self.charges.append(client_id)        # the side effect: card charged
        response = f"ok:{client_id}"
        if self.use_keys:
            self.seen[key] = response
        return response


def run_retry_storm(rng: random.Random, use_keys: bool) -> tuple[int, int]:
    """Each client pays once; the network drops success responses sometimes,
    so clients retry. Returns (clients_charged_more_than_once, total_charges)."""
    server = PaymentServer(use_keys)
    for c in range(N_CLIENTS):
        key = f"idem-{c}"                     # generated ONCE per logical payment
        for _attempt in range(1 + MAX_RETRIES):
            server.charge(f"client-{c}", key)
            if rng.random() >= RESPONSE_LOSS_PROB:
                break                         # response arrived: client stops
            # response lost -> client cannot tell success from failure -> retry
    counts: dict[str, int] = {}
    for cid in server.charges:
        counts[cid] = counts.get(cid, 0) + 1
    dupes = sum(1 for v in counts.values() if v > 1)
    return dupes, len(server.charges)


def experiment_2_idempotency(rng: random.Random) -> None:
    print("=" * 78)
    print("EXPERIMENT 2 — the retry storm: idempotency keys vs double charges")
    print("=" * 78)
    print(f"{N_CLIENTS} clients, {RESPONSE_LOSS_PROB:.0%} of success responses lost, "
          f"up to {MAX_RETRIES} retries\n")
    print(f"{'mode':<28} {'total charges':>14} {'double-charged':>15}")
    for use_keys, label in [(False, "no idempotency key"), (True, "with idempotency key")]:
        dupes, total = run_retry_storm(rng, use_keys)
        print(f"{label:<28} {total:>14} {dupes:>15}")
    print(f"\n  -> retries are NOT optional (networks lose responses); safety must live")
    print("     on the SERVER: same key => replay stored response, never re-execute.")
    print("     This is exactly Stripe's Idempotency-Key header contract.\n")


# ============================== EXPERIMENT 3 — retry amplification ==============================

def experiment_3_retry_amplification(rng: random.Random) -> None:
    print("=" * 78)
    print("EXPERIMENT 3 — retries amplify load on a server that is already dying")
    print("=" * 78)
    base = 10_000  # logical requests
    print(f"server failing {FAILURE_RATE:.0%} of requests; {base:,} logical requests\n")
    print(f"{'attempts':>9} {'requests sent':>14} {'load multiplier':>16}   verdict")
    for attempts in RETRY_ATTEMPTS:
        sent = 0
        for _ in range(base):
            for _a in range(attempts):
                sent += 1
                if rng.random() >= FAILURE_RATE:
                    break  # success: stop retrying
        mult = sent / base
        verdict = "fine" if mult < 1.5 else ("heavy" if mult < 1.8 else "storm fuel")
        print(f"{attempts:>9} {sent:>14,} {mult:>15.2f}x   {verdict}")
    # SRE-style retry budget: retries may not exceed RETRY_BUDGET-1 fraction extra
    sent = 0
    retries_spent = 0
    retry_cap = int(base * (RETRY_BUDGET - 1.0))
    for _ in range(base):
        sent += 1
        ok = rng.random() >= FAILURE_RATE
        while not ok and retries_spent < retry_cap:
            retries_spent += 1
            sent += 1
            ok = rng.random() >= FAILURE_RATE
    print(f"\n  with a retry BUDGET of {RETRY_BUDGET:.0%} of base load: "
          f"sent {sent:,} = {sent / base:.2f}x (capped)")
    print("  -> unbounded retries turn a 50% brownout into ~2x traffic — the push that")
    print("     kills the server. Google SRE: cap retries with budgets + jittered backoff.\n")


def main() -> None:
    rng = random.Random(SEED)
    t0 = time.perf_counter()
    experiment_1_profile()
    experiment_2_idempotency(rng)
    experiment_3_retry_amplification(rng)
    print(f"Done in {time.perf_counter() - t0:.1f} s. "
          "Now do the README exercises: predict, edit CONFIG, re-run, compare.")


if __name__ == "__main__":
    main()