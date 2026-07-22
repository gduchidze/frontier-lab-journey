"""Lab 0008 — Backpressure.

Three experiments that turn Lesson 0008's claims into things you've seen
with your own eyes. Run:  python3 backpressure_lab.py

A single consumer thread plays a service with ~SERVICE_RATE req/s of
capacity. Producers push work at it through a real queue.Queue. Wall time
is compressed (TIME_SCALE), so a full run takes seconds, and all waits
are reported in *simulated* milliseconds.

Timings ride on real thread scheduling, so numbers wiggle a little run to
run (deterministic-ish) — the *shapes* do not: the hockey stick, the flat
bounded-queue latency, and the retry storm show up every time.

Then do the exercises in README.md — they all involve editing the
CONFIG block below and predicting the output BEFORE re-running.
"""

from __future__ import annotations

import heapq
import queue
import random
import statistics
import threading
import time

# ---------------------------------------------------------------- CONFIG
# The exercises in README.md ask you to change these and predict results.
SERVICE_RATE = 100.0      # consumer capacity, requests/sec (mean service = 10 ms)
SERVICE_JITTER = 0.4      # service time varies uniformly ±40%
N_REQUESTS = 250          # arrivals per sweep point (experiments 1–2)
SWEEP = [0.50, 0.75, 0.90, 1.00, 1.20, 1.50]  # arrival rate ÷ capacity
QUEUE_BOUND = 20          # maxsize of the bounded queue (experiments 2–3)
OVERLOAD = 1.30           # offered load for the retry experiment
N_CLIENTS = 200           # first-attempt requests in experiment 3
MAX_RETRIES = 4           # extra attempts a rejected client gets
BACKOFF_BASE_MS = 100.0   # backoff cap doubles per attempt from this base
BACKOFF_CAP_MS = 2_000.0  # never back off longer than this
BACKOFF_JITTER = True     # full jitter: sleep uniform(0, cap). E4 flips this.
TIME_SCALE = 0.2          # wall seconds per simulated second (5× compressed)
SEED = 11
# -----------------------------------------------------------------------

_SENTINEL = object()


def sim_ms(real_seconds: float) -> float:
    """Convert measured wall time to simulated milliseconds."""
    return real_seconds / TIME_SCALE * 1000.0


def percentile(sorted_values: list[float], p: float) -> float:
    if not sorted_values:
        return float("nan")
    idx = min(int(len(sorted_values) * p), len(sorted_values) - 1)
    return sorted_values[idx]


def consumer(q: queue.Queue, waits: list[float], rng: random.Random) -> None:
    """Drain the queue at ~SERVICE_RATE until the sentinel arrives.

    For each item (its enqueue timestamp) we record how long it sat in the
    queue, then sleep the service time. Single consumer thread = the
    fixed-capacity service.
    """
    mean_service_s = 1.0 / SERVICE_RATE
    while True:
        item = q.get()
        if item is _SENTINEL:
            return
        waits.append(sim_ms(time.perf_counter() - item))
        service_s = mean_service_s * rng.uniform(1 - SERVICE_JITTER, 1 + SERVICE_JITTER)
        time.sleep(service_s * TIME_SCALE)


def run_sweep_point(load: float, bound: int) -> tuple[list[float], int, int]:
    """Fire N_REQUESTS at the consumer at `load` × capacity.

    bound=0 → unbounded queue, every request is accepted.
    bound>0 → bounded queue, a full queue rejects instantly (the 503 path).
    Returns (waits of served requests, rejected count, depth when arrivals stopped).
    """
    lam = SERVICE_RATE * load
    q: queue.Queue = queue.Queue(maxsize=bound)
    waits: list[float] = []
    rejected = 0
    arrivals = random.Random(SEED)      # same arrival pattern for every point
    service = random.Random(SEED + 1)   # same service-time pattern too
    worker = threading.Thread(target=consumer, args=(q, waits, service))
    worker.start()

    for _ in range(N_REQUESTS):
        time.sleep(arrivals.expovariate(lam) * TIME_SCALE)
        stamp = time.perf_counter()
        if bound:
            try:
                q.put_nowait(stamp)
            except queue.Full:
                rejected += 1          # immediate 503 — costs ~nothing
        else:
            q.put(stamp)

    depth_at_end = q.qsize()
    q.put(_SENTINEL)                   # blocks if bounded+full; consumer drains
    worker.join()
    return waits, rejected, depth_at_end


def experiment_1_unbounded() -> None:
    print("=" * 78)
    print("EXPERIMENT 1 — unbounded queue: the hockey stick (waits in simulated ms)")
    print("=" * 78)
    print(f"capacity ≈ {SERVICE_RATE:.0f} req/s; every request accepted; "
          f"{N_REQUESTS} arrivals per point\n")
    print(f"  {'load':>5}  {'arrival':>8}  {'mean wait':>10}  {'p99 wait':>10}  {'depth@end':>9}")
    for load in SWEEP:
        waits, _, depth = run_sweep_point(load, bound=0)
        s = sorted(waits)
        print(f"  {load:5.0%}  {SERVICE_RATE * load:6.0f}/s  "
              f"{statistics.fmean(s):8.1f}ms  {percentile(s, 0.99):8.1f}ms  {depth:9d}")
    print("\n  -> below ~90% load: small, stable waits. At 100%: wobbling on the edge.")
    print("     Past 100%: wait grows without limit and the queue runs away —")
    print("     'depth@end' is work still buried in the queue when arrivals stop.")
    print("     Nothing errored. The latency just hid in the queue.\n")


