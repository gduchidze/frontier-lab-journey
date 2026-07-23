"""Lab 0016 — Observability Lab.

A 3-service chain (gateway -> orders -> payments) emits structured events
for a compressed "month" of traffic (1,440 simulated minutes, ~200k
requests), with two injected faults: a payments slowness window at
10:00-10:05 and a payments error burst at 15:00-15:10, plus three
1-minute error blips that should NOT page anyone.

Run:  python3 observability_lab.py

Experiments:
  1. RED tables per service per minute — spot both faults in raw numbers.
  2. SLO math — availability + latency SLIs vs a 99.9% SLO, error-budget
     timeline, and how much budget each fault window ate.
  3. Burn-rate alerting — multi-window multi-burn-rate vs a naive
     per-minute threshold: pages fired, false pages, detection delay.
  Demo: trace reconstruction — span tree of the slowest request, showing
     the guilty hop. Plus a metric-series (cardinality) counter.

Deterministic (seeded RNG). Then do README exercises: predict, edit the
CONFIG block, re-run, compare.
"""

from __future__ import annotations

import random

# ---------------------------------------------------------------- CONFIG
SIM_MINUTES = 1440          # the compressed "month" (1 simulated day)
RPM = 140                   # requests per minute through the chain (~200k total)
BASE_ERROR_RATE = 0.0002    # payments baseline failure rate
SLOW_WINDOW = (600, 605)    # 10:00-10:05 — payments latency fault
SLOW_FRACTION = 0.20        # fraction of requests hit by the slowness
SLOW_MEAN_MS = 800.0        # payments latency during the fault
ERROR_WINDOW = (900, 910)   # 15:00-15:10 — payments error burst
FAULT_ERROR_RATE = 0.10     # error rate inside the burst
BLIP_MINUTES = (300, 1100, 1300)   # 1-minute noise blips (not page-worthy)
BLIP_ERROR_RATE = 0.03
SLO = 0.999                 # 99.9% for BOTH availability and latency SLOs
LATENCY_SLO_MS = 400.0      # end-to-end "good event" threshold
FAST_ALERT = (60, 5, 14.4)  # (long window, short window, burn threshold) -> PAGE
SLOW_ALERT = (360, 30, 6.0) # -> TICKET
NAIVE_THRESHOLD = 0.02      # naive alert: page if minute error rate > 2%
METRIC_LABELS = ("service",)   # E3: try ("service", "user_id")
NUM_USERS = 50_000
LOG_SAMPLE_RATE = 1         # keep 1 in N traces (E4: try 100)
SEED = 16
# -----------------------------------------------------------------------

SERVICES = ("gateway", "orders", "payments")


def hhmm(minute: int) -> str:
    return f"{minute // 60:02d}:{minute % 60:02d}"


def p99(values: list[float]) -> float:
    s = sorted(values)
    return s[int(0.99 * (len(s) - 1))]


def error_rate_at(minute: int) -> float:
    if ERROR_WINDOW[0] <= minute <= ERROR_WINDOW[1]:
        return FAULT_ERROR_RATE
    if minute in BLIP_MINUTES:
        return BLIP_ERROR_RATE
    return BASE_ERROR_RATE


def generate(rng: random.Random) -> list[tuple]:
    """One structured event per request: (minute, gw_ms, ord_ms, pay_ms,
    status, user_id). trace_id = index in this list."""
    events = []
    for m in range(SIM_MINUTES):
        err_rate = error_rate_at(m)
        in_slow = SLOW_WINDOW[0] <= m <= SLOW_WINDOW[1]
        for _ in range(RPM):
            gw = max(1.0, rng.gauss(6, 2))       # gateway self-time
            od = max(2.0, rng.gauss(20, 5))      # orders self-time
            if in_slow and rng.random() < SLOW_FRACTION:
                pay = max(50.0, rng.gauss(SLOW_MEAN_MS, 120))
            else:
                pay = max(5.0, rng.gauss(30, 8))
            status = 500 if rng.random() < err_rate else 200
            events.append((m, gw, od, pay, status, rng.randrange(NUM_USERS)))
    return events


def aggregate(events: list[tuple]):
    """Per-minute rollups: errors, latency-bad, union-bad, per-service latencies."""
    errors = [0] * SIM_MINUTES
    lat_bad = [0] * SIM_MINUTES
    union_bad = [0] * SIM_MINUTES
    lats = {svc: [[] for _ in range(SIM_MINUTES)] for svc in SERVICES}
    e2e = [[] for _ in range(SIM_MINUTES)]
    for m, gw, od, pay, status, _user in events:
        total = gw + od + pay
        is_err = status >= 500
        is_slow = total > LATENCY_SLO_MS
        errors[m] += is_err
        lat_bad[m] += is_slow
        union_bad[m] += is_err or is_slow
        lats["gateway"][m].append(total)          # span duration incl. children
        lats["orders"][m].append(od + pay)
        lats["payments"][m].append(pay)
        e2e[m].append(total)
    return errors, lat_bad, union_bad, lats, e2e


