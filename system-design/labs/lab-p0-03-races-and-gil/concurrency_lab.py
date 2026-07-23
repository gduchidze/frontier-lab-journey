"""Lab p0-03 — Races, Locks, the GIL, and the Event Loop.

Four experiments that make Lesson p0-03's claims measurable. Run:

    python3 concurrency_lab.py

Then do the exercises in README.md — predict the output BEFORE editing
CONFIG and re-running.
"""

from __future__ import annotations

import asyncio
import multiprocessing
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

# ---------------------------------------------------------------- CONFIG
RACE_THREADS = 4            # threads incrementing the shared counter
RACE_INCREMENTS = 50_000    # increments per thread
RACE_TRIALS = 5             # repeat to show non-determinism
SWITCH_INTERVAL = 5e-6      # tiny = frequent preemption = more races (default 0.005)

DEADLOCK_TIMEOUT_S = 0.5    # how long a thread waits before declaring deadlock

CPU_CHUNK = 12_000_000      # loop iterations per CPU-bound task
CPU_TASKS = 4               # number of CPU-bound tasks (= workers)

IO_TASKS = 1_000            # fake I/O calls (each sleeps IO_MS)
IO_MS = 50                  # duration of one fake I/O call
THREAD_POOL_WORKERS = 50    # thread pool size for the I/O comparison
# -----------------------------------------------------------------------


# ======================================================================
# Experiment 1 — the lost update
# ======================================================================
counter = 0


def unsafe_worker() -> None:
    """Read-modify-write with NO lock. The three steps can interleave.

    CPython 3.12+ only switches threads at specific bytecodes (backward
    jumps), so we put one inside the read->write window. Real code has the
    same window naturally: any call, any await, any C-level preemption
    between reading a value and writing it back.
    """
    global counter
    for _ in range(RACE_INCREMENTS):
        v = counter          # read
        for _ in range(1):   # preemption opportunity inside the window
            pass
        counter = v + 1      # write (another thread may have written meanwhile)


def safe_worker(lock: threading.Lock) -> None:
    global counter
    for _ in range(RACE_INCREMENTS):
        with lock:
            v = counter
            for _ in range(1):   # same window — but now inside the lock
                pass
            counter = v + 1


def run_threads(target, *args) -> float:
    threads = [threading.Thread(target=target, args=args) for _ in range(RACE_THREADS)]
    t0 = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return time.perf_counter() - t0


def experiment_1_lost_update() -> None:
    global counter
    print("=" * 78)
    print("EXPERIMENT 1 — the lost update race")
    print("=" * 78)
    expected = RACE_THREADS * RACE_INCREMENTS
    print(f"{RACE_THREADS} threads x {RACE_INCREMENTS:,} increments -> "
          f"expected {expected:,}\n")

    old_interval = sys.getswitchinterval()
    sys.setswitchinterval(SWITCH_INTERVAL)
    try:
        print("  WITHOUT lock (read-modify-write can interleave):")
        for trial in range(1, RACE_TRIALS + 1):
            counter = 0
            dt = run_threads(unsafe_worker)
            lost = expected - counter
            print(f"    trial {trial}: final={counter:>8,}   "
                  f"lost={lost:>8,} ({lost / expected:6.1%})   {dt * 1000:6.1f} ms")

        print("\n  WITH lock (critical section is atomic):")
        lock = threading.Lock()
        counter = 0
        dt = run_threads(safe_worker, lock)
        print(f"    final={counter:>8,}   lost={expected - counter:>8,}   "
              f"{dt * 1000:6.1f} ms")
    finally:
        sys.setswitchinterval(old_interval)

    print("\n  -> different answer every run without the lock; exact (and often\n"
          "     slower) with it. Correctness first, then optimize the lock away.\n")


# ======================================================================
# Experiment 2 — deadlock
# ======================================================================
def experiment_2_deadlock() -> None:
    print("=" * 78)
    print("EXPERIMENT 2 — deadlock: opposite lock order vs global lock order")
    print("=" * 78)

    lock_a, lock_b = threading.Lock(), threading.Lock()
    outcome: dict[str, str] = {}

    def take(first: threading.Lock, second: threading.Lock, name: str) -> None:
        with first:
            time.sleep(0.05)                       # guarantee the interleaving
            if second.acquire(timeout=DEADLOCK_TIMEOUT_S):
                second.release()
                outcome[name] = "ok"
            else:
                outcome[name] = "DEADLOCKED (gave up after timeout)"

    print("\n  Opposite order — T1: A then B, T2: B then A:")
    t1 = threading.Thread(target=take, args=(lock_a, lock_b, "T1"))
    t2 = threading.Thread(target=take, args=(lock_b, lock_a, "T2"))
    t0 = time.perf_counter()
    t1.start(); t2.start(); t1.join(); t2.join()
    for name in ("T1", "T2"):
        print(f"    {name}: {outcome[name]}")
    print(f"    elapsed {time.perf_counter() - t0:.2f} s "
          f"(each held one lock, waited forever for the other)")

    print("\n  Global order — both threads: A then B:")
    outcome.clear()
    t1 = threading.Thread(target=take, args=(lock_a, lock_b, "T1"))
    t2 = threading.Thread(target=take, args=(lock_a, lock_b, "T2"))
    t0 = time.perf_counter()
    t1.start(); t2.start(); t1.join(); t2.join()
    for name in ("T1", "T2"):
        print(f"    {name}: {outcome[name]}")
    print(f"    elapsed {time.perf_counter() - t0:.2f} s")
    print("\n  -> same locks, same work. Ordering the acquisitions breaks the\n"
          "     circular wait, and the deadlock is impossible.\n")


