"""Lab 0024 — Web Crawler.

Three experiments that turn Lesson 0024's claims into things you've seen
with your own eyes. Run:  python3 crawler_lab.py

No network calls. A synthetic web lives in memory: ~2,000 pages across
20 hosts, including one HOT host that ~50% of all links point at, and one
SPIDER-TRAP host whose calendar pages generate infinite parametrized URLs.
Time is a simulated clock (milliseconds), so runs are deterministic and
finish in seconds.

  EXPERIMENT 1 — naive FIFO crawler vs polite frontier (per-host queues +
                 politeness delay): per-host bursts and politeness violations
  EXPERIMENT 2 — bloom filter from scratch (int as bitarray, k hashes) as
                 the URL-seen test: false positives vs bits per key
  EXPERIMENT 3 — spider trap: per-host URL budget on vs off

Then do the exercises in README.md — they all involve editing the CONFIG
block below and predicting the output BEFORE re-running.
"""

from __future__ import annotations

import hashlib
import heapq
import itertools
import math
import random
from collections import Counter, defaultdict, deque

# ---------------------------------------------------------------- CONFIG
# The exercises in README.md ask you to change these and predict results.
SEED = 24
N_REGULAR_HOSTS = 18        # + 1 hot host + 1 trap host = 20 hosts total
N_PAGES = 2000              # static pages (hot host + regular hosts)
HOT_PAGES = 300             # of N_PAGES, how many live on the hot host
LINKS_PER_PAGE = 8          # outlinks per static page
HOT_LINK_FRACTION = 0.50    # fraction of links that point at the hot host
TRAP_LINK_FRACTION = 0.02   # fraction of links that point at the trap entry
FETCH_MS = 50.0             # simulated time per fetch
POLITENESS_MS = 1000.0      # required gap between hits on the same host
MAX_FETCHES = 1500          # fetch budget for experiment 1
TRAP_BUDGET_E1 = 60         # trap-host cap in experiment 1 (isolates politeness)
PER_HOST_BUDGET = 120       # per-host cap in experiment 3 (trap defense)
MAX_FETCHES_TRAP = 4000     # fetch budget for experiment 3
BLOOM_SWEEP = [4, 8, 12, 16]  # bits per key to try in experiment 2
BLOOM_PROBES = 10_000       # fresh, never-inserted URLs probed for FPs
# -----------------------------------------------------------------------

HOT_HOST = "hot-megastore.example"
TRAP_HOST = "calendar-trap.example"


# ------------------------------------------------------------ synthetic web
def build_web() -> tuple[dict[str, list[str]], list[str]]:
    """Build the static part of the web: url -> outlinks.

    Link targets are drawn so HOT_LINK_FRACTION of links hit the hot host
    and TRAP_LINK_FRACTION hit the trap entry page. The trap host itself
    is NOT in this dict — its pages are generated on the fly (see links_of).
    """
    rng = random.Random(SEED)
    hot_pages = [f"http://{HOT_HOST}/item{i}" for i in range(HOT_PAGES)]
    regular_pages: list[str] = []
    per_host = (N_PAGES - HOT_PAGES) // N_REGULAR_HOSTS
    for h in range(N_REGULAR_HOSTS):
        host = f"site{h:02d}.example"
        regular_pages += [f"http://{host}/page{i}" for i in range(per_host)]
    web: dict[str, list[str]] = {}
    for url in hot_pages + regular_pages:
        links = []
        for _ in range(LINKS_PER_PAGE):
            r = rng.random()
            if r < HOT_LINK_FRACTION:
                links.append(rng.choice(hot_pages))
            elif r < HOT_LINK_FRACTION + TRAP_LINK_FRACTION:
                links.append(f"http://{TRAP_HOST}/cal?d=0")
            else:
                links.append(rng.choice(regular_pages))
        web[url] = links
    return web, hot_pages + regular_pages


def host_of(url: str) -> str:
    return url.split("/")[2]


