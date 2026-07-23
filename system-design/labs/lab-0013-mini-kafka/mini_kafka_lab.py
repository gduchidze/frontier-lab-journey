"""Lab 0013 — Mini Kafka.

An in-memory partitioned log that turns Lesson 0013's claims into numbers:
per-partition ordering (and the death of global ordering), hot-key skew,
consumer-group parallelism limits, duplicate deliveries after a crash, and
log compaction. Run:  python3 mini_kafka_lab.py

Everything is simulated — no brokers, no network. "Processing time" is a
fixed cost per event, so throughput arithmetic is exact and runs are
reproducible (seeded RNG, deterministic CRC32 partitioner).

Then do the exercises in README.md — edit the CONFIG block below and
predict the output BEFORE re-running.
"""

from __future__ import annotations

import bisect
import random
import zlib
from collections import defaultdict
from dataclasses import dataclass

# ---------------------------------------------------------------- CONFIG
# The exercises in README.md ask you to change these and predict results.
NUM_EVENTS = 50_000        # events produced in experiment 1
NUM_PARTITIONS = 8         # partitions in the topic
NUM_KEYS = 5_000           # distinct keys (users / orders)
ZIPF_S = 1.1               # key skew (higher = a few keys dominate)
CONSUMER_COUNTS = [1, 2, 4, 8, 12]   # experiment 2 sweep
EVENT_COST_MS = 0.05       # simulated per-event processing cost
CRASH_CONSUMERS = 4        # consumer-group size for the crash scenario
COMMIT_EVERY = 500         # offset commit interval, in events
CRASH_FRACTION = 0.5       # crashed consumer dies after this share of its work
COMPACT_UPDATES = 30_000   # experiment 3: updates written to the changelog
COMPACT_KEYS = 2_000       # experiment 3: distinct keys in the changelog
POISON_OFFSET = None       # E4: e.g. 1_000 — poison pill at this offset of partition 0
SEED = 13
# -----------------------------------------------------------------------


@dataclass(frozen=True)
class Event:
    seq: int       # global produce order (what "global ordering" would need)
    key: int
    key_seq: int   # per-key sequence number (what partitioning preserves)


def partition_of(key: int, n_partitions: int) -> int:
    """Deterministic hash partitioner (Kafka's default is murmur2 % P)."""
    return zlib.crc32(str(key).encode()) % n_partitions


def zipf_keys(rng: random.Random, n: int, n_keys: int, s: float) -> list[int]:
    """Sample keys ~ Zipf(s): key rank k gets weight 1/k^s."""
    weights = [1.0 / (k ** s) for k in range(1, n_keys + 1)]
    cdf: list[float] = []
    total = 0.0
    for w in weights:
        total += w
        cdf.append(total)
    return [bisect.bisect_left(cdf, rng.random() * total) for _ in range(n)]


def produce(keys: list[int], n_partitions: int) -> list[list[Event]]:
    """Append keyed events to their partitions, preserving arrival order."""
    partitions: list[list[Event]] = [[] for _ in range(n_partitions)]
    key_seq: dict[int, int] = defaultdict(int)
    for seq, key in enumerate(keys):
        key_seq[key] += 1
        partitions[partition_of(key, n_partitions)].append(
            Event(seq, key, key_seq[key]))
    return partitions


# ---------------------------------------------------------- EXPERIMENT 1

