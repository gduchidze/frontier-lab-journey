"""Lab 0003 — Toy Load Balancer.

Three real HTTP backends + a load balancer with a pluggable routing
strategy and background health checks. Run the demo:

    python3 toy_lb.py --demo

Phase 1 sends 30 requests through the balancer and prints the
per-backend distribution. Phase 2 kills one backend mid-run so you can
watch health checks and failover do their job.

If the environment forbids binding localhost sockets, the demo
automatically falls back to an in-process simulation that exercises the
exact same strategy and health-check code paths and prints the same
tables.

Then do the exercises in README.md — they all involve editing the
CONFIG block below and predicting the output BEFORE re-running.
"""

from __future__ import annotations

import argparse
import http.server
import statistics
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field

# ---------------------------------------------------------------- CONFIG
# The exercises in README.md ask you to change these and predict results.
BACKEND_DELAYS_MS = [30.0, 30.0, 30.0]  # E1: skew these, e.g. [10, 10, 300]
STRATEGY = "round_robin"                # E2: "round_robin" | "least_connections"
HEALTH_INTERVAL_S = 0.25                # E3: how often the LB probes each backend
FAILS_TO_MARK_DOWN = 2                  # E3: consecutive failures before "down"
REQUESTS_PER_PHASE = 30                 # requests sent in each demo phase
KILL_AFTER = 8                          # phase 2: kill a backend after this many
CLIENT_CONCURRENCY = 4                  # parallel clients (matters for least_connections)
LB_PORT = 8900
BACKEND_PORTS = [8901, 8902, 8903]
REQUEST_TIMEOUT_S = 5.0
# -----------------------------------------------------------------------


@dataclass
class Backend:
    """One app server, as the load balancer sees it."""
    bid: str
    delay_ms: float
    port: int = 0
    alive: bool = True          # ground truth: is the "process" running?
    healthy: bool = True        # the LB's belief, driven by health checks
    consecutive_fails: int = 0
    in_flight: int = 0
    served: int = 0
    errors: int = 0


class SimTransport:
    """In-process stand-in for the network: same failures, no sockets."""

    def send(self, backend: Backend) -> str:
        if not backend.alive:
            raise ConnectionError(f"{backend.bid} is dead")
        time.sleep(backend.delay_ms / 1000.0)
        return f"hello from {backend.bid}"

    def probe(self, backend: Backend) -> None:
        if not backend.alive:
            raise ConnectionError(f"{backend.bid} failed health check")


class HttpTransport:
    """Real localhost HTTP to the backend servers."""

    def send(self, backend: Backend) -> str:
        url = f"http://127.0.0.1:{backend.port}/"
        with urllib.request.urlopen(url, timeout=REQUEST_TIMEOUT_S) as resp:
            return resp.read().decode()

    def probe(self, backend: Backend) -> None:
        url = f"http://127.0.0.1:{backend.port}/health"
        with urllib.request.urlopen(url, timeout=1.0) as resp:
            resp.read()


class LoadBalancer:
    """Pluggable-strategy balancer with active health checks and retry."""

    def __init__(self, backends: list[Backend], strategy: str, transport) -> None:
        if strategy not in ("round_robin", "least_connections"):
            raise ValueError(f"unknown strategy: {strategy!r}")
        self.backends = backends
        self.strategy = strategy
        self.transport = transport
        self._lock = threading.Lock()
        self._rr_index = 0
        self._stop = threading.Event()

    # -------------------------------------------------- routing strategy
    def _pick(self) -> Backend | None:
        with self._lock:
            pool = [b for b in self.backends if b.healthy]
            if not pool:
                return None
            if self.strategy == "round_robin":
                chosen = pool[self._rr_index % len(pool)]
                self._rr_index += 1
            else:  # least_connections; tie-break on served so idle traffic spreads
                chosen = min(pool, key=lambda b: (b.in_flight, b.served))
            chosen.in_flight += 1
            return chosen

    def _release(self, backend: Backend, ok: bool) -> None:
        with self._lock:
            backend.in_flight -= 1
            if ok:
                backend.served += 1
                backend.consecutive_fails = 0
            else:
                backend.errors += 1
                backend.consecutive_fails += 1
                if backend.consecutive_fails >= FAILS_TO_MARK_DOWN and backend.healthy:
                    backend.healthy = False
                    print(f"  [lb]     {backend.bid} marked DOWN (passive: request failures)")

    # -------------------------------------------------------- data path
    def handle(self) -> str:
        """Route one request; on backend failure, retry the next pick."""
        last_error: Exception | None = None
        for _ in range(len(self.backends)):
            backend = self._pick()
            if backend is None:
                raise RuntimeError("no healthy backends in rotation")
            try:
                body = self.transport.send(backend)
                self._release(backend, ok=True)
                return body
            except Exception as exc:  # dead socket, timeout, sim failure
                self._release(backend, ok=False)
                last_error = exc
        raise RuntimeError(f"all backends failed; last error: {last_error}")

    # ----------------------------------------------------- health checks
    def health_loop(self) -> None:
        """Background probe of every backend, forever (daemon thread)."""
        while not self._stop.is_set():
            for backend in self.backends:
                try:
                    self.transport.probe(backend)
                    with self._lock:
                        if not backend.healthy:
                            print(f"  [health] {backend.bid} recovered -> back in rotation")
                        backend.healthy = True
                        backend.consecutive_fails = 0
                except Exception:
                    with self._lock:
                        backend.consecutive_fails += 1
                        if (backend.consecutive_fails >= FAILS_TO_MARK_DOWN
                                and backend.healthy):
                            backend.healthy = False
                            print(f"  [health] {backend.bid} marked DOWN "
                                  f"after {backend.consecutive_fails} failed checks")
            self._stop.wait(HEALTH_INTERVAL_S)

    def stop(self) -> None:
        self._stop.set()