def links_of(url: str, web: dict[str, list[str]]) -> list[str]:
    """Outlinks of a page. Trap pages mint fresh URLs forever."""
    if host_of(url) == TRAP_HOST:
        day = int(url.split("?d=")[1].split("&")[0])
        base = f"http://{TRAP_HOST}/cal?d={day + 1}"
        return [base, base + "&view=week", base + "&view=month"]
    return web.get(url, [])


# ---------------------------------------------------------------- crawlers
class CrawlStats:
    def __init__(self, name: str) -> None:
        self.name = name
        self.host_seq: list[str] = []
        self.host_counts: Counter[str] = Counter()
        self.violations = 0
        self.elapsed_ms = 0.0
        self.fetched = 0

    def max_run(self, target: str | None = None) -> int:
        best = cur = 0
        prev = None
        for h in self.host_seq:
            cur = cur + 1 if h == prev else 1
            prev = h
            if target is None or h == target:
                best = max(best, cur)
        return best


def budget_for(host: str, budgets: dict[str, int] | None,
               default_budget: int | None) -> int | None:
    if budgets and host in budgets:
        return budgets[host]
    return default_budget


def crawl_naive(web: dict[str, list[str]], seeds: list[str], max_fetches: int,
                budgets: dict[str, int] | None = None,
                default_budget: int | None = None) -> CrawlStats:
    """One FIFO frontier, no per-host separation, no delays.

    Fetches back to back (clock += FETCH_MS each). A hit on a host less
    than POLITENESS_MS after the previous hit counts as a violation.
    """
    stats = CrawlStats("naive FIFO")
    frontier = deque(seeds)
    seen = set(seeds)
    clock = 0.0
    last_start: dict[str, float] = {}
    while frontier and stats.fetched < max_fetches:
        url = frontier.popleft()
        host = host_of(url)
        cap = budget_for(host, budgets, default_budget)
        if cap is not None and stats.host_counts[host] >= cap:
            continue                      # budget spent: drop, don't fetch
        if host in last_start and clock - last_start[host] < POLITENESS_MS:
            stats.violations += 1
        last_start[host] = clock
        clock += FETCH_MS
        stats.fetched += 1
        stats.host_counts[host] += 1
        stats.host_seq.append(host)
        for link in links_of(url, web):
            if link not in seen:
                seen.add(link)
                frontier.append(link)
    stats.elapsed_ms = clock
    return stats


def crawl_polite(web: dict[str, list[str]], seeds: list[str], max_fetches: int,
                 budgets: dict[str, int] | None = None,
                 default_budget: int | None = None) -> CrawlStats:
    """Mercator-style back queues: one FIFO per host + a heap of
    (next_allowed_time, host). A host re-enters the heap POLITENESS_MS
    after its last fetch started. The clock jumps forward when no host
    is ready yet — politeness is enforced, never violated.
    """
    stats = CrawlStats("polite frontier")
    host_queues: dict[str, deque[str]] = defaultdict(deque)
    next_allowed: dict[str, float] = {}
    ready: list[tuple[float, int, str]] = []
    in_heap: set[str] = set()
    tie = itertools.count()
    seen: set[str] = set()
    last_start: dict[str, float] = {}
    clock = 0.0

    def enqueue(url: str) -> None:
        host = host_of(url)
        host_queues[host].append(url)
        if host not in in_heap:
            heapq.heappush(ready, (next_allowed.get(host, 0.0), next(tie), host))
            in_heap.add(host)

    for s in seeds:
        seen.add(s)
        enqueue(s)

    while ready and stats.fetched < max_fetches:
        t, _, host = heapq.heappop(ready)
        in_heap.discard(host)
        cap = budget_for(host, budgets, default_budget)
        if cap is not None and stats.host_counts[host] >= cap:
            host_queues[host].clear()     # budget spent: drop the queue
            continue
        url = host_queues[host].popleft()
        clock = max(clock, t)             # wait for the host's cooldown
        if host in last_start and clock - last_start[host] < POLITENESS_MS - 1e-9:
            stats.violations += 1
        last_start[host] = clock
        next_allowed[host] = clock + POLITENESS_MS
        clock += FETCH_MS
        stats.fetched += 1
        stats.host_counts[host] += 1
        stats.host_seq.append(host)
        for link in links_of(url, web):
            if link not in seen:
                seen.add(link)
                enqueue(link)
        if host_queues[host] and host not in in_heap:
            heapq.heappush(ready, (next_allowed[host], next(tie), host))
            in_heap.add(host)
    stats.elapsed_ms = clock
    return stats


