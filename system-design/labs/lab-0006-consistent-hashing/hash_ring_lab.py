"""Lab 0006 — Consistent Hashing.

Four experiments that turn Lesson 0006's claims into things you've seen
with your own eyes. Run:  python3 hash_ring_lab.py

Then do the exercises in README.md — they all involve editing the
CONFIG block below and predicting the output BEFORE re-running.
"""

from __future__ import annotations

import bisect
import hashlib
import random
import statistics

# ---------------------------------------------------------------- CONFIG
# The exercises in README.md ask you to change these and predict results.
NUM_KEYS = 100_000        # keys mapped in experiments 1-3
NUM_NODES = 5             # starting cluster size
RING_VNODES = 100         # virtual nodes per physical node (experiments 1, 2, 4)
VNODE_SWEEP = [1, 10, 100, 500]   # experiment 3: load smoothing
ZIPF_KEYS = 10_000        # experiment 4: distinct keys with zipf popularity
ZIPF_EXPONENT = 1.1       # popularity of rank r ~ 1 / r^s  (bigger s = hotter head)
SEED = 7
# -----------------------------------------------------------------------


def stable_hash(value: str) -> int:
    """Deterministic 64-bit hash (Python's built-in hash() is salted per run)."""
    digest = hashlib.sha1(value.encode()).digest()
    return int.from_bytes(digest[:8], "big")


def mod_n_map(keys: list[str], nodes: list[str]) -> dict[str, str]:
    """The naive scheme: node = hash(key) % N."""
    return {k: nodes[stable_hash(k) % len(nodes)] for k in keys}


class HashRing:
    """Consistent-hash ring with virtual nodes. Lookup = first point clockwise."""

    def __init__(self, nodes: list[str], vnodes: int) -> None:
        points = sorted(
            (stable_hash(f"{node}#vnode-{v}"), node)
            for node in nodes
            for v in range(vnodes)
        )
        self._hashes = [h for h, _ in points]
        self._owners = [node for _, node in points]

    def lookup(self, key: str) -> str:
        idx = bisect.bisect_right(self._hashes, stable_hash(key)) % len(self._hashes)
        return self._owners[idx]

    def map_keys(self, keys: list[str]) -> dict[str, str]:
        return {k: self.lookup(k) for k in keys}


def moved_fraction(before: dict[str, str], after: dict[str, str]) -> float:
    return sum(1 for k in before if before[k] != after[k]) / len(before)


def node_names(n: int) -> list[str]:
    return [f"node-{i}" for i in range(n)]


def counts_by_node(mapping: dict[str, str], nodes: list[str]) -> dict[str, int]:
    counts = {node: 0 for node in nodes}
    for owner in mapping.values():
        counts[owner] += 1
    return counts


def experiment_1_add_a_node(keys: list[str]) -> None:
    print("=" * 78)
    print(f"EXPERIMENT 1 — add a node: {NUM_NODES} -> {NUM_NODES + 1} "
          f"({len(keys):,} keys)")
    print("=" * 78)
    old_nodes, new_nodes = node_names(NUM_NODES), node_names(NUM_NODES + 1)

    mod_moved = moved_fraction(mod_n_map(keys, old_nodes), mod_n_map(keys, new_nodes))
    ring_before = HashRing(old_nodes, RING_VNODES).map_keys(keys)
    ring_after = HashRing(new_nodes, RING_VNODES).map_keys(keys)
    ring_moved = moved_fraction(ring_before, ring_after)

    ideal = 1 / (NUM_NODES + 1)
    print(f"  {'scheme':<22}{'keys moved':>10}    theory")
    print(f"  {'mod-N  hash(key)%N':<22}{mod_moved:>10.1%}    ~{1 - ideal:.0%}"
          f" (stays only if hash%{NUM_NODES} == hash%{NUM_NODES + 1})")
    print(f"  {f'ring   ({RING_VNODES} vnodes)':<22}{ring_moved:>10.1%}    ~{ideal:.0%}"
          f" (only the new node's arc)")
    print(f"\n  -> one added machine reshuffles {mod_moved:.0%} of the dataset under mod-N,"
          f"\n     but only {ring_moved:.0%} under the ring — and those keys all move TO the"
          f"\n     new node. This is why every distributed KV store uses a ring.\n")


