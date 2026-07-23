"""Lab 0010 — The Microservice Tax.

Three experiments that price the monolith-to-microservices trade with
numbers instead of vibes. Run:  python3 microservice_tax_lab.py

Everything is simulated — no network, no containers. A "service hop" is a
lognormal latency draw (network calls have tails, not averages), a
"service" is a coin that comes up heads 99.9% of the time. Seeded RNG,
so runs are reproducible.

Then do the exercises in README.md — they all involve editing the
CONFIG block below and predicting the output BEFORE re-running.
"""

from __future__ import annotations

import math
import random

# ---------------------------------------------------------------- CONFIG
# The exercises in README.md ask you to change these and predict results.
SEED = 10
WORK_MS_TOTAL = 20.0        # total business work per request (split across N)
SERVICE_COUNTS = [1, 2, 5, 10, 20]   # N=1 is the monolith (zero network hops)
HOP_MEAN_MS = 1.0           # mean network latency per hop
HOP_SIGMA = 1.0             # lognormal shape: bigger sigma = fatter tail
LATENCY_REQUESTS = 20_000   # requests per N in experiment 1
AVAIL_REQUESTS = 100_000    # requests per N in experiment 2
SERVICE_AVAILABILITY = 0.999   # per-service success probability per call
RETRIES = 0                 # extra attempts per failed call (experiment 2)
FANOUT_SIZES = [1, 5, 10, 20, 100]   # parallel fan-out widths, experiment 3
FANOUT_REQUESTS = 20_000    # requests per width in experiment 3
HEDGE_AT_PCTL = 95          # fire a hedge when a call passes this pctl (None = off)
# -----------------------------------------------------------------------

# Lognormal parameterized so the mean equals HOP_MEAN_MS exactly.
_MU = math.log(HOP_MEAN_MS) - HOP_SIGMA ** 2 / 2.0


def hop_ms(rng: random.Random) -> float:
    """One network hop: lognormal — most are fast, a few are ugly."""
    return rng.lognormvariate(_MU, HOP_SIGMA)


def percentile(sorted_vals: list[float], p: float) -> float:
    idx = min(len(sorted_vals) - 1, int(p / 100.0 * len(sorted_vals)))
    return sorted_vals[idx]


def experiment_1_latency(rng: random.Random) -> None:
    print("=" * 78)
    print(f"EXPERIMENT 1 — same {WORK_MS_TOTAL:.0f} ms of work, split across N services")
    print(f"  serial chain, one network hop per service "
          f"(lognormal, mean {HOP_MEAN_MS:.1f} ms, sigma {HOP_SIGMA})")
    print("=" * 78)
    print(f"  {'N services':>10}  {'hops':>4}  {'mean ms':>8}  {'p50 ms':>8}  "
          f"{'p99 ms':>8}  {'p99 overhead':>12}")
    for n in SERVICE_COUNTS:
        hops = 0 if n == 1 else n           # monolith: in-process calls, ~0 cost
        lat = []
        for _ in range(LATENCY_REQUESTS):
            total = WORK_MS_TOTAL           # work is conserved — only hops differ
            for _ in range(hops):
                total += hop_ms(rng)
            lat.append(total)
        lat.sort()
        mean = sum(lat) / len(lat)
        p50, p99 = percentile(lat, 50), percentile(lat, 99)
        over = f"+{p99 - WORK_MS_TOTAL:5.1f} ms" if hops else "   (base)"
        label = "monolith" if n == 1 else f"{n}"
        print(f"  {label:>10}  {hops:>4}  {mean:>8.1f}  {p50:>8.1f}  "
              f"{p99:>8.1f}  {over:>12}")
    print("\n  -> the work never changed; the network did. Mean grows ~1 ms per hop,")
    print("     but p99 grows much faster: tails add across serial hops. That gap")
    print("     between mean and p99 is the latency line of the microservice tax.\n")


