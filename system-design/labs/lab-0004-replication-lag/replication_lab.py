"""Lab 0004 — Replication Lag.

Four experiments that turn Lesson 0004's claims into things you've seen
with your own eyes. Run:  python3 replication_lab.py

Then do the exercises in README.md — they all involve editing the
CONFIG block below and predicting the output BEFORE re-running.
"""

from __future__ import annotations

import math
import random

# ---------------------------------------------------------------- CONFIG
# The exercises in README.md ask you to change these and predict results.
WRITES = 20_000            # write→read trials per table row (experiments 1-2)
N_FOLLOWERS = 3            # followers behind the leader (experiments 1-2)
REPL_MEDIAN_MS = 30.0      # median replication delay, leader -> follower
REPL_SIGMA = 0.8           # lognormal spread of that delay (tail heaviness)
READ_DELAYS_MS = [0, 5, 10, 25, 50, 100, 250, 500]  # experiment 1 sweep
SESSION_READ_DELAY_MS = 10.0   # experiment 2: read this long after writing
N_REPLICAS = 3             # experiment 3: quorum group size
QUORUM_TRIALS = 20_000     # experiment 3: trials per (W, R) combo
NINES = [0.999, 0.9999, 0.99999]   # experiment 4: availability levels
COMPOSED = 0.999           # experiment 4: availability of each of 2 services
SEED = 7
# -----------------------------------------------------------------------

MINUTES_PER_YEAR = 525_600.0


def repl_delay(rng: random.Random) -> float:
    """Time (ms) for one write to reach one follower: lognormal — most
    replication is fast, but network hiccups and follower GC make a tail."""
    return rng.lognormvariate(math.log(REPL_MEDIAN_MS), REPL_SIGMA)


def prob_follower_stale(read_delay_ms: float) -> float:
    """Analytic P(follower hasn't applied the write yet at read time)."""
    if read_delay_ms <= 0:
        return 1.0
    z = (math.log(read_delay_ms) - math.log(REPL_MEDIAN_MS)) / REPL_SIGMA
    return 0.5 * math.erfc(z / math.sqrt(2))


def experiment_1_stale_reads(rng: random.Random) -> None:
    print("=" * 78)
    print("EXPERIMENT 1 — write, then read from a random replica (leader + "
          f"{N_FOLLOWERS} followers)")
    print("=" * 78)
    print(f"replication delay: lognormal, median {REPL_MEDIAN_MS:.0f} ms, "
          f"sigma {REPL_SIGMA}; reads load-balanced over all "
          f"{N_FOLLOWERS + 1} nodes\n")
    frac_followers = N_FOLLOWERS / (N_FOLLOWERS + 1)
    for t in READ_DELAYS_MS:
        stale = 0
        for _ in range(WRITES):
            node = rng.randrange(N_FOLLOWERS + 1)   # 0 = leader, always fresh
            if node > 0 and repl_delay(rng) > t:
                stale += 1
        theory = frac_followers * prob_follower_stale(t)
        print(f"  read {t:4d} ms after write   stale reads: "
              f"measured={stale / WRITES:6.1%}   theory={theory:6.1%}")
    print("\n  -> 'write then immediately read' is a coin flip against the lag.")
    print("     Waiting out the median delay still leaves the TAIL of slow "
          "replicas.\n")


def experiment_2_read_your_writes(rng: random.Random) -> None:
    print("=" * 78)
    print("EXPERIMENT 2 — read-your-writes via session pinning to the leader")
    print("=" * 78)
    print(f"each session writes, then reads {SESSION_READ_DELAY_MS:.0f} ms "
          "later\n")
    stale_random = 0
    leader_reads_random = 0
    for _ in range(WRITES):
        node = rng.randrange(N_FOLLOWERS + 1)
        if node == 0:
            leader_reads_random += 1
        elif repl_delay(rng) > SESSION_READ_DELAY_MS:
            stale_random += 1
    print(f"  policy: random replica     stale={stale_random / WRITES:6.1%}   "
          f"leader serves {leader_reads_random / WRITES:5.1%} of reads")
    print(f"  policy: pin to leader      stale={0:6.1%}   "
          f"leader serves {1:5.1%} of reads")
    load_factor = WRITES / leader_reads_random
    print(f"\n  -> stale reads go to zero, but the leader's read load "
          f"jumps {load_factor:.1f}x.")
    print("     Read-your-writes is bought with leader capacity, not magic.\n")


def experiment_3_quorum(rng: random.Random) -> None:
    print("=" * 78)
    print(f"EXPERIMENT 3 — quorum reads/writes, N={N_REPLICAS} "
          "(write acked after W applies; read asks R, keeps freshest)")
    print("=" * 78)
    print("read fires the instant the write is acknowledged — worst case\n")
    for w in range(1, N_REPLICAS + 1):
        for r in range(1, N_REPLICAS + 1):
            stale = 0
            for _ in range(QUORUM_TRIALS):
                delays = [repl_delay(rng) for _ in range(N_REPLICAS)]
                ack_time = sorted(delays)[w - 1]        # W-th replica applies
                chosen = rng.sample(range(N_REPLICAS), r)
                if min(delays[i] for i in chosen) > ack_time:
                    stale += 1
            guaranteed = "yes" if r + w > N_REPLICAS else "no "
            print(f"  W={w} R={r}   R+W>N: {guaranteed}   "
                  f"stale reads: {stale / QUORUM_TRIALS:7.3%}")
    print("\n  -> every R+W>N row is exactly 0.000%: the read set MUST "
          "overlap the write set.")
    print("     Every other row leaks stale reads. Overlap is arithmetic, "
          "not luck.\n")


def experiment_4_availability_math() -> None:
    print("=" * 78)
    print("EXPERIMENT 4 — availability math (no simulation, just arithmetic)")
    print("=" * 78)
    print("what the nines actually buy you:\n")
    for a in NINES:
        down_min = (1 - a) * MINUTES_PER_YEAR
        print(f"  {a:8.3%} available   ->  {down_min:8.1f} min of downtime/yr "
              f"({down_min / 60:6.2f} h)")
    serial = COMPOSED * COMPOSED
    parallel = 1 - (1 - COMPOSED) ** 2
    print(f"\ncomposing two services that are each {COMPOSED:.1%} available:\n")
    for label, a in (("in series (A calls B)", serial),
                     ("in parallel (A or B)", parallel)):
        down_min = (1 - a) * MINUTES_PER_YEAR
        print(f"  {label:<22} availability={a:9.4%}   "
              f"downtime={down_min:8.1f} min/yr")
    print("\n  -> every serial dependency multiplies availabilities "
          "(subtracts nines);")
    print("     parallel redundancy multiplies failure probabilities "
          "(adds nines).\n")


def main() -> None:
    rng = random.Random(SEED)
    experiment_1_stale_reads(rng)
    experiment_2_read_your_writes(rng)
    experiment_3_quorum(rng)
    experiment_4_availability_math()
    print("Done. Now do the README exercises: predict, edit CONFIG, re-run, "
          "compare.")


if __name__ == "__main__":
    main()
