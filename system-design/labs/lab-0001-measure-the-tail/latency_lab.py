"""Lab 0001 — Measure the Tail.

Three experiments that turn Lesson 0001's claims into things you've seen
with your own eyes. Run:  python3 latency_lab.py

Then do the exercises in README.md — they all involve editing the
CONFIG block below and predicting the output BEFORE re-running.
"""

from __future__ import annotations

import random
import statistics
from dataclasses import dataclass

# ---------------------------------------------------------------- CONFIG
# The exercises in README.md ask you to change these and predict results.
SAMPLES = 50_000          # requests simulated per experiment
BASE_MS = 40.0            # typical fast-path service time
TAIL_PROB = 0.01          # fraction of requests that hit the slow path
TAIL_MS = 1_000.0         # how slow the slow path is
FANOUTS = [1, 10, 50, 100, 500]   # backend calls per page load (experiment 2)
BATCH_SIZES = [1, 8, 32, 128]     # experiment 3
PER_ITEM_MS = 1.0         # GPU-ish cost per item inside a batch
FIXED_OVERHEAD_MS = 25.0  # fixed cost paid once per batch (kernel launch, weights read)
ARRIVAL_RATE_RPS = 400    # incoming request rate for experiment 3
SEED = 7
# -----------------------------------------------------------------------


def service_latency(rng: random.Random) -> float:
    """One request's latency: lognormal body + rare slow tail (GC pause,
    cache miss, page fault, noisy neighbor...)."""
    body = rng.lognormvariate(0, 0.3) * BASE_MS
    if rng.random() < TAIL_PROB:
        return body + rng.uniform(0.5, 1.5) * TAIL_MS
    return body


def percentile(sorted_values: list[float], p: float) -> float:
    idx = min(int(len(sorted_values) * p), len(sorted_values) - 1)
    return sorted_values[idx]


@dataclass(frozen=True)
class Summary:
    mean: float
    p50: float
    p90: float
    p99: float
    p999: float

    @classmethod
    def of(cls, values: list[float]) -> "Summary":
        s = sorted(values)
        return cls(
            mean=statistics.fmean(s),
            p50=percentile(s, 0.50),
            p90=percentile(s, 0.90),
            p99=percentile(s, 0.99),
            p999=percentile(s, 0.999),
        )

    def row(self, label: str) -> str:
        return (f"{label:<22} mean={self.mean:8.1f}  p50={self.p50:8.1f}  "
                f"p90={self.p90:8.1f}  p99={self.p99:8.1f}  p999={self.p999:8.1f}")


def experiment_1_mean_vs_tail(rng: random.Random) -> list[float]:
    print("=" * 78)
    print("EXPERIMENT 1 — the mean is a lie (all numbers in ms)")
    print("=" * 78)
    lat = [service_latency(rng) for _ in range(SAMPLES)]
    print(Summary.of(lat).row("single service call"))
    mean, p99 = statistics.fmean(lat), Summary.of(lat).p99
    print(f"\n  -> mean says '{mean:.0f} ms service'; the p99 user waits "
          f"{p99 / mean:.0f}x longer ({p99:.0f} ms).")
    print(f"  -> only {TAIL_PROB:.0%} of requests are slow, yet they own the tail.\n")
    return lat


def experiment_2_tail_amplification(rng: random.Random, single: list[float]) -> None:
    print("=" * 78)
    print("EXPERIMENT 2 — fan-out amplifies the tail (page = max of N calls)")
    print("=" * 78)
    threshold = Summary.of(single).p99
    print(f"'slow' below means: worse than the single-call p99 ({threshold:.0f} ms)\n")
    for n in FANOUTS:
        pages = 2_000
        page_lat = [max(service_latency(rng) for _ in range(n)) for _ in range(pages)]
        slow_frac = sum(1 for v in page_lat if v > threshold) / pages
        predicted = 1 - (0.99 ** n)
        print(f"  fanout N={n:<4} p50(page)={percentile(sorted(page_lat), 0.5):8.1f} ms   "
              f"pages hitting tail: measured={slow_frac:5.1%}  theory(1-0.99^N)={predicted:5.1%}")
    print("\n  -> at N=100+, the 'rare' 1% tail is most page loads. "
          "Averages never showed this.\n")


def experiment_3_batching_tradeoff() -> None:
    print("=" * 78)
    print("EXPERIMENT 3 — batching: throughput up, latency up (deterministic model)")
    print("=" * 78)
    print(f"model: batch of B costs {FIXED_OVERHEAD_MS:.0f} ms fixed + "
          f"{PER_ITEM_MS:.0f} ms/item; arrivals at {ARRIVAL_RATE_RPS} req/s\n")
    for b in BATCH_SIZES:
        proc_ms = FIXED_OVERHEAD_MS + PER_ITEM_MS * b
        throughput = b / (proc_ms / 1000.0)
        # average wait for the batch to fill at the given arrival rate,
        # then the whole batch is processed together
        fill_ms = (b - 1) / 2 / ARRIVAL_RATE_RPS * 1000.0
        avg_latency = fill_ms + proc_ms
        print(f"  batch={b:<4} throughput={throughput:8.0f} req/s   "
              f"avg latency={avg_latency:7.1f} ms  "
              f"(wait {fill_ms:5.1f} + process {proc_ms:5.1f})")
    print("\n  -> same hardware, 30x the throughput, at a latency price. "
          "LLM serving (Phase 4) is the art of paying that price wisely.\n")


def main() -> None:
    rng = random.Random(SEED)
    single = experiment_1_mean_vs_tail(rng)
    experiment_2_tail_amplification(rng, single)
    experiment_3_batching_tradeoff()
    print("Done. Now do the README exercises: predict, edit CONFIG, re-run, compare.")


if __name__ == "__main__":
    main()