def experiment_1_red(errors, lats, e2e) -> None:
    print("=" * 78)
    print(f"EXPERIMENT 1 — RED per service per minute "
          f"({RPM} req/min through gateway->orders->payments)")
    print("=" * 78)
    print("  Latency fault window (payments slow 10:00-10:05) — p99 ms per hop:")
    print(f"  {'min':>6} {'rate':>5} {'err%':>6} {'gw p99':>8} "
          f"{'ord p99':>8} {'pay p99':>8}")
    for m in range(SLOW_WINDOW[0] - 3, SLOW_WINDOW[1] + 3):
        marker = "  <- fault" if SLOW_WINDOW[0] <= m <= SLOW_WINDOW[1] else ""
        print(f"  {hhmm(m):>6} {RPM:>5} {errors[m] / RPM:>6.1%} "
              f"{p99(lats['gateway'][m]):>8.0f} {p99(lats['orders'][m]):>8.0f} "
              f"{p99(lats['payments'][m]):>8.0f}{marker}")
    print("\n  Error burst window (payments 500s 15:00-15:10):")
    print(f"  {'min':>6} {'rate':>5} {'errors':>7} {'err%':>6} {'e2e p99':>8}")
    for m in range(ERROR_WINDOW[0] - 2, ERROR_WINDOW[1] + 3):
        marker = "  <- fault" if ERROR_WINDOW[0] <= m <= ERROR_WINDOW[1] else ""
        print(f"  {hhmm(m):>6} {RPM:>5} {errors[m]:>7} {errors[m] / RPM:>6.1%} "
              f"{p99(e2e[m]):>8.0f}{marker}")
    print("\n  -> RED answers WHEN and WHAT: the pay-p99 column fingers payments for")
    print("     the latency fault; err% spikes for the burst. WHO inside a single")
    print("     slow request is the trace demo's job.\n")


def experiment_2_slo(errors, lat_bad) -> None:
    total_req = SIM_MINUTES * RPM
    budget = (1 - SLO) * total_req
    print("=" * 78)
    print(f"EXPERIMENT 2 — SLO math: {SLO:.1%} availability + latency "
          f"(<{LATENCY_SLO_MS:.0f} ms) over the '{'month'}'")
    print("=" * 78)
    print(f"  total requests: {total_req:,}   error budget per SLI: "
          f"{budget:,.0f} bad events ({1 - SLO:.1%})")
    print(f"\n  {'time':>6} {'avail bad':>10} {'avail budget left':>18} "
          f"{'lat bad':>8} {'lat budget left':>16}")
    cum_err = cum_lat = 0
    for m in range(SIM_MINUTES):
        cum_err += errors[m]
        cum_lat += lat_bad[m]
        if (m + 1) % 180 == 0:
            print(f"  {hhmm(m):>6} {cum_err:>10,} {1 - cum_err / budget:>17.0%} "
                  f"{cum_lat:>8,} {1 - cum_lat / budget:>15.0%}")
    slow_cost = sum(lat_bad[SLOW_WINDOW[0]:SLOW_WINDOW[1] + 1])
    err_cost = sum(errors[ERROR_WINDOW[0]:ERROR_WINDOW[1] + 1])
    print(f"\n  -> the 6-min slowness window alone ate {slow_cost:,} latency-bad "
          f"events = {slow_cost / budget:.0%} of the monthly latency budget.")
    print(f"  -> the 11-min error burst ate {err_cost:,} errors = "
          f"{err_cost / budget:.0%} of the monthly availability budget.")
    print(f"  -> month-end: availability budget at "
          f"{1 - cum_err / budget:.0%}, latency budget at {1 - cum_lat / budget:.0%}."
          f" Negative = SLO violated; error-budget policy says freeze features.\n")


def burn(prefix: list[int], m: int, window: int) -> float:
    """Burn rate of the union SLI over `window` minutes ending at m."""
    lo = max(0, m + 1 - window)
    bad = prefix[m + 1] - prefix[lo]
    total = (m + 1 - lo) * RPM
    return (bad / total) / (1 - SLO)


def fire_minutes(active: list[bool]) -> list[int]:
    """Rising edges: the minute each alert run starts."""
    return [m for m in range(len(active)) if active[m] and (m == 0 or not active[m - 1])]