# ------------------------------------------------------------ HTTP servers
def _make_backend_handler(backend: Backend):
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 (stdlib naming)
            if self.path != "/health":
                time.sleep(backend.delay_ms / 1000.0)
            body = f"hello from {backend.bid}".encode()
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):  # keep demo output clean
            pass

    return Handler


def _make_lb_handler(lb: LoadBalancer):
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            try:
                body = lb.handle().encode()
                status = 200
            except Exception as exc:
                body = f"lb error: {exc}".encode()
                status = 503
            self.send_response(status)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    return Handler


def start_http_stack(backends: list[Backend]):
    """Bind and start all servers. Returns None if binding is forbidden."""
    servers: dict[str, http.server.ThreadingHTTPServer] = {}
    lb = LoadBalancer(backends, STRATEGY, HttpTransport())
    try:
        for backend in backends:
            srv = http.server.ThreadingHTTPServer(
                ("127.0.0.1", backend.port), _make_backend_handler(backend))
            servers[backend.bid] = srv
        lb_server = http.server.ThreadingHTTPServer(
            ("127.0.0.1", LB_PORT), _make_lb_handler(lb))
    except OSError as exc:
        for srv in servers.values():
            srv.server_close()
        print(f"  [warn] could not bind localhost sockets ({exc}) — "
              f"falling back to in-process simulation")
        return None
    for srv in list(servers.values()) + [lb_server]:
        threading.Thread(target=srv.serve_forever, daemon=True).start()
    return servers, lb_server, lb


# ------------------------------------------------------------ demo helpers
def percentile(sorted_values: list[float], p: float) -> float:
    idx = min(int(len(sorted_values) * p), len(sorted_values) - 1)
    return sorted_values[idx]


