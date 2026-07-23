"""Lab 0014 — Sagas & Fencing.

Three experiments that turn Lesson 0014's claims into things you've seen
with your own eyes. Run:  python3 saga_lab.py

Everything is simulated — no broker, no database, no real locks. Crashes
are coin flips at exactly the points where real processes die: between a
DB commit and a broker publish, between a saga step and the next, between
"lock acquired" and "write performed". Runs are reproducible (seeded RNG).

Then do the exercises in README.md — they all involve editing the CONFIG
block below and predicting the output BEFORE re-running.
"""

from __future__ import annotations

import math
import random

# ---------------------------------------------------------------- CONFIG
# The exercises in README.md ask you to change these and predict results.
SEED = 14

# Experiment 1 — dual-write vs outbox
RUNS = 10_000                   # checkout orders committed
CRASH_AFTER_COMMIT_RATE = 0.02  # naive: crash between DB commit and publish
RELAY_CRASH_RATE = 0.01         # outbox relay dies after publish, before marking sent
CONSUMER_DEDUP = True           # consumer ignores event ids it has already applied

# Experiment 2 — saga with crash injection
SAGA_RUNS = 10_000
STEP_FAIL_RATE = 0.03           # each forward step fails with this probability
COMP_FAIL_RATE = 0.10           # each compensation ATTEMPT fails with this probability
ACK_LOST_FRACTION = 0.5         # of failed attempts, fraction where work ran but ack was lost
COMP_IDEMPOTENT = True          # compensations carry an id; duplicates are ignored

# Experiment 3 — TTL lock, GC pause, fencing token
LOCK_TRIALS = 10_000
LOCK_TTL_S = 10.0               # lease length granted to worker A
PAUSE_MEAN_S = 4.0              # worker A's pause ~ exponential(mean); tail exceeds TTL
# -----------------------------------------------------------------------


def experiment_1_dual_write(rng: random.Random) -> None:
    print("=" * 78)
    print(f"EXPERIMENT 1 — dual write vs transactional outbox "
          f"({RUNS:,} orders, {CRASH_AFTER_COMMIT_RATE:.0%} crash-after-commit)")
    print("=" * 78)

    # --- naive dual write: commit DB row, THEN publish. Crash in between = lost event.
    naive_committed = RUNS
    naive_published = 0
    for _ in range(RUNS):
        if rng.random() >= CRASH_AFTER_COMMIT_RATE:   # survived the gap
            naive_published += 1
    naive_lost = naive_committed - naive_published

    # --- outbox: order row + event row commit in ONE local transaction.
    # A relay reads unsent rows, publishes, then marks them sent. If the relay
    # crashes after publish but before marking, the row is re-published on
    # restart -> at-least-once -> duplicates, never losses.
    out_committed = RUNS
    publishes = 0
    applied = 0
    seen: set[int] = set()
    for event_id in range(RUNS):
        sent = False
        while not sent:
            publishes += 1                      # broker got a copy
            if CONSUMER_DEDUP:
                if event_id not in seen:
                    seen.add(event_id)
                    applied += 1                # first delivery applied
            else:
                applied += 1                    # every delivery applied (!)
            if rng.random() < RELAY_CRASH_RATE:
                continue                        # crashed before marking sent -> retry
            sent = True
    duplicates = publishes - out_committed

    print(f"  {'scheme':<22} {'DB committed':>12} {'published':>10} "
          f"{'lost':>6} {'dupes':>6} {'consumer applied':>17}")
    print(f"  {'naive dual write':<22} {naive_committed:>12,} {naive_published:>10,} "
          f"{naive_lost:>6,} {0:>6} {naive_published:>17,}")
    print(f"  {'outbox + relay':<22} {out_committed:>12,} {publishes:>10,} "
          f"{0:>6} {duplicates:>6,} {applied:>17,}")
    dedup_note = "dedup ON: effectively-once" if CONSUMER_DEDUP else \
        "dedup OFF: duplicates were APPLIED — double-processing"
    print(f"\n  -> dual write silently lost {naive_lost:,} paid orders "
          f"({naive_lost / RUNS:.1%}) — committed, never announced.")
    print(f"     Outbox lost 0 but published {duplicates:,} duplicates; {dedup_note}.")
    print("     At-least-once delivery + idempotent consumer = effectively-once.\n")


# Saga steps as (forward action, compensating action) — a classic checkout.
STEPS = [
    ("create order", "cancel order"),
    ("charge payment", "refund payment"),
    ("reserve inventory", "release inventory"),
    ("create shipment", "void shipment"),
]


