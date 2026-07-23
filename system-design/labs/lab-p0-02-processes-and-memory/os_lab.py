"""Lab p0-02 — Processes and Memory.

Four experiments that turn the OS lesson's claims into numbers:
  1. what a thread costs vs a fork vs a freshly spawned process
  2. virtual memory is lazy: allocation is free, first touch is not
  3. an LRU paging simulator that walks off the thrashing cliff
  4. the price of a context switch (thread ping-pong)

Run:  python3 os_lab.py        (stdlib only, finishes well under 60 s)

Then do the exercises in README.md — they all involve editing the
CONFIG block below and predicting the output BEFORE re-running.
"""

from __future__ import annotations

import multiprocessing as mp
import os
import random
import threading
import time
from collections import OrderedDict

# ---------------------------------------------------------------- CONFIG
# The exercises in README.md ask you to change these and predict results.
CONFIG = {
    "THREADS": 200,            # exp 1: threads to create + join
    "FORKS": 50,               # exp 1: os.fork() children (skipped on Windows)
    "SPAWNS": 6,               # exp 1: spawned fresh-interpreter processes
    "ALLOC_MB": 256,           # exp 2: buffer size in MiB
    "PAGE_BYTES": 4096,        # exp 2/3: page size
    "RAM_PAGES": 256,          # exp 3: simulated physical frames
    "WORKING_SETS": [64, 128, 224, 256, 288, 384, 512],  # exp 3: pages touched
    "SIM_ACCESSES": 60_000,    # exp 3: memory accesses per run
    "HIT_COST_US": 0.1,        # exp 3: RAM access = 100 ns
    "FAULT_COST_US": 1_000.0,  # exp 3: swap-in from SSD ≈ 1 ms
    "PINGPONGS": 2_000,        # exp 4: thread round trips
    "SEED": 7,
}
# -----------------------------------------------------------------------


def _noop() -> None:
    """Cheapest possible unit of work — we are timing creation, not work."""


