"""Lab 0012 — LSM vs B-tree.

Two toy storage engines built from scratch, racing on the same workload.
Run:  python3 lsm_btree_lab.py

The mini-LSM: a dict memtable flushed at a threshold into sorted immutable
"SSTables", size-tiered compaction, and a perfect bloom-filter stand-in
(a set of keys per table). The mini-"B-tree": pages of sorted keys behind
a tiny buffer pool, in-place inserts, page splits, dirty-page flushes.

Cost proxy everywhere = entries touched / comparisons made / entries
rewritten. No real disk, so runs are exact and reproducible (seeded RNG).

Then do the exercises in README.md — edit the CONFIG block and predict
the output BEFORE re-running.
"""

from __future__ import annotations

import bisect
import math
import random
from collections import OrderedDict

# ---------------------------------------------------------------- CONFIG
# The exercises in README.md ask you to change these and predict results.
NUM_KEYS = 100_000            # unique keys inserted into each engine
KEY_PATTERN = "sequential"    # "sequential" or "random" insert order (E3)
MEMTABLE_LIMIT = 2_000        # LSM: flush memtable at this many entries (E1)
TIER_FANOUT = 4               # LSM: merge a tier when it holds this many tables
COMPACTION_ENABLED = True     # LSM: turn off to watch reads rot (E4)
BLOOM_ENABLED = True          # LSM: per-table key set standing in for a bloom (E2)
PAGE_SIZE = 64                # B-tree: max entries per page
BUFFER_POOL_PAGES = 32        # B-tree: cached pages before dirty eviction
POINT_READS = 1_000           # reads per category in experiment 2
RANGE_SCANS = 200             # scans in experiment 3
RANGE_SPAN = 100              # key-span of each range scan
SEED = 12
# -----------------------------------------------------------------------