def experiment_3_alerting(errors, union_bad) -> None:
    print("=" * 78)
    print("EXPERIMENT 3 — burn-rate paging vs naive threshold alert")
    print("=" * 78)
    prefix = [0]
    for b in union_bad:
        prefix.append(prefix[-1] + b)

    def multi_window(long_w: int, short_w: int, thresh: float) -> list[bool]:
        return [burn(prefix, m, long_w) >= thresh and burn(prefix, m, short_w) >= thresh
                for m in range(SIM_MINUTES)]

    fast = multi_window(*FAST_ALERT)
    slow = multi_window(*SLOW_ALERT)
    naive = [errors[m] / RPM > NAIVE_THRESHOLD for m in range(SIM_MINUTES)]

    incidents = [("payments slowness", SLOW_WINDOW), ("error burst", ERROR_WINDOW)]

    def describe(name: str, fires: list[int]):
        real, false_pages = [], 0
        for f in fires:
            hit = next((inc for inc, (a, b) in incidents if a <= f <= b + 15), None)
            if hit:
                real.append((hit, f))
            else:
                false_pages += 1
        caught = {inc for inc, _ in real}
        delays = ", ".join(f"{inc.split()[0]} +{f - dict(incidents)[inc][0]}m"
                           for inc, f in real) or "-"
        print(f"  {name:<26} {len(fires):>5} {false_pages:>6} "
              f"{len(caught)}/2       {delays}")

    print(f"  {'alert':<26} {'pages':>5} {'false':>6} {'incidents':<9} detection")
    describe(f"fast burn {FAST_ALERT[2]}x (1h+5m)", fire_minutes(fast))
    describe(f"slow burn {SLOW_ALERT[2]}x (6h+30m)", fire_minutes(slow))
    describe(f"naive err% > {NAIVE_THRESHOLD:.0%}/min", fire_minutes(naive))
    print("\n  -> the naive alert is fastest on the burst but pages for self-healing")
    print("     blips and NEVER sees the latency incident (it watches raw")
    print("     errors, not the SLI). Burn-rate pages trade a few minutes of delay")
    print("     for zero false pages and full incident coverage.\n")


def demo_trace_and_cardinality(events: list[tuple]) -> None:
    print("=" * 78)
    print("DEMO — trace reconstruction + metric cardinality")
    print("=" * 78)
    kept = [(i, e) for i, e in enumerate(events) if i % LOG_SAMPLE_RATE == 0]
    window_kept = [(i, e) for i, e in kept
                   if SLOW_WINDOW[0] <= e[0] <= SLOW_WINDOW[1]]
    print(f"  traces kept by 1:{LOG_SAMPLE_RATE} sampling: {len(kept):,} / "
          f"{len(events):,} ({len(window_kept):,} inside the slow window)")
    if window_kept:
        tid, (m, gw, od, pay, status, _u) = max(
            window_kept, key=lambda ie: ie[1][1] + ie[1][2] + ie[1][3])
        total = gw + od + pay
        print(f"\n  slowest retained trace {tid:#010x} at {hhmm(m)} — "
              f"{total:.0f} ms end-to-end, status {status}")
        print(f"  └─ gateway   {total:>6.0f} ms  (self {gw:>5.0f} ms)")
        print(f"     └─ orders   {od + pay:>6.0f} ms  (self {od:>5.0f} ms)")
        guilty = "   <-- guilty hop" if pay > 0.8 * total else ""
        print(f"        └─ payments {pay:>6.0f} ms  (self {pay:>5.0f} ms){guilty}")
    else:
        print("  no trace retained inside the fault window — sampling ate the evidence.")

    series = set()
    for m, gw, od, pay, status, user in events:
        for svc in SERVICES:
            labels = {"service": svc, "status": status, "user_id": user}
            series.add(tuple(labels[k] for k in METRIC_LABELS))
    print(f"\n  metric time series with labels {METRIC_LABELS}: {len(series):,}")
    print("     (E3: add 'user_id' to METRIC_LABELS and watch this number — and")
    print("      your metrics bill — explode.)\n")


def main() -> None:
    rng = random.Random(SEED)
    events = generate(rng)
    errors, lat_bad, union_bad, lats, e2e = aggregate(events)
    experiment_1_red(errors, lats, e2e)
    experiment_2_slo(errors, lat_bad)
    experiment_3_alerting(errors, union_bad)
    demo_trace_and_cardinality(events)
    print("Done. Now do the README exercises: predict, edit CONFIG, re-run, compare.")


if __name__ == "__main__":
    main()