def _time_threads(n: int) -> float:
    t0 = time.perf_counter()
    threads = [threading.Thread(target=_noop) for _ in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return time.perf_counter() - t0


def _time_forks(n: int) -> float:
    t0 = time.perf_counter()
    for _ in range(n):
        pid = os.fork()
        if pid == 0:  # child: exit immediately, skipping cleanup handlers
            os._exit(0)
        os.waitpid(pid, 0)
    return time.perf_counter() - t0


def _time_spawns(n: int) -> float:
    ctx = mp.get_context("spawn")
    t0 = time.perf_counter()
    procs = [ctx.Process(target=_noop) for _ in range(n)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    return time.perf_counter() - t0


def experiment_1_creation_cost() -> None:
    print("=" * 78)
    print("EXPERIMENT 1 — what does one unit of concurrency cost to CREATE?")
    print("=" * 78)
    rows: list[tuple[str, int, float]] = []

    if hasattr(os, "fork"):
        rows.append(("os.fork() + exit + wait", CONFIG["FORKS"], _time_forks(CONFIG["FORKS"])))
    else:
        print("  (os.fork unavailable on this platform — skipping fork row)")
    rows.append(("thread (same process)", CONFIG["THREADS"], _time_threads(CONFIG["THREADS"])))
    rows.append(("spawn (new interpreter)", CONFIG["SPAWNS"], _time_spawns(CONFIG["SPAWNS"])))

    per_unit = {label: total / count * 1e6 for label, count, total in rows}
    base = min(per_unit.values())
    print(f"\n  {'kind':<26}{'count':>6}{'total ms':>11}{'per-unit µs':>13}{'vs cheapest':>12}")
    for label, count, total in rows:
        us = per_unit[label]
        print(f"  {label:<26}{count:>6}{total * 1e3:>11.1f}{us:>13.1f}{us / base:>11.1f}x")
    print("\n  -> a thread shares the address space, so it is cheap; fork copies")
    print("     page tables (copy-on-write); spawn boots a whole interpreter.")
    print("     This gap is why servers pre-fork / pool instead of creating per request.\n")


def experiment_2_lazy_memory() -> None:
    print("=" * 78)
    print("EXPERIMENT 2 — allocation is a promise; first touch pays for it")
    print("=" * 78)
    n = CONFIG["ALLOC_MB"] * 1024 * 1024
    page = CONFIG["PAGE_BYTES"]
    npages = n // page

    t0 = time.perf_counter()
    buf = bytearray(n)
    alloc_s = time.perf_counter() - t0

    t0 = time.perf_counter()
    for i in range(0, n, page):
        buf[i] = 1  # first write to each page -> page fault, frame mapped
    first_s = time.perf_counter() - t0

    t0 = time.perf_counter()
    for i in range(0, n, page):
        buf[i] = 2  # same loop, pages already resident
    second_s = time.perf_counter() - t0

    per_fault_us = max(first_s - second_s, 0.0) / npages * 1e6
    print(f"  buffer: {CONFIG['ALLOC_MB']} MiB = {npages:,} pages of {page} B")
    print(f"  {'step':<38}{'time ms':>10}")
    print(f"  {'allocate (bytearray)':<38}{alloc_s * 1e3:>10.1f}")
    print(f"  {'first touch  (1 write per page)':<38}{first_s * 1e3:>10.1f}")
    print(f"  {'second touch (same loop, resident)':<38}{second_s * 1e3:>10.1f}")
    print(f"\n  -> first pass / second pass = {first_s / max(second_s, 1e-9):.1f}x;")
    print(f"     implied soft page-fault cost ≈ {per_fault_us:.2f} µs per page.")
    print("     'We allocated the buffer at startup' does NOT mean the memory is there.\n")


def _lru_faults(ram_pages: int, working_set: int, accesses: int, rng: random.Random) -> int:
    resident: OrderedDict[int, bool] = OrderedDict()
    faults = 0
    for _ in range(accesses):
        p = rng.randrange(working_set)
        if p in resident:
            resident.move_to_end(p)
        else:
            faults += 1
            if len(resident) >= ram_pages:
                resident.popitem(last=False)  # evict least-recently-used
            resident[p] = True
    return faults


def experiment_3_thrashing_cliff() -> None:
    print("=" * 78)
    print("EXPERIMENT 3 — the thrashing cliff (LRU paging simulator)")
    print("=" * 78)
    ram = CONFIG["RAM_PAGES"]
    hit_us, fault_us = CONFIG["HIT_COST_US"], CONFIG["FAULT_COST_US"]
    rng = random.Random(CONFIG["SEED"])
    print(f"  simulated RAM = {ram} frames; uniform random access over the working set")
    print(f"  costs: hit {hit_us} µs, hard fault {fault_us:.0f} µs\n")
    print(f"  {'working set':>12}{'fits?':>7}{'fault rate':>12}{'eff access µs':>15}{'slowdown':>10}")
    for ws in CONFIG["WORKING_SETS"]:
        faults = _lru_faults(ram, ws, CONFIG["SIM_ACCESSES"], rng)
        rate = faults / CONFIG["SIM_ACCESSES"]
        eff = (1 - rate) * hit_us + rate * fault_us
        fits = "yes" if ws <= ram else "NO"
        print(f"  {ws:>12}{fits:>7}{rate:>11.1%}{eff:>15.2f}{eff / hit_us:>9.0f}x")
    print("\n  -> below RAM size: ~free after warm-up. A few % past RAM: 100-1000x")
    print("     slower. Nothing degrades gracefully here — that is thrashing,")
    print("     and it is why serving boxes run with swap disabled.\n")


def experiment_4_context_switch() -> None:
    print("=" * 78)
    print("EXPERIMENT 4 — the price of a context switch (thread ping-pong)")
    print("=" * 78)
    n = CONFIG["PINGPONGS"]

    t0 = time.perf_counter()
    for _ in range(2 * n):
        _noop()
    call_us = (time.perf_counter() - t0) / (2 * n) * 1e6

    ping, pong = threading.Event(), threading.Event()

    def player(mine: threading.Event, other: threading.Event) -> None:
        for _ in range(n):
            mine.wait()
            mine.clear()
            other.set()

    t1 = threading.Thread(target=player, args=(ping, pong))
    t2 = threading.Thread(target=player, args=(pong, ping))
    t1.start()
    t2.start()
    t0 = time.perf_counter()
    ping.set()  # kick off the rally
    t1.join()
    t2.join()
    total = time.perf_counter() - t0
    switch_us = total / (2 * n) * 1e6

    print(f"  {n:,} round trips = {2 * n:,} hand-offs in {total * 1e3:.1f} ms")
    print(f"  per hand-off ≈ {switch_us:.1f} µs   (plain function call: {call_us:.3f} µs)")
    print(f"\n  -> every hand-off is ~{switch_us / max(call_us, 1e-9):.0f}x a function call, before")
    print("     counting the caches and TLB entries the next thread finds cold.")
    print("     Oversubscribe cores and this tax is charged on your p99.\n")


def main() -> None:
    t0 = time.perf_counter()
    experiment_1_creation_cost()
    experiment_2_lazy_memory()
    experiment_3_thrashing_cliff()
    experiment_4_context_switch()
    print(f"Done in {time.perf_counter() - t0:.1f} s. "
          "Now do the README exercises: predict, edit CONFIG, re-run, compare.")


if __name__ == "__main__":
    main()