# ------------------------------------------------------------ bloom filter
class Bloom:
    """Bloom filter from scratch: one big int as the bit array,
    k hash positions per key via double hashing over sha256."""

    def __init__(self, n_keys: int, bits_per_key: int) -> None:
        self.m = max(8, n_keys * bits_per_key)
        self.k = max(1, round(bits_per_key * math.log(2)))
        self.bits = 0

    def _positions(self, key: str) -> list[int]:
        d = hashlib.sha256(key.encode()).digest()
        h1 = int.from_bytes(d[:8], "big")
        h2 = int.from_bytes(d[8:16], "big") | 1
        return [(h1 + i * h2) % self.m for i in range(self.k)]

    def add(self, key: str) -> None:
        for pos in self._positions(key):
            self.bits |= 1 << pos

    def __contains__(self, key: str) -> bool:
        return all((self.bits >> pos) & 1 for pos in self._positions(key))


# -------------------------------------------------------------- experiments
def experiment_1(web: dict[str, list[str]], seeds: list[str]) -> None:
    print("=" * 78)
    print("EXPERIMENT 1 — naive FIFO vs polite frontier "
          f"(politeness gap {POLITENESS_MS:.0f} ms, fetch {FETCH_MS:.0f} ms, "
          f"{MAX_FETCHES} fetches max)")
    print("=" * 78)
    print(f"one hot host receives ~{HOT_LINK_FRACTION:.0%} of all links; "
          f"trap host capped at {TRAP_BUDGET_E1} to isolate politeness\n")
    hdr = (f"  {'crawler':<17}{'fetches':>8}{'hosts':>7}{'hot hits':>9}"
           f"{'max run(hot)':>13}{'violations':>11}{'elapsed':>10}")
    print(hdr)
    for fn in (crawl_naive, crawl_polite):
        s = fn(web, seeds, MAX_FETCHES, budgets={TRAP_HOST: TRAP_BUDGET_E1})
        print(f"  {s.name:<17}{s.fetched:>8}{len(s.host_counts):>7}"
              f"{s.host_counts[HOT_HOST]:>9}{s.max_run(HOT_HOST):>13}"
              f"{s.violations:>11}{s.elapsed_ms / 1000:>9.1f}s")
    print("\n  -> naive FIFO fetches back to back, so nearly every repeat hit on a")
    print("     host lands inside the 1000 ms politeness window — hundreds of")
    print("     violations, with consecutive BURSTS on the hot host. That is what")
    print("     earns IP bans in the real world. The polite frontier interleaves")
    print("     hosts and reaches ZERO violations — but look at 'hot hits': the")
    print("     hot host is now served at most once per delay (1/s), so the same")
    print("     fetch budget buys fewer of its pages. Politeness caps per-host")
    print("     throughput at 1/delay; you scale a crawler by keeping MORE hosts")
    print("     in flight, never by shrinking the delay.\n")