def experiment_2_availability(rng: random.Random) -> None:
    per_call = 1.0 - (1.0 - SERVICE_AVAILABILITY) ** (RETRIES + 1)
    print("=" * 78)
    print(f"EXPERIMENT 2 — availability of a serial chain: each service "
          f"{SERVICE_AVAILABILITY:.1%} per call, retries={RETRIES}")
    print("=" * 78)
    print(f"  {'N services':>10}  {'theory p^N':>10}  {'measured':>9}  "
          f"{'failed/100k':>11}  {'calls/req':>9}")
    for n in SERVICE_COUNTS:
        ok = 0
        calls = 0
        for _ in range(AVAIL_REQUESTS):
            success = True
            for _ in range(n):
                attempt_ok = False
                for _ in range(RETRIES + 1):
                    calls += 1
                    if rng.random() < SERVICE_AVAILABILITY:
                        attempt_ok = True
                        break               # stop retrying once a call lands
                if not attempt_ok:
                    success = False
                    break                   # chain is serial: one dead link kills it
            if success:
                ok += 1
        theory = per_call ** n
        measured = ok / AVAIL_REQUESTS
        print(f"  {n:>10}  {theory:>10.3%}  {measured:>9.3%}  "
              f"{AVAIL_REQUESTS - ok:>11,}  {calls / AVAIL_REQUESTS:>9.2f}")
    print("\n  -> availability multiplies, and it only multiplies DOWN: twenty")
    print("     three-nines services chained serially are a ~98% system. Retries")
    print("     buy nines back but pay in extra calls — watch calls/req when you")
    print("     rerun with RETRIES=1, and remember every retry is load somewhere.\n")


def _fanout_request(rng: random.Random, n: int, hedge_ms: float | None) -> tuple[float, int]:
    """Max of n parallel calls; optionally hedge each call at hedge_ms.

    Returns (request latency, hedges fired). A hedged call finishes at
    min(original, hedge_ms + fresh draw) — the 'tied request' idea from
    The Tail at Scale, simplified.
    """
    worst = 0.0
    hedges = 0
    for _ in range(n):
        t = hop_ms(rng)
        if hedge_ms is not None and t > hedge_ms:
            hedges += 1
            t = min(t, hedge_ms + hop_ms(rng))
        worst = max(worst, t)
    return worst, hedges


def experiment_3_fanout(rng: random.Random) -> None:
    # Establish the single-service latency profile first.
    single = sorted(hop_ms(rng) for _ in range(100_000))
    p99_1 = percentile(single, 99)
    hedge_ms = percentile(single, HEDGE_AT_PCTL) if HEDGE_AT_PCTL else None

    print("=" * 78)
    print(f"EXPERIMENT 3 — parallel fan-out: request waits for the SLOWEST of N")
    print(f"  single service: p50 {percentile(single, 50):.2f} ms, "
          f"p99 {p99_1:.2f} ms"
          + (f"; hedge fires at p{HEDGE_AT_PCTL} = {hedge_ms:.2f} ms" if hedge_ms else ""))
    print("=" * 78)
    print(f"  {'fan-out N':>9}  {'p99 ms':>7}  {'>1-svc p99':>10}  {'theory':>7}"
          f"  {'hedged p99':>10}  {'extra load':>10}")
    for n in FANOUT_SIZES:
        plain, hedged, hedge_count = [], [], 0
        for _ in range(FANOUT_REQUESTS):
            worst, _ = _fanout_request(rng, n, None)
            plain.append(worst)
            if hedge_ms is not None:
                worst_h, fired = _fanout_request(rng, n, hedge_ms)
                hedged.append(worst_h)
                hedge_count += fired
        plain.sort()
        over = sum(1 for v in plain if v > p99_1) / len(plain)
        theory = 1.0 - 0.99 ** n
        if hedge_ms is not None:
            hedged.sort()
            hp99 = f"{percentile(hedged, 99):>10.2f}"
            extra = f"{hedge_count / (FANOUT_REQUESTS * n):>9.1%}"
        else:
            hp99, extra = f"{'—':>10}", f"{'—':>9}"
        print(f"  {n:>9}  {percentile(plain, 99):>7.2f}  {over:>10.1%}  "
              f"{theory:>7.1%}  {hp99}  {extra}")
    print("\n  -> with fan-out, the 1-in-100 slow call becomes the COMMON case:")
    print("     at N=100, nearly every request eats at least one p99 straggler")
    print("     (theory 1 - 0.99^N). Hedging at p95 caps the tail for ~5% extra")
    print("     load per call — Dean & Barroso's tail-at-scale trade, measured.\n")


def main() -> None:
    rng = random.Random(SEED)
    experiment_1_latency(rng)
    experiment_2_availability(rng)
    experiment_3_fanout(rng)
    print("Done. Now do the README exercises: predict, edit CONFIG, re-run, compare.")


if __name__ == "__main__":
    main()