class MiniLSM:
    """Memtable -> sorted SSTables -> size-tiered compaction."""

    def __init__(self) -> None:
        self.memtable: dict[int, bool] = {}
        self.tables: list[dict] = []          # oldest -> newest
        self.inserted = 0
        self.flush_entries = 0                # entries written by flushes
        self.compact_entries = 0              # entries rewritten by compaction

    def put(self, key: int) -> None:
        self.inserted += 1
        self.memtable[key] = True
        if len(self.memtable) >= MEMTABLE_LIMIT:
            self._flush()

    def _flush(self) -> None:
        keys = sorted(self.memtable)
        self.tables.append({"keys": keys, "bloom": set(keys)})
        self.flush_entries += len(keys)
        self.memtable = {}
        if COMPACTION_ENABLED:
            self._maybe_compact()

    def _tier(self, table: dict) -> int:
        ratio = max(len(table["keys"]) // MEMTABLE_LIMIT, 1)
        return int(math.log(ratio, TIER_FANOUT))

    def _maybe_compact(self) -> None:
        while True:
            tiers: dict[int, list[int]] = {}
            for i, t in enumerate(self.tables):
                tiers.setdefault(self._tier(t), []).append(i)
            victim = next((idx for _, idx in sorted(tiers.items())
                           if len(idx) >= TIER_FANOUT), None)
            if victim is None:
                return
            merged: set[int] = set()
            for i in victim:
                merged.update(self.tables[i]["keys"])
            keys = sorted(merged)
            self.compact_entries += len(keys)     # entries rewritten to disk
            self.tables = [t for i, t in enumerate(self.tables) if i not in victim]
            self.tables.insert(victim[0], {"keys": keys, "bloom": set(keys)})

    def finish_load(self) -> None:
        if self.memtable:
            self._flush()

    @property
    def write_amp(self) -> float:
        return (self.flush_entries + self.compact_entries) / max(self.inserted, 1)

    def point_read(self, key: int, use_bloom: bool) -> int:
        """Returns cost (comparisons + bloom probes) for one lookup."""
        cost = 1                                  # memtable check
        if key in self.memtable:
            return cost
        for t in reversed(self.tables):           # newest first
            if use_bloom:
                cost += 1                         # bloom probe
                if key not in t["bloom"]:
                    continue
            keys = t["keys"]
            cost += len(keys).bit_length()        # ~log2 N binary-search steps
            i = bisect.bisect_left(keys, key)
            if i < len(keys) and keys[i] == key:
                return cost
        return cost

    def range_scan(self, start: int) -> int:
        """Scan keys in [start, start+RANGE_SPAN). Cost = entries touched."""
        end = start + RANGE_SPAN
        cost = 1
        cost += sum(1 for k in self.memtable if start <= k < end)
        for t in self.tables:                     # EVERY table must be consulted
            keys = t["keys"]
            cost += len(keys).bit_length()
            i = bisect.bisect_left(keys, start)
            while i < len(keys) and keys[i] < end:
                cost += 1
                i += 1
        return cost


class MiniBTree:
    """Sorted pages + tiny buffer pool. In-place inserts, splits, dirty flushes."""

    def __init__(self) -> None:
        self.pages: list[list[int]] = [[]]
        self.firsts: list[int] = [0]              # directory: first key per page
        self.cache: OrderedDict[int, list] = OrderedDict()  # id(page) -> [page, dirty]
        self.inserts = 0
        self.entries_flushed = 0                  # entries in flushed pages
        self.page_flushes = 0
        self.splits = 0

    def _touch(self, page: list[int], dirty: bool) -> None:
        pid = id(page)
        if pid in self.cache:
            self.cache.move_to_end(pid)
            self.cache[pid][1] = self.cache[pid][1] or dirty
            return
        self.cache[pid] = [page, dirty]
        if len(self.cache) > BUFFER_POOL_PAGES:
            _, (old, was_dirty) = self.cache.popitem(last=False)
            if was_dirty:                         # evicting dirty page = page write
                self.page_flushes += 1
                self.entries_flushed += len(old)

    def _find(self, key: int) -> int:
        return max(bisect.bisect_right(self.firsts, key) - 1, 0)

    def insert(self, key: int) -> None:
        self.inserts += 1
        i = self._find(key)
        page = self.pages[i]
        bisect.insort(page, key)
        self._touch(page, dirty=True)
        if len(page) > PAGE_SIZE:
            self._split(i)

    def _split(self, i: int) -> None:
        self.splits += 1
        page = self.pages[i]
        mid = len(page) // 2
        left, right = page[:mid], page[mid:]
        self.pages[i] = left
        self.pages.insert(i + 1, right)
        self.firsts[i] = left[0]
        self.firsts.insert(i + 1, right[0])
        self.cache.pop(id(page), None)
        self.page_flushes += 2                    # a split writes both halves
        self.entries_flushed += len(left) + len(right)
        self._touch(left, dirty=False)
        self._touch(right, dirty=False)

    def finish_load(self) -> None:
        for page, dirty in self.cache.values():
            if dirty:
                self.page_flushes += 1
                self.entries_flushed += len(page)
        self.cache.clear()

    @property
    def write_amp(self) -> float:
        return self.entries_flushed / max(self.inserts, 1)

    def point_read(self, key: int) -> int:
        i = self._find(key)
        return len(self.pages).bit_length() + max(len(self.pages[i]), 1).bit_length()

    def range_scan(self, start: int) -> int:
        end = start + RANGE_SPAN
        i = self._find(start)
        cost = len(self.pages).bit_length()
        while i < len(self.pages):                # pages are contiguous & sorted
            page = self.pages[i]
            j = bisect.bisect_left(page, start)
            while j < len(page) and page[j] < end:
                cost += 1
                j += 1
            if page and page[-1] >= end:
                break
            i += 1
            cost += 1                             # step to sibling page
        return cost


def build_engines() -> tuple[MiniLSM, MiniBTree, list[int]]:
    rng = random.Random(SEED)
    keys = list(range(NUM_KEYS))
    if KEY_PATTERN == "random":
        rng.shuffle(keys)
    lsm, btree = MiniLSM(), MiniBTree()
    for k in keys:
        lsm.put(k)
        btree.insert(k)
    lsm.finish_load()
    btree.finish_load()
    return lsm, btree, keys


def experiment_1_write_cost(lsm: MiniLSM, btree: MiniBTree) -> None:
    print("=" * 78)
    print(f"EXPERIMENT 1 — write {NUM_KEYS:,} keys ({KEY_PATTERN} order), "
          f"memtable={MEMTABLE_LIMIT:,}, page={PAGE_SIZE}")
    print("=" * 78)
    print(f"  {'engine':<10} {'entries written':>15} {'rewrites/flushes':>17} "
          f"{'write amp':>10}   structure at end")
    lsm_total = lsm.flush_entries + lsm.compact_entries
    print(f"  {'mini-LSM':<10} {lsm_total:>15,} "
          f"{'compact ' + format(lsm.compact_entries, ','):>17} "
          f"{lsm.write_amp:>9.2f}x   {len(lsm.tables)} sstables")
    print(f"  {'mini-Btree':<10} {btree.entries_flushed:>15,} "
          f"{'flushes ' + format(btree.page_flushes, ','):>17} "
          f"{btree.write_amp:>9.2f}x   {len(btree.pages)} pages, "
          f"{btree.splits} splits")
    print("\n  -> LSM write amp = (flushed + compacted) / inserted: every entry is")
    print("     rewritten once per tier merge. B-tree write amp = whole pages")
    print("     rewritten per insert; sequential keys keep the hot page cached,")
    print("     random keys (E3) evict a dirty page for almost every insert.\n")


def experiment_2_point_reads(lsm: MiniLSM, btree: MiniBTree,
                             keys: list[int]) -> None:
    rng = random.Random(SEED + 1)
    hot = rng.choices(keys[-NUM_KEYS // 20:], k=POINT_READS)     # recent 5%
    cold = rng.choices(keys[:NUM_KEYS // 2], k=POINT_READS)      # oldest half
    missing = [NUM_KEYS + rng.randrange(NUM_KEYS) for _ in range(POINT_READS)]

    print("=" * 78)
    print(f"EXPERIMENT 2 — point reads, {POINT_READS:,} per row "
          f"(cost = comparisons + bloom probes)")
    print("=" * 78)
    print(f"  {'key set':<22} {'LSM + bloom':>11} {'LSM no bloom':>13} "
          f"{'B-tree':>7}")
    for label, sample in (("hot (recently written)", hot),
                          ("cold (written early)", cold),
                          ("missing (never written)", missing)):
        with_b = sum(lsm.point_read(k, True) for k in sample) / len(sample)
        no_b = sum(lsm.point_read(k, False) for k in sample) / len(sample)
        bt = sum(btree.point_read(k) for k in sample) / len(sample)
        print(f"  {label:<22} {with_b:>11.1f} {no_b:>13.1f} {bt:>7.1f}")
    print("\n  -> the B-tree pays one predictable tree descent for everything.")
    print("     The LSM checks memtable + tables newest-first: blooms make absent")
    print("     tables cost 1 probe instead of a binary search — the gap explodes")
    print("     on missing keys, which touch EVERY table without blooms (E2).\n")


def experiment_3_range_scans(lsm: MiniLSM, btree: MiniBTree) -> None:
    rng = random.Random(SEED + 2)
    starts = [rng.randrange(NUM_KEYS - RANGE_SPAN) for _ in range(RANGE_SCANS)]
    lsm_avg = sum(lsm.range_scan(s) for s in starts) / len(starts)
    bt_avg = sum(btree.range_scan(s) for s in starts) / len(starts)

    print("=" * 78)
    print(f"EXPERIMENT 3 — {RANGE_SCANS} range scans of {RANGE_SPAN} keys "
          f"(cost = entries + seeks touched)")
    print("=" * 78)
    print(f"  {'engine':<10} {'avg scan cost':>13}  note")
    print(f"  {'mini-LSM':<10} {lsm_avg:>13.1f}  must seek into all "
          f"{len(lsm.tables)} sstables and merge")
    print(f"  {'mini-Btree':<10} {bt_avg:>13.1f}  one descent, then walk "
          f"sibling pages in order")
    print("\n  -> blooms cannot help a range scan: 'no key in [a,b)' is not a")
    print("     membership question. Every extra sstable is a mandatory seek —")
    print("     this is read amplification, and compaction is what caps it (E4).\n")


def main() -> None:
    lsm, btree, keys = build_engines()
    experiment_1_write_cost(lsm, btree)
    experiment_2_point_reads(lsm, btree, keys)
    experiment_3_range_scans(lsm, btree)
    print("Done. Now do the README exercises: predict, edit CONFIG, re-run, compare.")


if __name__ == "__main__":
    main()