def experiment_2(inserted: list[str]) -> None:
    n = len(inserted)
    print("=" * 78)
    print(f"EXPERIMENT 2 — bloom filter as the URL-seen test "
          f"({n} URLs inserted, {BLOOM_PROBES} fresh URLs probed)")
    print("=" * 78)
    print("a false positive = a brand-new URL the filter claims was seen\n")
    print(f"  {'bits/key':>8}{'k':>4}{'memory':>10}{'predicted FP':>14}"
          f"{'observed FP':>13}{'lost URLs':>11}")
    fresh = [f"http://never-seen.example/fp{i}" for i in range(BLOOM_PROBES)]
    for bpk in BLOOM_SWEEP:
        bloom = Bloom(n, bpk)
        for url in inserted:
            bloom.add(url)
        fp = sum(1 for url in fresh if url in bloom)
        predicted = (1 - math.exp(-bloom.k * n / bloom.m)) ** bloom.k
        print(f"  {bpk:>8}{bloom.k:>4}{bloom.m / 8 / 1024:>8.1f}KB"
              f"{predicted:>13.3%}{fp / BLOOM_PROBES:>12.3%}{fp:>11}")
    exact_kb = n * 40 / 1024   # ~40 B/URL for a hash set of digests
    print(f"\n  -> an exact hash set of these URLs needs ~{exact_kb:.0f} KB; "
          f"the 8-bits/key filter")
    print("     does the same job in a fraction of that, at the price of ~2% of new")
    print("     URLs silently never being crawled (FP = 'seen' = skipped). At 1B")
    print("     URLs the same math is 1.25 GB of RAM vs ~40 GB — that is why every")
    print("     large crawler accepts the false-positive trade.\n")


def experiment_3(web: dict[str, list[str]], seeds: list[str],
                 n_static: int) -> None:
    print("=" * 78)
    print(f"EXPERIMENT 3 — spider trap vs per-host budget "
          f"({MAX_FETCHES_TRAP} fetches max, budget {PER_HOST_BUDGET} URLs/host)")
    print("=" * 78)
    print("the trap host mints 3 fresh URLs per fetch, forever\n")
    print(f"  {'defense':<21}{'fetches':>8}{'trap hits':>10}{'trap share':>11}"
          f"{'static coverage':>16}{'fetch/page':>11}")
    for label, default_budget in (("no budget", None),
                                  (f"budget={PER_HOST_BUDGET}/host", PER_HOST_BUDGET)):
        s = crawl_naive(web, seeds, MAX_FETCHES_TRAP, default_budget=default_budget)
        static_fetched = s.fetched - s.host_counts[TRAP_HOST]
        coverage = static_fetched / n_static
        cost = s.fetched / max(1, static_fetched)
        print(f"  {label:<21}{s.fetched:>8}{s.host_counts[TRAP_HOST]:>10}"
              f"{s.host_counts[TRAP_HOST] / s.fetched:>10.1%}"
              f"{coverage:>15.1%}{cost:>11.2f}")
    print("\n  -> without a budget the finite real web runs out and the crawler")
    print("     keeps burning its entire remaining budget on machine-generated")
    print("     calendar URLs — it would do so FOREVER. The per-host budget trades")
    print("     a few percent of hot-host coverage for immunity: the crawl simply")
    print("     terminates when honest work is done. URL count per domain is the")
    print("     defense; no URL pattern blacklist survives contact with the web.\n")


def main() -> None:
    print(f"(synthetic web, simulated clock, seed={SEED} — no network calls; "
          "deterministic)\n")
    web, static_pages = build_web()
    seeds = [f"http://site{h:02d}.example/page0" for h in range(N_REGULAR_HOSTS)]
    seeds.append(f"http://{HOT_HOST}/item0")
    print(f"web built: {len(static_pages)} static pages on {N_REGULAR_HOSTS + 1} "
          f"hosts + 1 infinite trap host ({TRAP_HOST})\n")
    experiment_1(web, seeds)
    # URL-seen keys for the bloom experiment: the full static web —
    # exactly the set a complete crawl must remember to avoid re-fetching.
    experiment_2(static_pages)
    experiment_3(web, seeds, n_static=len(static_pages))
    print("Now do the README exercises: predict, edit CONFIG, re-run, compare.")


if __name__ == "__main__":
    main()
