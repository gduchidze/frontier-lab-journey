"""Lab p0-04 — Latency Anatomy.

Three experiments that turn Lesson p0-04's claims about handshakes,
connection reuse, and RTT-dominated page loads into measured numbers.

Run:  python3 latency_anatomy_lab.py

Then do the exercises in README.md — they all involve editing the
CONFIG block below and predicting the output BEFORE re-running.
Pure stdlib. Experiment 1 uses real sockets on localhost; experiments
2 and 3 are exact RTT arithmetic (no randomness, so your hand math
must match the program to the millisecond).
"""

from __future__ import annotations

import socket
import statistics
import threading
import time

# ---------------------------------------------------------------- CONFIG
# The exercises in README.md ask you to change these and predict results.
REQUESTS = 300            # requests per strategy in experiment 1 (real sockets)
PAYLOAD_BYTES = 64        # request/response size for the echo round trip
RTT_MS_SCENARIOS = [10.0, 50.0, 150.0]   # same-region / cross-region / cross-ocean
RESOURCES = 24            # objects on the simulated page (experiment 2)
PARALLEL_CONNECTIONS = 6  # browser-style parallel HTTP/1.1 connections
TLS_VERSION = "1.3"       # "1.2" (2-RTT handshake) or "1.3" (1-RTT handshake)
SERVER_THINK_MS = 0.0     # per-request server processing time to add everywhere
# -----------------------------------------------------------------------

TLS_HANDSHAKE_RTTS = {"1.2": 2, "1.3": 1}


def percentile(sorted_values: list[float], p: float) -> float:
    idx = min(int(len(sorted_values) * p), len(sorted_values) - 1)
    return sorted_values[idx]


# ---------------------------------------------------------------- server