def experiment_1_ordering_and_skew(partitions: list[list[Event]]) -> None:
    print("=" * 78)
    print(f"EXPERIMENT 1 — ordering & skew: {NUM_EVENTS:,} events, "
          f"{NUM_KEYS:,} zipf({ZIPF_S}) keys, {NUM_PARTITIONS} partitions")
    print("=" * 78)

    # Per-key ordering inside each partition: key_seq must be monotonic.
    per_key_violations = 0
    for part in partitions:
        last_seq: dict[int, int] = {}
        for ev in part:
            if ev.key in last_seq and ev.key_seq <= last_seq[ev.key]:
                per_key_violations += 1
            last_seq[ev.key] = ev.key_seq

    # Global ordering: merge partitions round-robin (what a consumer group
    # effectively sees) and count adjacent pairs that go backwards in time.
    merged: list[Event] = []
    cursors = [0] * len(partitions)
    remaining = sum(len(p) for p in partitions)
    while remaining:
        for i, part in enumerate(partitions):
            if cursors[i] < len(part):
                merged.append(part[cursors[i]])
                cursors[i] += 1
                remaining -= 1
    inversions = sum(1 for a, b in zip(merged, merged[1:]) if b.seq < a.seq)

    print(f"  per-key order violations inside partitions : {per_key_violations}")
    print(f"  global-order inversions in round-robin read: {inversions:,} "
          f"({inversions / len(merged):.0%} of adjacent pairs)")

    print(f"\n  partition sizes (even split would be "
          f"{NUM_EVENTS // NUM_PARTITIONS:,} = {1 / NUM_PARTITIONS:.1%} each):")
    print(f"  {'partition':>9}  {'events':>8}  {'share':>6}  {'vs even':>8}")
    even = NUM_EVENTS / NUM_PARTITIONS
    for i, part in enumerate(partitions):
        print(f"  {i:>9}  {len(part):>8,}  {len(part) / NUM_EVENTS:>6.1%}  "
              f"{len(part) / even:>7.2f}x")

    key_counts = defaultdict(int)
    for part in partitions:
        for ev in part:
            key_counts[ev.key] += 1
    top_key, top_n = max(key_counts.items(), key=lambda kv: kv[1])
    print(f"\n  hottest key: key={top_key} with {top_n:,} events "
          f"({top_n / NUM_EVENTS:.1%} of all traffic) — it pins partition "
          f"{partition_of(top_key, NUM_PARTITIONS)}")
    print("\n  -> per-key order survives partitioning; global order does not.")
    print("     Zipf keys make partitions unequal: the hot key's partition is")
    print("     the celebrity problem wearing a new hat.\n")


# ---------------------------------------------------------- EXPERIMENT 2

def experiment_2_consumer_groups(partitions: list[list[Event]]) -> None:
    print("=" * 78)
    print(f"EXPERIMENT 2 — consumer group over {NUM_PARTITIONS} partitions, "
          f"{EVENT_COST_MS} ms/event")
    print("=" * 78)
    print(f"  {'consumers':>9}  {'busy':>5}  {'idle':>5}  "
          f"{'busiest load':>12}  {'finish time':>11}  {'speedup':>7}")
    base_time = None
    for c in CONSUMER_COUNTS:
        # Round-robin partition assignment: consumer i owns partitions p
        # with p % c == i. A partition has exactly one owner in the group.
        loads = [0] * c
        for p, part in enumerate(partitions):
            loads[p % c] += len(part)
        busy = sum(1 for x in loads if x > 0)
        finish_s = max(loads) * EVENT_COST_MS / 1000
        if base_time is None:
            base_time = finish_s
        print(f"  {c:>9}  {busy:>5}  {c - busy:>5}  "
              f"{max(loads):>10,} ev  {finish_s:>9.2f} s  "
              f"{base_time / finish_s:>6.2f}x")
    print("\n  -> speedup stops at #partitions: extra consumers own nothing.")
    print("     And even below that cap, the hot partition sets the finish")
    print("     time — parallelism is per-partition, skew and all.\n")

    _crash_and_redeliver(partitions)
    if POISON_OFFSET is not None:
        _poison_pill(partitions)