def blast(send, n: int, concurrency: int) -> tuple[list[float], int]:
    """Fire n requests from `concurrency` client threads; return (latencies_ms, errors)."""
    lock = threading.Lock()
    remaining = [n]
    latencies: list[float] = []
    errors = [0]

    def worker() -> None:
        while True:
            with lock:
                if remaining[0] == 0:
                    return
                remaining[0] -= 1
            t0 = time.perf_counter()
            try:
                send()
                ok = True
            except Exception:
                ok = False
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            with lock:
                if ok:
                    latencies.append(elapsed_ms)
                else:
                    errors[0] += 1

    threads = [threading.Thread(target=worker, daemon=True) for _ in range(concurrency)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return latencies, errors[0]


def snapshot(backends: list[Backend]) -> dict[str, tuple[int, int]]:
    return {b.bid: (b.served, b.errors) for b in backends}


def print_latency(latencies: list[float], client_errors: int) -> None:
    if not latencies:
        print("  no successful requests!")
        return
    s = sorted(latencies)
    print(f"  client latency ms: mean={statistics.fmean(s):7.1f}  "
          f"p50={percentile(s, 0.50):7.1f}  p99={percentile(s, 0.99):7.1f}  "
          f"(n={len(s)}, client-visible errors={client_errors})")


def print_table(backends: list[Backend], before: dict[str, tuple[int, int]]) -> None:
    total = sum(b.served - before[b.bid][0] for b in backends) or 1
    print("  backend      delay_ms  healthy  served  errors  share")
    for b in backends:
        served = b.served - before[b.bid][0]
        errors = b.errors - before[b.bid][1]
        bar = "#" * round(served / total * 20)
        health = "yes" if b.healthy else "NO"
        print(f"  {b.bid:<12} {b.delay_ms:8.0f}  {health:>7}  {served:6d}  "
              f"{errors:6d}  {bar} {served / total:.0%}")


# ------------------------------------------------------------------- demo
def run_demo(lb: LoadBalancer, send, kill, mode: str) -> None:
    print("=" * 78)
    print(f"TOY LOAD BALANCER — mode={mode}, strategy={STRATEGY}")
    print("backends: " + ", ".join(f"{b.bid}({b.delay_ms:.0f}ms)" for b in lb.backends))
    print(f"health checks every {HEALTH_INTERVAL_S}s, "
          f"down after {FAILS_TO_MARK_DOWN} consecutive failures")
    print("=" * 78)

    threading.Thread(target=lb.health_loop, daemon=True).start()

    print(f"\nPHASE 1 — {REQUESTS_PER_PHASE} requests, all backends up")
    before = snapshot(lb.backends)
    latencies, errs = blast(send, REQUESTS_PER_PHASE, CLIENT_CONCURRENCY)
    print_latency(latencies, errs)
    print_table(lb.backends, before)

    victim = lb.backends[1]
    print(f"\nPHASE 2 — {REQUESTS_PER_PHASE} requests, "
          f"killing {victim.bid} after the first {KILL_AFTER}")
    before = snapshot(lb.backends)
    lat1, err1 = blast(send, KILL_AFTER, CLIENT_CONCURRENCY)
    kill(victim)
    print(f"  [demo]   {victim.bid} killed mid-run — watch detection and failover")
    lat2, err2 = blast(send, REQUESTS_PER_PHASE - KILL_AFTER, CLIENT_CONCURRENCY)
    print_latency(lat1 + lat2, err1 + err2)
    print_table(lb.backends, before)
    print(f"\n  -> {victim.bid} left the rotation; survivors absorbed its share.")
    print("     The LB retried failed picks on other backends, so clients saw "
          f"{err1 + err2} errors.")

    lb.stop()
    print("\nDone. Now do the README exercises: predict, edit CONFIG, re-run, compare.")


def build_backends() -> list[Backend]:
    return [
        Backend(bid=f"backend-{i + 1}", delay_ms=float(delay), port=port)
        for i, (delay, port) in enumerate(zip(BACKEND_DELAYS_MS, BACKEND_PORTS))
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true",
                        help="run the finite two-phase demo and exit")
    args = parser.parse_args()

    backends = build_backends()

    if not args.demo:
        stack = start_http_stack(backends)
        if stack is None:
            print("Serve mode needs sockets. Try:  python3 toy_lb.py --demo")
            return
        servers, lb_server, _lb = stack
        print(f"LB listening on http://127.0.0.1:{LB_PORT}/  (Ctrl+C to stop)")
        for b in backends:
            print(f"  {b.bid} on http://127.0.0.1:{b.port}/  delay={b.delay_ms:.0f}ms")
        try:
            threading.Event().wait()
        except KeyboardInterrupt:
            pass
        finally:
            lb_server.shutdown()
            for srv in servers.values():
                srv.shutdown()
        return

    stack = start_http_stack(backends)
    if stack is not None:
        servers, lb_server, lb = stack
        lb_url = f"http://127.0.0.1:{LB_PORT}/"

        def send() -> None:
            with urllib.request.urlopen(lb_url, timeout=REQUEST_TIMEOUT_S) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"lb returned {resp.status}")
                resp.read()

        def kill(backend: Backend) -> None:
            backend.alive = False
            servers[backend.bid].shutdown()
            servers[backend.bid].server_close()

        try:
            run_demo(lb, send, kill, mode="real HTTP servers")
        finally:
            lb_server.shutdown()
            lb_server.server_close()
            for bid, srv in servers.items():
                if bid != "backend-2":  # backend-2 already closed by kill()
                    srv.shutdown()
                    srv.server_close()
    else:
        lb = LoadBalancer(backends, STRATEGY, SimTransport())

        def kill_sim(backend: Backend) -> None:
            backend.alive = False

        run_demo(lb, lb.handle, kill_sim, mode="in-process simulation")


if __name__ == "__main__":
    main()