def start_echo_server() -> tuple[str, int]:
    """Echo server on localhost. One handler thread per connection so a
    reused (kept-alive) connection can serve many requests."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 0))
    srv.listen(64)
    host, port = srv.getsockname()

    def handle(conn: socket.socket) -> None:
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        with conn:
            while True:
                data = conn.recv(PAYLOAD_BYTES)
                if not data:
                    return
                conn.sendall(data)

    def accept_loop() -> None:
        while True:
            conn, _ = srv.accept()
            threading.Thread(target=handle, args=(conn,), daemon=True).start()

    threading.Thread(target=accept_loop, daemon=True).start()
    return host, port


# ------------------------------------------------------- experiment 1


def timed_round_trip(conn: socket.socket, msg: bytes) -> float:
    t0 = time.perf_counter()
    conn.sendall(msg)
    received = 0
    while received < len(msg):
        received += len(conn.recv(PAYLOAD_BYTES))
    return (time.perf_counter() - t0) * 1e6  # microseconds


def experiment_1_connect_vs_reuse() -> None:
    print("=" * 78)
    print("EXPERIMENT 1 — real sockets: new connection per request vs reuse")
    print(f"({REQUESTS} requests of {PAYLOAD_BYTES} bytes to a localhost echo "
          "server; all numbers in microseconds)")
    print("=" * 78)
    host, port = start_echo_server()
    msg = b"x" * PAYLOAD_BYTES

    # Strategy A: cold — TCP connect + request + close, every time.
    cold: list[float] = []
    for _ in range(REQUESTS):
        t0 = time.perf_counter()
        with socket.create_connection((host, port)) as conn:
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            conn.sendall(msg)
            received = 0
            while received < len(msg):
                received += len(conn.recv(PAYLOAD_BYTES))
        cold.append((time.perf_counter() - t0) * 1e6)

    # Strategy B: warm — connect once, reuse for every request (a pool of 1).
    warm: list[float] = []
    with socket.create_connection((host, port)) as conn:
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        timed_round_trip(conn, msg)  # warm-up, excluded from stats
        for _ in range(REQUESTS):
            warm.append(timed_round_trip(conn, msg))

    rows = [("new conn every request", cold), ("one reused connection", warm)]
    print(f"  {'strategy':<26}{'mean':>9}{'p50':>9}{'p99':>9}")
    for label, vals in rows:
        s = sorted(vals)
        print(f"  {label:<26}{statistics.fmean(s):>9.1f}"
              f"{percentile(s, 0.50):>9.1f}{percentile(s, 0.99):>9.1f}")
    ratio = statistics.fmean(cold) / statistics.fmean(warm)
    print(f"\n  -> connection setup made the mean {ratio:.1f}x slower — and this is "
          "localhost,")
    print("     where the 'round trip' is ~free. On a 50 ms WAN link every fresh")
    print("     connection adds 50+ ms of pure handshake before byte one.\n")


# ------------------------------------------------------- experiment 2


def setup_rtts() -> int:
    """RTTs spent before the first request can be sent on a new connection:
    1 for the TCP handshake + the TLS handshake for the configured version."""
    return 1 + TLS_HANDSHAKE_RTTS[TLS_VERSION]


def experiment_2_page_load_strategies() -> None:
    print("=" * 78)
    print(f"EXPERIMENT 2 — page with {RESOURCES} resources: handshake math "
          "(deterministic)")
    print(f"model: each request costs 1 RTT; new connection costs "
          f"{setup_rtts()} setup RTTs (TCP + TLS {TLS_VERSION}); "
          f"think={SERVER_THINK_MS:.0f} ms/request")
    print("=" * 78)
    n, c = RESOURCES, PARALLEL_CONNECTIONS
    think = SERVER_THINK_MS

    for rtt in RTT_MS_SCENARIOS:
        # HTTP/1.1, Connection: close — every resource pays setup + request,
        # serialized over c parallel connections.
        per_resource = (setup_rtts() + 1) * rtt + think
        rounds_close = -(-n // c)  # ceil division
        t_close = rounds_close * per_resource
        hs_close = n

        # HTTP/1.1 keep-alive — c connections pay setup once, then requests
        # are serialized per connection (no pipelining).
        t_keep = setup_rtts() * rtt + rounds_close * (rtt + think)
        hs_keep = c

        # HTTP/2 — one connection, one setup, all streams multiplexed:
        # ~1 RTT for the whole batch (bandwidth ignored on purpose).
        t_h2 = setup_rtts() * rtt + (rtt + think)
        hs_h2 = 1

        # HTTP/3 (QUIC) — transport + TLS 1.3 combined into 1 setup RTT.
        t_h3 = 1 * rtt + (rtt + think)
        hs_h3 = 1

        print(f"\n  RTT = {rtt:.0f} ms")
        print(f"    {'strategy':<34}{'handshakes':>10}{'page load':>12}")
        for label, hs, total in [
            ("HTTP/1.1  Connection: close", hs_close, t_close),
            (f"HTTP/1.1  keep-alive x{c} conns", hs_keep, t_keep),
            ("HTTP/2    one multiplexed conn", hs_h2, t_h2),
            ("HTTP/3    QUIC one connection", hs_h3, t_h3),
        ]:
            print(f"    {label:<34}{hs:>10}{total:>10.0f} ms")

    print("\n  -> same bytes, same server — a ~6x gap at every RTT, and the gap")
    print("     is pure handshakes and serialized round trips, not bandwidth.")
    print("     Latency is a protocol-design problem.\n")


# ------------------------------------------------------- experiment 3


def experiment_3_time_to_first_byte() -> None:
    print("=" * 78)
    print("EXPERIMENT 3 — time to first byte for ONE request on a fresh connection")
    print("(setup RTTs + 1 request RTT; deterministic ladder)")
    print("=" * 78)
    ladder = [
        ("TCP + TLS 1.2", 1 + TLS_HANDSHAKE_RTTS["1.2"] + 1),
        ("TCP + TLS 1.3", 1 + TLS_HANDSHAKE_RTTS["1.3"] + 1),
        ("QUIC (HTTP/3) 1-RTT", 1 + 1),
        ("QUIC 0-RTT resumption", 0 + 1),
        ("reused pooled connection", 0 + 1),
    ]
    header = "".join(f"{f'RTT {r:.0f} ms':>14}" for r in RTT_MS_SCENARIOS)
    print(f"  {'connection state':<28}{'RTTs':>5}{header}")
    for label, rtts in ladder:
        cells = "".join(
            f"{rtts * rtt + SERVER_THINK_MS:>11.0f} ms" for rtt in RTT_MS_SCENARIOS
        )
        print(f"  {label:<28}{rtts:>5}{cells}")
    print("\n  -> a pooled (or 0-RTT-resumed) connection reaches first byte 4x")
    print("     faster than TCP + TLS 1.2 on the same wire. Nothing got faster —")
    print("     we just stopped paying for round trips we did not need.\n")


def main() -> None:
    experiment_1_connect_vs_reuse()
    experiment_2_page_load_strategies()
    experiment_3_time_to_first_byte()
    print("Done. Now do the README exercises: predict, edit CONFIG, re-run, compare.")


if __name__ == "__main__":
    main()