def experiment_2_remove_a_node(keys: list[str]) -> None:
    print("=" * 78)
    print(f"EXPERIMENT 2 — remove a node: {NUM_NODES} -> {NUM_NODES - 1} "
          f"({len(keys):,} keys)")
    print("=" * 78)
    old_nodes = node_names(NUM_NODES)
    survivors = old_nodes[:-1]          # node with the highest index dies

    mod_moved = moved_fraction(mod_n_map(keys, old_nodes), mod_n_map(keys, survivors))
    ring_before = HashRing(old_nodes, RING_VNODES).map_keys(keys)
    ring_after = HashRing(survivors, RING_VNODES).map_keys(keys)
    ring_moved = moved_fraction(ring_before, ring_after)

    ideal = 1 / NUM_NODES
    print(f"  {'scheme':<22}{'keys moved':>10}    theory")
    print(f"  {'mod-N  hash(key)%N':<22}{mod_moved:>10.1%}    almost everything reshuffles")
    print(f"  {f'ring   ({RING_VNODES} vnodes)':<22}{ring_moved:>10.1%}    ~{ideal:.0%}"
          f" (exactly the dead node's keys)")
    print(f"\n  -> under the ring, a node failure disturbs only the keys it owned;"
          f"\n     every other key keeps its owner. Failures are the COMMON case at"
          f"\n     scale — this property is not optional.\n")


def experiment_3_vnode_smoothing(keys: list[str]) -> None:
    print("=" * 78)
    print(f"EXPERIMENT 3 — virtual nodes smooth the load "
          f"({NUM_NODES} nodes, {len(keys):,} keys)")
    print("=" * 78)
    nodes = node_names(NUM_NODES)
    fair = len(keys) / NUM_NODES
    print(f"  fair share = {fair:,.0f} keys/node\n")
    print(f"  {'vnodes':>6}  {'min':>8}  {'max':>8}  {'stddev':>8}  {'max/fair':>9}")
    for vnodes in VNODE_SWEEP:
        counts = counts_by_node(HashRing(nodes, vnodes).map_keys(keys), nodes)
        values = list(counts.values())
        print(f"  {vnodes:>6}  {min(values):>8,}  {max(values):>8,}  "
              f"{statistics.pstdev(values):>8,.0f}  {max(values) / fair:>8.2f}x")
    print(f"\n  -> with 1 vnode, arc sizes are luck: one node can own several times"
          f"\n     its share. Hundreds of vnodes average the arcs out — that is the"
          f"\n     whole reason Cassandra defaults to 256 tokens per node.\n")


def experiment_4_hot_keys(rng: random.Random) -> None:
    print("=" * 78)
    print(f"EXPERIMENT 4 — hot-key reality check "
          f"(zipf s={ZIPF_EXPONENT}, {ZIPF_KEYS:,} keys, {RING_VNODES} vnodes)")
    print("=" * 78)
    nodes = node_names(NUM_NODES)
    ring = HashRing(nodes, RING_VNODES)

    keys = [f"user:{i}" for i in range(ZIPF_KEYS)]
    rng.shuffle(keys)                                # random rank -> key assignment
    weights = [1.0 / (rank + 1) ** ZIPF_EXPONENT for rank in range(ZIPF_KEYS)]
    total = sum(weights)

    count_share = {node: 0.0 for node in nodes}
    load_share = {node: 0.0 for node in nodes}
    for key, weight in zip(keys, weights):
        owner = ring.lookup(key)
        count_share[owner] += 1 / ZIPF_KEYS
        load_share[owner] += weight / total

    print(f"  {'node':<8}  {'key-count share':>15}  {'traffic share':>13}")
    for node in nodes:
        print(f"  {node:<8}  {count_share[node]:>15.1%}  {load_share[node]:>13.1%}")

    hottest = max(nodes, key=lambda n: load_share[n])
    top_key_share = weights[0] / total
    print(f"\n  {'hottest key alone':<24}= {top_key_share:.1%} of all traffic")
    print(f"  {f'hottest node ({hottest})':<24}= {load_share[hottest]:.1%} of all traffic "
          f"(fair share {1 / NUM_NODES:.0%})")
    print(f"\n  -> the ring balanced key COUNTS (~{1 / NUM_NODES:.0%} each) but not LOAD:"
          f"\n     whichever node drew the zipf head is overloaded. More vnodes cannot"
          f"\n     fix this — you need hot-key replication or a cache in front (0007).\n")


def main() -> None:
    rng = random.Random(SEED)
    keys = [f"key-{i}" for i in range(NUM_KEYS)]
    experiment_1_add_a_node(keys)
    experiment_2_remove_a_node(keys)
    experiment_3_vnode_smoothing(keys)
    experiment_4_hot_keys(rng)
    print("Done. Now do the README exercises: predict, edit CONFIG, re-run, compare.")


if __name__ == "__main__":
    main()