def experiment_2_bounded() -> None:
    print("=" * 78)
    print(f"EXPERIMENT 2 — bounded queue (maxsize={QUEUE_BOUND}) + immediate 503 rejection")
    print("=" * 78)
    print("same sweep; a full queue now rejects instead of absorbing\n")
    print(f"  {'load':>5}  {'arrival':>8}  {'mean wait':>10}  {'p99 wait':>10}  {'rejected':>9}")
    for load in SWEEP:
        waits, rejected, _ = run_sweep_point(load, bound=QUEUE_BOUND)
        s = sorted(waits)
        rej_rate = rejected / N_REQUESTS
        print(f"  {load:5.0%}  {SERVICE_RATE * load:6.0f}/s  "
              f"{statistics.fmean(s):8.1f}ms  {percentile(s, 0.99):8.1f}ms  {rej_rate:9.1%}")
    print(f"\n  -> accepted requests never wait more than ~bound/rate "
          f"≈ {QUEUE_BOUND / SERVICE_RATE * 1000:.0f} ms, at ANY load.")
    print("     Overload now shows up as an explicit, honest rejection rate —")
    print("     which clients can handle. That is backpressure.\n")


def run_retry_wave(naive: bool) -> tuple[int, int, float]:
    """Experiment 3 core: N_CLIENTS arrive at OVERLOAD × capacity.

    A rejected client retries up to MAX_RETRIES times:
      naive=True  -> retries ~immediately (1 ms later)
      naive=False -> exponential backoff, full jitter if BACKOFF_JITTER
    Returns (total attempts, successes, wall seconds for the wave).
    """
    q: queue.Queue = queue.Queue(maxsize=QUEUE_BOUND)
    waits: list[float] = []
    arrivals = random.Random(SEED + 2)
    service = random.Random(SEED + 3)
    jitter = random.Random(SEED + 4)
    worker = threading.Thread(target=consumer, args=(q, waits, service))
    worker.start()

    start = time.perf_counter()
    lam = SERVICE_RATE * OVERLOAD
    pending: list[tuple[float, int, int]] = []   # (due_time, client_id, attempt)
    t = start
    for i in range(N_CLIENTS):
        t += arrivals.expovariate(lam) * TIME_SCALE
        heapq.heappush(pending, (t, i, 0))

    attempts = succeeded = 0
    while pending:
        due, cid, attempt = heapq.heappop(pending)
        delay = due - time.perf_counter()
        if delay > 0:
            time.sleep(delay)
        attempts += 1
        try:
            q.put_nowait(time.perf_counter())
            succeeded += 1
        except queue.Full:                        # the 503 path
            if attempt >= MAX_RETRIES:
                continue                          # client gives up
            if naive:
                delay_ms = 1.0                    # hammer again, immediately
            else:
                cap = min(BACKOFF_CAP_MS, BACKOFF_BASE_MS * (2 ** attempt))
                delay_ms = jitter.uniform(0.0, cap) if BACKOFF_JITTER else cap
            retry_at = time.perf_counter() + delay_ms / 1000.0 * TIME_SCALE
            heapq.heappush(pending, (retry_at, cid, attempt + 1))

    q.put(_SENTINEL)
    worker.join()
    return attempts, succeeded, time.perf_counter() - start


def experiment_3_retries() -> None:
    print("=" * 78)
    print(f"EXPERIMENT 3 — retry storm vs backoff+jitter "
          f"(offered load {OVERLOAD:.0%}, {N_CLIENTS} clients, {MAX_RETRIES} retries max)")
    print("=" * 78)
    print(f"  {'policy':<26}  {'attempts':>8}  {'amplification':>13}  "
          f"{'wasted':>6}  {'success':>8}")
    for naive, label in ((True, "naive immediate retry"), (False, "exp. backoff + jitter")):
        attempts, ok, _wall = run_retry_wave(naive)
        print(f"  {label:<26}  {attempts:8d}  {attempts / N_CLIENTS:12.2f}x  "
              f"{attempts - ok:6d}  {ok / N_CLIENTS:8.1%}")
    print("\n  -> a naive client fires its whole retry budget within milliseconds of")
    print("     the first 503 — while the queue is still full. Amplified load lands")
    print("     exactly at the overload peak, almost all of it wasted, and the")
    print("     client dies anyway. Backoff+jitter defers retries past the spike,")
    print("     so they arrive at a draining queue and convert into successes.")
    print("     Jitter is what keeps those deferred retries from becoming a")
    print("     second synchronized wave (flip BACKOFF_JITTER to see it).\n")


def main() -> None:
    print(f"(wall clock compressed {1 / TIME_SCALE:.0f}x; all waits printed "
          f"in simulated ms; seed={SEED})\n")
    t0 = time.perf_counter()
    experiment_1_unbounded()
    experiment_2_bounded()
    experiment_3_retries()
    print(f"Done in {time.perf_counter() - t0:.1f}s wall time. "
          f"Now do the README exercises: predict, edit CONFIG, re-run, compare.")


if __name__ == "__main__":
    main()