def _crash_and_redeliver(partitions: list[list[Event]]) -> None:
    """Consumer 0 (of CRASH_CONSUMERS) dies mid-run; its partitions are
    reassigned. Compare commit-after-batch (at-least-once) with
    commit-before-batch (at-most-once)."""
    owned = [p for p in range(NUM_PARTITIONS) if p % CRASH_CONSUMERS == 0]
    total = sum(len(partitions[p]) for p in owned)
    crash_at = int(total * CRASH_FRACTION)

    # How far did consumer 0 get in each of its partitions before dying?
    progress: list[tuple[int, int]] = []   # (processed, partition length)
    done = 0
    for p in owned:
        plen = len(partitions[p])
        if done + plen <= crash_at:
            progress.append((plen, plen))          # finished this partition
            done += plen
        else:
            progress.append((max(0, crash_at - done), plen))
            done = crash_at
    processed = sum(pr for pr, _ in progress)

    dup = 0     # at-least-once: processed but not yet committed -> redelivered
    lost = 0    # at-most-once: committed ahead but never processed -> gone
    for pr, plen in progress:
        committed_after = (pr // COMMIT_EVERY) * COMMIT_EVERY if pr < plen else plen
        dup += pr - committed_after
        if pr < plen and pr % COMMIT_EVERY != 0:
            committed_before = min(plen, (pr // COMMIT_EVERY + 1) * COMMIT_EVERY)
        else:
            committed_before = pr
        lost += committed_before - pr

    print(f"  crash: consumer 0 of {CRASH_CONSUMERS} owns partitions {owned}, "
          f"dies after {processed:,}/{total:,} events (commit every "
          f"{COMMIT_EVERY})")
    print(f"  {'offset strategy':<34} {'duplicates':>10}  {'lost':>6}")
    print(f"  {'commit AFTER batch (at-least-once)':<34} {dup:>10,}  {0:>6}")
    print(f"  {'commit BEFORE batch (at-most-once)':<34} {0:>10,}  {lost:>6,}")
    print("\n  -> the gap between 'processed' and 'committed' at crash time is")
    print("     exactly your duplicate (or loss) budget. Pick which side of the")
    print("     ledger you'd rather be on — then make the consumer idempotent.\n")


def _poison_pill(partitions: list[list[Event]]) -> None:
    """A poison event at POISON_OFFSET of partition 0: without a DLQ the
    consumer retries forever and the partition blocks behind it."""
    plen = len(partitions[0])
    off = min(POISON_OFFSET, plen - 1)
    print(f"  poison pill at offset {off:,} of partition 0 ({plen:,} events):")
    print(f"  {'strategy':<22} {'processed':>9}  {'blocked':>8}  {'to DLQ':>6}")
    print(f"  {'retry forever':<22} {off:>9,}  {plen - off:>8,}  {0:>6}")
    print(f"  {'skip to DLQ':<22} {plen - 1:>9,}  {0:>8,}  {1:>6}")
    print("\n  -> one bad event can park an entire partition (and every key in")
    print("     it) forever. A dead-letter queue trades ordering for progress.\n")


# ---------------------------------------------------------- EXPERIMENT 3

def experiment_3_compaction(rng: random.Random) -> None:
    print("=" * 78)
    print(f"EXPERIMENT 3 — log compaction: {COMPACT_UPDATES:,} updates over "
          f"{COMPACT_KEYS:,} keys")
    print("=" * 78)
    keys = zipf_keys(rng, COMPACT_UPDATES, COMPACT_KEYS, ZIPF_S)
    full_log = [(k, f"v{i}") for i, k in enumerate(keys)]

    # Compaction keeps only the LAST record per key, preserving log order.
    last_index = {k: i for i, (k, _) in enumerate(full_log)}
    compacted = [full_log[i] for i in sorted(last_index.values())]

    state_full = {k: v for k, v in full_log}         # replay everything
    state_compact = {k: v for k, v in compacted}     # replay the changelog
    assert state_full == state_compact, "compaction must preserve final state"

    print(f"  {'log':<12} {'entries replayed':>16}  {'final state size':>16}")
    print(f"  {'full log':<12} {len(full_log):>16,}  {len(state_full):>16,}")
    print(f"  {'compacted':<12} {len(compacted):>16,}  {len(state_compact):>16,}")
    print(f"\n  -> identical final state from {len(compacted):,} entries instead "
          f"of {len(full_log):,} ({len(full_log) / len(compacted):.1f}x less replay).")
    print("     That is a changelog: latest-value-per-key. But every overwritten")
    print("     intermediate value is GONE — compaction keeps state, not history.\n")


def main() -> None:
    rng = random.Random(SEED)
    keys = zipf_keys(rng, NUM_EVENTS, NUM_KEYS, ZIPF_S)
    partitions = produce(keys, NUM_PARTITIONS)
    experiment_1_ordering_and_skew(partitions)
    experiment_2_consumer_groups(partitions)
    experiment_3_compaction(rng)
    print("Done. Now do the README exercises: predict, edit CONFIG, re-run, compare.")


if __name__ == "__main__":
    main()
