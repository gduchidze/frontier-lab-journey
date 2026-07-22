"""Lab 0007 — Cache Lab.

Three experiments that turn Lesson 0007's claims into things you've seen
with your own eyes. Run:  python3 cache_lab.py

Everything is simulated — no network, no Redis. The "database" is a
counter that charges a fixed latency per access, so DB load is exact
and runs are reproducible (seeded RNG; experiment 3 uses threads, so
its counts are deterministic by construction, not by luck).

Then do the exercises in README.md — they all involve editing the
CONFIG block below and predicting the output BEFORE re-running.
"""

from __future__ import annotations

import bisect
import random
import threading
import time
from collections import OrderedDict

# ---------------------------------------------------------------- CONFIG
# The exercises in README.md ask you to change these and predict results.
NUM_KEYS = 50_000          # distinct keys in the keyspace
NUM_REQUESTS = 200_000     # requests per workload
ZIPF_S = 1.1               # skew exponent (1.0+ = "few keys get most traffic")
CACHE_SIZES = [100, 500, 2_000, 10_000]   # experiment 1 sweep
DB_READ_MS = 5.0           # simulated cost of one DB read
DB_WRITE_MS = 8.0          # simulated cost of one DB write
WRITE_FRACTION = 0.10      # experiment 2: fraction of ops that are writes
EXP2_CACHE_SIZE = 2_000    # experiment 2 cache capacity
STAMPEDE_THREADS = 50      # experiment 3: concurrent requesters
STAMPEDE_DB_LATENCY_S = 0.05   # real sleep per DB read in experiment 3 only
HOT_KEYS = 50              # experiment 3: hot keys for the jitter scenario
TTL_JITTER_FRAC = 0.5      # jitter as a fraction of base TTL
SEED = 7
# -----------------------------------------------------------------------


class SimDB:
    """A 'database' that only counts. Each access charges fixed latency."""

    def __init__(self, latency_s: float = 0.0) -> None:
        self.reads = 0
        self.writes = 0
        self._latency_s = latency_s   # real sleep: opens the race window
        self._lock = threading.Lock()

    def read(self, key: int) -> str:
        with self._lock:
            self.reads += 1
        if self._latency_s:
            time.sleep(self._latency_s)
        return f"value-{key}"

    def write(self, key: int) -> None:
        with self._lock:
            self.writes += 1

    @property
    def simulated_ms(self) -> float:
        return self.reads * DB_READ_MS + self.writes * DB_WRITE_MS


class LRUCache:
    """Classic LRU on OrderedDict: get moves to end, evict from front."""

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self._data: OrderedDict[int, str] = OrderedDict()

    def get(self, key: int) -> str | None:
        if key not in self._data:
            return None
        self._data.move_to_end(key)
        return self._data[key]

    def put(self, key: int, value: str) -> None:
        self._data[key] = value
        self._data.move_to_end(key)
        if len(self._data) > self.capacity:
            self._data.popitem(last=False)

    def invalidate(self, key: int) -> None:
        self._data.pop(key, None)


def zipf_workload(rng: random.Random, n_requests: int) -> list[int]:
    """Sample keys ~ Zipf(ZIPF_S): key rank k gets weight 1/k^s."""
    weights = [1.0 / (k ** ZIPF_S) for k in range(1, NUM_KEYS + 1)]
    cdf: list[float] = []
    total = 0.0
    for w in weights:
        total += w
        cdf.append(total)
    return [bisect.bisect_left(cdf, rng.random() * total) for _ in range(n_requests)]


def experiment_1_hit_rate_curve(workload: list[int]) -> None:
    print("=" * 78)
    print(f"EXPERIMENT 1 — LRU cache-aside, zipf({ZIPF_S}) reads: "
          f"{NUM_REQUESTS:,} requests over {NUM_KEYS:,} keys")
    print("=" * 78)
    print(f"  {'cache size':>10}  {'% of keys':>9}  {'hit rate':>8}  "
          f"{'DB reads':>9}  {'simulated DB time':>18}")
    prev_hit = None
    for size in CACHE_SIZES:
        cache, db, hits = LRUCache(size), SimDB(), 0
        for key in workload:
            if cache.get(key) is not None:
                hits += 1
            else:
                cache.put(key, db.read(key))       # cache-aside: load on miss
        hit_rate = hits / len(workload)
        delta = "" if prev_hit is None else f"  (+{(hit_rate - prev_hit) * 100:4.1f} pts)"
        prev_hit = hit_rate
        print(f"  {size:>10,}  {size / NUM_KEYS:>9.1%}  {hit_rate:>8.1%}  "
              f"{db.reads:>9,}  {db.simulated_ms / 1000:>16.1f} s{delta}")
    print("\n  -> each step multiplies cache size ~4-5x but buys fewer extra points:")
    print("     the hit-rate curve flattens. Size the cache at the knee, not the top.\n")


