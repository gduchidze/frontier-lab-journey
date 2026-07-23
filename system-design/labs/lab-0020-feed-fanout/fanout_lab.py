"""Lab 0020 — Feed Fanout.

Lesson 0020's three delivery strategies, measured instead of believed.
Run:  python3 fanout_lab.py            (default celebrity threshold = 500)
      python3 fanout_lab.py --threshold 100

The simulation builds a 10,000-user social graph with a power-law follower
distribution (random.paretovariate — a few accounts have thousands of
followers, most have a handful), fires seeded post + read traffic at it,
then delivers the posts three ways:

  fanout-on-write  every post is pushed into every follower's feed list
  fanout-on-read   nothing is pushed; readers merge their followees' lists
  hybrid           authors with >= THRESHOLD followers are 'celebrities':
                   their posts are merged at read time, the rest are pushed

Fanout workers have finite capacity (FANOUT_CAPACITY inserts per tick), so
a celebrity post creates a real backlog and real staleness — the
head-of-line blocking from lesson section 6, on your own CPU.

Everything is seeded and stdlib-only. Do the README exercises: predict,
run, compare. The numbers wiggle only if you change CONFIG.
"""

from __future__ import annotations

import argparse
import random
from collections import deque

# ---------------------------------------------------------------- CONFIG
# The exercises in README.md ask you to change these and predict results.
N_USERS = 10_000          # accounts in the graph
ALPHA = 1.15              # pareto shape: lower = heavier celebrity tail (E4)
BASE_FOLLOWERS = 4        # follower count = BASE * paretovariate(ALPHA), capped
N_POSTS = 5_000           # posts fired during the run
N_READS = 20_000          # feed reads during the run
N_TICKS = 200             # posts arrive uniformly over this many ticks
FANOUT_CAPACITY = 3_000   # feed inserts the worker pool completes per tick
FEED_CAP = 100            # max entries kept per feed list (lesson: ~800; scaled down)
DEFAULT_THRESHOLD = 500   # followers >= threshold -> celebrity (hybrid only)
SWEEP = [1, 10, 50, 100, 250, 500, 1_000, 2_500, 10_000]  # thresholds for E3
SEED = 20
# -----------------------------------------------------------------------


def build_graph(rng: random.Random) -> tuple[list[list[int]], list[list[int]]]:
    """followers[u] = who follows u; following[u] = whom u follows."""
    followers: list[list[int]] = []
    population = range(N_USERS)
    for u in range(N_USERS):
        k = min(N_USERS - 1, int(BASE_FOLLOWERS * rng.paretovariate(ALPHA)))
        picked = rng.sample(population, min(N_USERS, k + 1))
        followers.append([v for v in picked if v != u][:k])
    following: list[list[int]] = [[] for _ in range(N_USERS)]
    for author, fans in enumerate(followers):
        for fan in fans:
            following[fan].append(author)
    return followers, following


def make_traffic(
    rng: random.Random, followers: list[list[int]]
) -> tuple[list[tuple[int, int]], list[int]]:
    """Posts as sorted (tick, author); readers as user ids.

    Posting activity is weighted by 1 + sqrt(followers): big accounts post
    more, as they do in real feeds. Reads are uniform across users.
    """
    weights = [1.0 + len(f) ** 0.5 for f in followers]
    authors = rng.choices(range(N_USERS), weights=weights, k=N_POSTS)
    posts = sorted((rng.randrange(N_TICKS), a) for a in authors)
    readers = rng.choices(range(N_USERS), k=N_READS)
    return posts, readers