# ======================================================================
# Experiment 3 — the GIL and CPU-bound work
# ======================================================================
def cpu_work(n: int) -> int:
    s = 0
    for i in range(n):
        s += i * i
    return s


def experiment_3_gil() -> None:
    print("=" * 78)
    print("EXPERIMENT 3 — GIL: CPU-bound tasks, threads vs processes")
    print("=" * 78)
    print(f"{CPU_TASKS} tasks x {CPU_CHUNK:,} iterations of pure-Python math\n")

    t0 = time.perf_counter()
    for _ in range(CPU_TASKS):
        cpu_work(CPU_CHUNK)
    seq = time.perf_counter() - t0

    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=CPU_TASKS) as pool:
        list(pool.map(cpu_work, [CPU_CHUNK] * CPU_TASKS))
    thr = time.perf_counter() - t0

    t0 = time.perf_counter()
    with multiprocessing.Pool(processes=CPU_TASKS) as pool:
        pool.map(cpu_work, [CPU_CHUNK] * CPU_TASKS)
    proc = time.perf_counter() - t0

    print(f"  {'sequential':<22} {seq:6.2f} s   speedup {seq / seq:4.1f}x")
    print(f"  {'threads (' + str(CPU_TASKS) + ')':<22} {thr:6.2f} s   "
          f"speedup {seq / thr:4.1f}x   <- GIL: one interpreter at a time")
    print(f"  {'processes (' + str(CPU_TASKS) + ')':<22} {proc:6.2f} s   "
          f"speedup {seq / proc:4.1f}x   <- one GIL per process")
    print("\n  -> threads buy ~nothing for CPU-bound Python (sometimes worse:\n"
          "     GIL hand-offs cost). Processes scale until spawn/IPC overhead bites.\n")


# ======================================================================
# Experiment 4 — I/O concurrency: asyncio vs thread pool
# ======================================================================
async def fake_io_async() -> None:
    await asyncio.sleep(IO_MS / 1000.0)


def fake_io_blocking() -> None:
    time.sleep(IO_MS / 1000.0)


async def run_asyncio_batch() -> None:
    await asyncio.gather(*(fake_io_async() for _ in range(IO_TASKS)))


def experiment_4_event_loop() -> None:
    print("=" * 78)
    print("EXPERIMENT 4 — 1,000 fake I/O calls: event loop vs thread pool")
    print("=" * 78)
    seq_est = IO_TASKS * IO_MS / 1000.0
    print(f"{IO_TASKS:,} calls x {IO_MS} ms each; "
          f"sequential would take ~{seq_est:.0f} s (not run)\n")

    t0 = time.perf_counter()
    asyncio.run(run_asyncio_batch())
    loop_s = time.perf_counter() - t0

    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=THREAD_POOL_WORKERS) as pool:
        list(pool.map(lambda _: fake_io_blocking(), range(IO_TASKS)))
    pool_s = time.perf_counter() - t0

    ideal_pool = IO_TASKS / THREAD_POOL_WORKERS * IO_MS / 1000.0
    print(f"  {'asyncio (1 thread)':<28} {loop_s:6.2f} s   "
          f"all {IO_TASKS:,} waits overlap on one thread")
    print(f"  {'thread pool (' + str(THREAD_POOL_WORKERS) + ' workers)':<28} "
          f"{pool_s:6.2f} s   ideal = tasks/workers x {IO_MS} ms = {ideal_pool:.1f} s")
    print(f"  {'sequential (estimated)':<28} {seq_est:6.2f} s")
    print("\n  -> waiting is free to overlap. The event loop holds 1,000 in-flight\n"
          "     waits on one thread; the pool is capped by worker count. This is\n"
          "     why gateways and proxies are async, and why pool size is a knob\n"
          "     you must size (lesson: threads = rate x wait time).\n")


def main() -> None:
    t_start = time.perf_counter()
    experiment_1_lost_update()
    experiment_2_deadlock()
    experiment_3_gil()
    experiment_4_event_loop()
    print(f"Total runtime: {time.perf_counter() - t_start:.1f} s")
    print("Done. Now do the README exercises: predict, edit CONFIG, re-run, compare.")


if __name__ == "__main__":
    main()