def _compensate(rng: random.Random, n_comps: int, retry: bool) -> tuple[bool, int]:
    """Run n_comps compensations. Returns (all_succeeded, double_applied_count)."""
    doubles = 0
    for _ in range(n_comps):
        executions = 0
        while True:
            if rng.random() < COMP_FAIL_RATE:            # attempt "failed"...
                if rng.random() < ACK_LOST_FRACTION:
                    executions += 1                      # ...but work actually ran
                if not retry:
                    return False, doubles                # stuck: give up after one try
                continue                                 # retry the compensation
            executions += 1                              # clean success
            break
        if executions > 1 and not COMP_IDEMPOTENT:
            doubles += executions - 1                    # e.g. refund applied twice
    return True, doubles


def experiment_2_saga(rng: random.Random) -> None:
    print("=" * 78)
    print(f"EXPERIMENT 2 — checkout saga, {SAGA_RUNS:,} runs, "
          f"{STEP_FAIL_RATE:.0%} step failure, {COMP_FAIL_RATE:.0%} compensation failure")
    print("=" * 78)

    # Precompute the forward-failure point of every run ONCE, so all three
    # modes face the identical sequence of step failures.
    step_rng = random.Random(SEED + 1)
    failures: list[int] = []
    for _ in range(SAGA_RUNS):
        failed_at = -1
        for i in range(len(STEPS)):
            if step_rng.random() < STEP_FAIL_RATE:
                failed_at = i
                break
        failures.append(failed_at)

    modes = [
        ("no compensation", None),
        ("compensate, 1 attempt", False),
        ("compensate + retry", True),
    ]
    print(f"  {'mode':<24} {'completed':>9} {'clean undo':>10} "
          f"{'stuck':>6} {'violations':>10} {'double-comps':>12}")
    for label, retry in modes:
        run_rng = random.Random(SEED + 2)     # compensation-outcome randomness
        completed = clean = stuck = violated = doubles = 0
        for failed_at in failures:
            if failed_at == -1:
                completed += 1
                continue
            if failed_at == 0:                # nothing to undo
                clean += 1
                continue
            if retry is None:                 # abort with no compensation
                violated += 1                 # e.g. payment charged, no shipment
                continue
            ok, d = _compensate(run_rng, failed_at, retry)
            doubles += d
            if ok:
                clean += 1
            else:
                stuck += 1                    # half-undone -> human queue
                violated += 1
        print(f"  {label:<24} {completed:>9,} {clean:>10,} "
              f"{stuck:>6,} {violated:>10,} {doubles:>12,}")

    print("\n  -> without compensation, every mid-saga failure strands an invariant")
    print("     (charged-but-unshipped). One-shot compensation still leaves a stuck")
    print("     queue when the UNDO also fails. Retry-until-success drives stuck to 0 —")
    print("     which is why compensations must be idempotent and retryable.\n")


def experiment_3_fencing(rng: random.Random) -> None:
    print("=" * 78)
    print(f"EXPERIMENT 3 — TTL lock ({LOCK_TTL_S:.0f}s) vs GC pause "
          f"(exp mean {PAUSE_MEAN_S:.0f}s), {LOCK_TRIALS:,} trials")
    print("=" * 78)

    expired = 0
    corrupted_no_fence = 0
    rejected_with_fence = 0
    for _ in range(LOCK_TRIALS):
        pause = rng.expovariate(1.0 / PAUSE_MEAN_S)   # A stalls after acquiring
        if pause <= LOCK_TTL_S:
            continue                                   # A writes within its lease: fine
        expired += 1
        # Lease expired mid-pause: B acquires with token 2, writes, then A wakes
        # and writes with its stale token 1.
        token_a, token_b = 1, 2
        highest_seen = token_b                         # resource saw B's write
        # without fencing: resource accepts A's late write -> B's update clobbered
        corrupted_no_fence += 1
        # with fencing: resource rejects token 1 < highest_seen
        if token_a < highest_seen:
            rejected_with_fence += 1

    p_theory = math.exp(-LOCK_TTL_S / PAUSE_MEAN_S)
    print(f"  {'mode':<20} {'pauses > TTL':>12} {'corrupted writes':>16} "
          f"{'stale rejected':>14}")
    print(f"  {'no fencing':<20} {expired:>12,} {corrupted_no_fence:>16,} "
          f"{0:>14}")
    print(f"  {'fencing token':<20} {expired:>12,} {0:>16} "
          f"{rejected_with_fence:>14,}")
    print(f"\n  -> {expired:,} of {LOCK_TRIALS:,} pauses outlived the lease "
          f"(theory: e^(-TTL/mean) = {p_theory:.1%}).")
    print("     Without fencing every one of them is a silent lost update by a client")
    print("     that BELIEVES it holds the lock. The fix is not a longer TTL — it is")
    print("     the resource checking a monotonically increasing token (Kleppmann).\n")


def main() -> None:
    rng = random.Random(SEED)
    experiment_1_dual_write(rng)
    experiment_2_saga(rng)
    experiment_3_fencing(rng)
    print("Done. Now do the README exercises: predict, edit CONFIG, re-run, compare.")


if __name__ == "__main__":
    main()