def simulate_fanout(
    posts: list[tuple[int, int]],
    followers: list[list[int]],
    celebrities: set[int],
) -> tuple[int, list[tuple[int, int]], list[int]]:
    """Push every non-celebrity post through a finite-capacity worker pool.

    Returns (total feed inserts, [(delay_ticks, n_inserts)], deliveries per user).
    A FIFO job queue + FANOUT_CAPACITY inserts/tick means a huge post at the
    head delays everything behind it — measurable head-of-line blocking.
    """
    job_queue: deque[list[int]] = deque()   # [post_tick, author, delivered_so_far]
    write_ops = 0
    delays: list[tuple[int, int]] = []
    delivered_to = [0] * N_USERS
    next_post = 0
    tick = 0
    while next_post < len(posts) or job_queue:
        while next_post < len(posts) and posts[next_post][0] == tick:
            post_tick, author = posts[next_post]
            next_post += 1
            if author in celebrities or not followers[author]:
                continue
            job_queue.append([post_tick, author, 0])
        capacity = FANOUT_CAPACITY
        while capacity > 0 and job_queue:
            post_tick, author, done = job_queue[0]
            fans = followers[author]
            take = min(capacity, len(fans) - done)
            for fan in fans[done:done + take]:
                delivered_to[fan] += 1
            write_ops += take
            delays.append((tick - post_tick, take))
            capacity -= take
            job_queue[0][2] = done + take
            if job_queue[0][2] >= len(fans):
                job_queue.popleft()
        tick += 1
    return write_ops, delays, delivered_to


def staleness_stats(delays: list[tuple[int, int]]) -> tuple[float, int]:
    """Insert-weighted (mean, p99) delivery delay in ticks."""
    total = sum(count for _, count in delays)
    if total == 0:
        return 0.0, 0
    mean = sum(delay * count for delay, count in delays) / total
    seen = 0
    for delay, count in sorted(delays):
        seen += count
        if seen >= 0.99 * total:
            return mean, delay
    return mean, delays[-1][0]


def read_merge_costs(
    readers: list[int],
    following: list[list[int]],
    celebrities: set[int],
    pure_pull: bool,
) -> list[int]:
    """Lists a reader must fetch+merge per feed read (the latency proxy)."""
    costs = []
    for r in readers:
        if pure_pull:
            costs.append(max(1, len(following[r])))
        else:
            costs.append(1 + sum(1 for a in following[r] if a in celebrities))
    return costs


def memory_cells(
    delivered_to: list[int],
    posts_by_author: list[int],
    celebrities: set[int],
    pure_pull: bool,
) -> int:
    """Feed-serving entries resident: follower lists (capped) + timelines
    of every author readers must pull from (celebrities, or all if pure pull)."""
    if pure_pull:
        return sum(min(n, FEED_CAP) for n in posts_by_author if n)
    cells = sum(min(n, FEED_CAP) for n in delivered_to)
    cells += sum(min(posts_by_author[a], FEED_CAP) for a in celebrities)
    return cells


def run_strategy(
    name: str,
    posts: list[tuple[int, int]],
    readers: list[int],
    followers: list[list[int]],
    following: list[list[int]],
    celebrities: set[int],
    pure_pull: bool,
) -> dict:
    posts_by_author = [0] * N_USERS
    for _, author in posts:
        posts_by_author[author] += 1
    if pure_pull:
        write_ops, delays, delivered = 0, [], [0] * N_USERS
    else:
        write_ops, delays, delivered = simulate_fanout(posts, followers, celebrities)
    costs = read_merge_costs(readers, following, celebrities, pure_pull)
    mean_stale, p99_stale = staleness_stats(delays)
    costs_sorted = sorted(costs)
    return {
        "name": name,
        "write_ops": write_ops,
        "merge_avg": sum(costs) / len(costs),
        "merge_p99": costs_sorted[int(len(costs_sorted) * 0.99)],
        "stale_mean": mean_stale,
        "stale_p99": p99_stale,
        "memory": memory_cells(delivered, posts_by_author, celebrities, pure_pull),
        "cost": write_ops + sum(costs),
    }