def experiment_2_update_patterns(rng: random.Random, workload: list[int]) -> None:
    print("=" * 78)
    print(f"EXPERIMENT 2 — cache-aside vs write-through "
          f"({1 - WRITE_FRACTION:.0%} reads / {WRITE_FRACTION:.0%} writes, "
          f"cache={EXP2_CACHE_SIZE:,})")
    print("=" * 78)
    ops = [(key, rng.random() < WRITE_FRACTION) for key in workload]

    results = []
    for policy in ("cache-aside", "write-through"):
        cache, db = LRUCache(EXP2_CACHE_SIZE), SimDB()
        reads = hits = 0
        for key, is_write in ops:
            if is_write:
                db.write(key)
                if policy == "cache-aside":
                    cache.invalidate(key)          # stale entry must go
                else:
                    cache.put(key, f"value-{key}")  # cache stays warm
            else:
                reads += 1
                if cache.get(key) is not None:
                    hits += 1
                else:
                    cache.put(key, db.read(key))
        results.append((policy, hits / reads, db.reads, db.writes, db.simulated_ms))

    print(f"  {'policy':<14} {'read hit rate':>13}  {'DB reads':>9}  "
          f"{'DB writes':>9}  {'total simulated DB load':>24}")
    for policy, hit_rate, db_reads, db_writes, ms in results:
        print(f"  {policy:<14} {hit_rate:>13.1%}  {db_reads:>9,}  "
              f"{db_writes:>9,}  {ms / 1000:>22.1f} s")
    print("\n  -> write-through pays the same DB writes but keeps hot keys warm,")
    print("     so reads miss less. Cache-aside invalidation re-buys hot keys from")
    print("     the DB after every write. Neither is free: write-through also fills")
    print("     the cache with keys nobody reads.\n")


def _stampede_run(n_threads: int, protected: bool) -> int:
    """One expired hot key, n_threads concurrent readers. Returns DB loads."""
    db = SimDB(latency_s=STAMPEDE_DB_LATENCY_S)
    cache: dict[int, str] = {}                     # hot key 0 already expired
    barrier = threading.Barrier(n_threads)
    key_lock = threading.Lock()                    # per-key lock (one key here)

    def unprotected_reader() -> None:
        barrier.wait()                             # everyone checks at once
        if 0 not in cache:                         # all see the miss...
            cache[0] = db.read(0)                  # ...all reload the DB

    def locked_reader() -> None:
        barrier.wait()
        if 0 not in cache:
            with key_lock:                         # only one recomputes
                if 0 not in cache:                 # double-check after wait
                    cache[0] = db.read(0)

    target = locked_reader if protected else unprotected_reader
    threads = [threading.Thread(target=target) for _ in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return db.reads


def _jitter_run(rng: random.Random) -> int:
    """HOT_KEYS keys cached at t=0 with jittered TTLs; burst just after the
    base TTL. Only keys whose jittered TTL already passed get reloaded."""
    db = SimDB(latency_s=STAMPEDE_DB_LATENCY_S)
    base_ttl = 60.0
    expiry = {k: base_ttl + rng.uniform(0, base_ttl * TTL_JITTER_FRAC)
              for k in range(HOT_KEYS)}
    now = base_ttl + base_ttl * TTL_JITTER_FRAC * 0.05   # burst moment
    barrier = threading.Barrier(STAMPEDE_THREADS)

    def reader(key: int) -> None:
        barrier.wait()
        if expiry[key] <= now:                     # this key's TTL is up
            db.read(key)

    threads = [threading.Thread(target=reader, args=(i % HOT_KEYS,))
               for i in range(STAMPEDE_THREADS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return db.reads


def experiment_3_stampede(rng: random.Random) -> None:
    print("=" * 78)
    print(f"EXPERIMENT 3 — stampede: hot key expires, "
          f"{STAMPEDE_THREADS} threads request it at once")
    print("=" * 78)
    naive = _stampede_run(STAMPEDE_THREADS, protected=False)
    locked = _stampede_run(STAMPEDE_THREADS, protected=True)
    jittered = _jitter_run(rng)

    rows = [
        ("no protection (1 hot key)", naive, "every miss dogpiles the DB"),
        ("per-key lock (1 hot key)", locked, "one recompute, rest wait"),
        (f"TTL jitter ({HOT_KEYS} hot keys)", jittered,
         "expiries decorrelated in time"),
    ]
    print(f"  {'scenario':<28} {'DB loads in burst':>17}   note")
    for label, loads, note in rows:
        print(f"  {label:<28} {loads:>17}   {note}")
    print(f"\n  -> unprotected: {naive} identical DB loads for ONE key — "
          f"a {naive}x self-inflicted spike.")
    print("     The lock collapses it to 1. Jitter doesn't stop reloads, it spreads")
    print("     them out so they never land in the same instant. Real systems use")
    print("     both (plus refresh-ahead for the keys they can predict).\n")


def main() -> None:
    rng = random.Random(SEED)
    workload = zipf_workload(rng, NUM_REQUESTS)
    experiment_1_hit_rate_curve(workload)
    experiment_2_update_patterns(rng, workload)
    experiment_3_stampede(rng)
    print("Done. Now do the README exercises: predict, edit CONFIG, re-run, compare.")


if __name__ == "__main__":
    main()