def print_comparison(rows: list[dict]) -> None:
    print(f"  {'strategy':<22}{'feed inserts':>13}{'merge avg':>10}{'merge p99':>10}"
          f"{'stale mean':>11}{'stale p99':>10}{'mem cells':>11}{'cost proxy':>11}")
    for r in rows:
        print(f"  {r['name']:<22}{r['write_ops']:>13,}{r['merge_avg']:>10.1f}"
              f"{r['merge_p99']:>10}{r['stale_mean']:>11.1f}{r['stale_p99']:>10}"
              f"{r['memory']:>11,}{r['cost']:>11,}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Lab 0020 — feed fanout strategies")
    parser.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD,
                        help="follower count at which an author becomes a "
                             f"celebrity in the hybrid (default {DEFAULT_THRESHOLD})")
    args = parser.parse_args()

    rng = random.Random(SEED)
    followers, following = build_graph(rng)
    posts, readers = make_traffic(rng, followers)

    counts = sorted((len(f) for f in followers), reverse=True)
    edges = sum(counts)
    print(f"(seed={SEED}; {N_USERS:,} users; followers ~ "
          f"{BASE_FOLLOWERS}*paretovariate({ALPHA}))\n")
    print("=" * 78)
    print("THE GRAPH — power-law follower distribution")
    print("=" * 78)
    print(f"  edges={edges:,}  mean={edges / N_USERS:.1f}  "
          f"median={counts[N_USERS // 2]}  max={counts[0]:,}")
    print(f"  top 5 accounts by followers: {[f'{c:,}' for c in counts[:5]]}")
    print(f"  accounts with >= {args.threshold} followers (hybrid celebrities): "
          f"{sum(1 for c in counts if c >= args.threshold)}")
    print(f"  {N_POSTS:,} posts over {N_TICKS} ticks (activity ~ 1+sqrt(followers)); "
          f"{N_READS:,} reads; worker pool = {FANOUT_CAPACITY:,} inserts/tick\n")

    print("=" * 78)
    print(f"EXPERIMENT 1+2 — three strategies head-to-head "
          f"(hybrid threshold = {args.threshold})")
    print("=" * 78)
    empty: set[int] = set()
    everyone = set(range(N_USERS))
    celebs = {u for u in range(N_USERS) if len(followers[u]) >= args.threshold}
    shared = (posts, readers, followers, following)
    rows = [
        run_strategy("fanout-on-write", *shared, empty, pure_pull=False),
        run_strategy("fanout-on-read", *shared, everyone, pure_pull=True),
        run_strategy(f"hybrid({args.threshold})", *shared, celebs, pure_pull=False),
    ]
    print_comparison(rows)
    print("\n  -> push: O(1) reads, but the celebrity posts flood the workers —")
    print("     look at stale p99 (ticks a delivered insert waited in the queue).")
    print("     pull: perfectly fresh, zero feed inserts, but EVERY read pays a")
    print("     ~mean-followees-wide merge. hybrid: push's cheap reads, pull's")
    print("     freshness, by special-casing the handful of heavy accounts.\n")

    print("=" * 78)
    print("EXPERIMENT 3 — threshold sweep "
          "(cost proxy = feed inserts + lists merged across all reads)")
    print("=" * 78)
    print(f"  {'threshold':>9}  {'celebs':>6}  {'feed inserts':>13}"
          f"  {'read merges':>12}  {'cost proxy':>11}  {'stale p99':>9}")
    for th in SWEEP:
        c = {u for u in range(N_USERS) if len(followers[u]) >= th}
        r = run_strategy(f"hybrid({th})", *shared, c, pure_pull=False)
        read_merges = r["cost"] - r["write_ops"]
        print(f"  {th:>9,}  {len(c):>6,}  {r['write_ops']:>13,}"
              f"  {read_merges:>12,}  {r['cost']:>11,}  {r['stale_p99']:>9}")
    print("\n  -> threshold ~1: everyone is a celebrity = pure pull; reads pay for")
    print("     everything. threshold beyond max followers: pure push; celebrity")
    print("     inserts pay for everything. The minimum sits between — the U-curve.")
    print("     Move --threshold and FANOUT_CAPACITY, predict, re-run (README E1–E4).")


if __name__ == "__main__":
    main()
