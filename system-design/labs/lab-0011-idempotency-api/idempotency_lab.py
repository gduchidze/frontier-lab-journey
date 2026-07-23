"""Lab 0011 — Idempotency API Lab.

A tiny payments API (stdlib http.server, running in a thread) plus a
client with a deliberately flaky network. Three experiments that turn
Lesson 0011's claims into numbers:

  1. Naive retry on POST /charge with 30% response loss -> double charges.
  2. Same traffic with an Idempotency-Key header + server key store ->
     zero doubles (Stripe's model), plus retried DELETE refunds staying safe.
  3. Offset pagination over a live-inserting orders table -> duplicated /
     missed rows; cursor (seek by id) pagination -> clean.

Run:  python3 idempotency_lab.py     (finishes in a few seconds)

"Response loss" is simulated on the client side AFTER the server has
done the work — semantically identical to a lost response packet: the
money moved, the confirmation didn't. Seeded RNG, so runs reproduce.
"""

from __future__ import annotations

import http.client
import json
import random
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

# ---------------------------------------------------------------- CONFIG
# The exercises in README.md ask you to change these and predict results.
NUM_ORDERS = 200            # orders to charge in experiments 1 and 2
RESPONSE_LOSS = 0.30        # P(response lost after server did the work)
MAX_RETRIES = 3             # client retries after the initial attempt
RETRY_DELAY_S = 0.01        # pause between attempts (the "retry window")
IDEMPOTENCY_TTL_S = 60.0    # server key-store TTL (E2: shrink below window)
NON_IDEMPOTENT_DELETE = False   # E4: True makes DELETE append blindly
NUM_REFUNDS = 50            # experiment 2: charges to refund with retries
ORDERS_SEEDED = 120         # experiment 3: rows present when paging starts
PAGE_SIZE = 10              # experiment 3: rows per page
INSERTS_PER_PAGE = 4        # experiment 3: new orders landing between pages
SEED = 11
# -----------------------------------------------------------------------


class State:
    """All server-side state, guarded by one lock."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.ledger: list[dict] = []          # charge + refund records
        self.idem_store: dict[str, tuple[float, int, bytes]] = {}
        self.orders: list[dict] = []          # {"id": int, "item": str}
        self.next_order_id = 1

    def reset_payments(self) -> None:
        with self.lock:
            self.ledger.clear()
            self.idem_store.clear()

    def seed_orders(self, n: int) -> None:
        with self.lock:
            self.orders.clear()
            self.next_order_id = 1
            for _ in range(n):
                self._insert_order_locked()

    def insert_order(self) -> None:
        with self.lock:
            self._insert_order_locked()

    def _insert_order_locked(self) -> None:
        self.orders.append({"id": self.next_order_id,
                            "item": f"sku-{self.next_order_id % 7}"})
        self.next_order_id += 1


STATE = State()


class Handler(BaseHTTPRequestHandler):
    """POST /charge, DELETE /charge/<id>, GET /orders (offset or cursor)."""

    def log_message(self, *_args) -> None:   # silence request logging
        pass

    def _send(self, status: int, body: dict, replayed: bool = False) -> None:
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        if replayed:
            self.send_header("Idempotent-Replayed", "true")
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/charge":
            self._send(404, {"error": "not_found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(length))
        key = self.headers.get("Idempotency-Key")
        with STATE.lock:
            now = time.monotonic()
            if key is not None:
                # purge expired keys, then try to replay
                for k in [k for k, (t, _, _) in STATE.idem_store.items()
                          if now - t > IDEMPOTENCY_TTL_S]:
                    del STATE.idem_store[k]
                if key in STATE.idem_store:
                    _, status, body = STATE.idem_store[key]
                    self._send(status, json.loads(body), replayed=True)
                    return
            charge_id = f"ch_{len(STATE.ledger) + 1:04d}"
            STATE.ledger.append({"type": "charge", "id": charge_id,
                                 "order_id": payload["order_id"],
                                 "amount": payload["amount"]})
            body = {"charge_id": charge_id, "status": "succeeded"}
            if key is not None:
                STATE.idem_store[key] = (now, 201, json.dumps(body).encode())
        self._send(201, body)

    def do_DELETE(self) -> None:
        parts = urlparse(self.path).path.strip("/").split("/")
        if len(parts) != 2 or parts[0] != "charge":
            self._send(404, {"error": "not_found"})
            return
        charge_id = parts[1]
        with STATE.lock:
            already = any(r["type"] == "refund" and r["charge_id"] == charge_id
                          for r in STATE.ledger)
            if NON_IDEMPOTENT_DELETE or not already:
                STATE.ledger.append({"type": "refund", "charge_id": charge_id})
        self._send(204, {})

    def do_GET(self) -> None:
        url = urlparse(self.path)
        if url.path != "/orders":
            self._send(404, {"error": "not_found"})
            return
        q = parse_qs(url.query)
        limit = int(q.get("limit", ["10"])[0])
        with STATE.lock:
            newest_first = sorted(STATE.orders, key=lambda o: -o["id"])
            if "before_id" in q or "cursor" in q:      # cursor: seek by id
                before = int(q.get("before_id", q.get("cursor", ["0"]))[0])
                rows = [o for o in newest_first if o["id"] < before][:limit] \
                    if before else newest_first[:limit]
            else:                                      # offset pagination
                offset = int(q.get("offset", ["0"])[0])
                rows = newest_first[offset:offset + limit]
        next_cursor = rows[-1]["id"] if rows else None
        self._send(200, {"orders": rows, "next_cursor": next_cursor})


class SimulatedTimeout(Exception):
    """The server answered, but the network 'ate' the response."""


class FlakyClient:
    """HTTP client whose responses vanish with probability RESPONSE_LOSS."""

    def __init__(self, port: int, rng: random.Random) -> None:
        self.port = port
        self.rng = rng

    def request(self, method: str, path: str, body: dict | None = None,
                headers: dict | None = None, flaky: bool = True) -> dict:
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        data = json.dumps(body) if body is not None else None
        conn.request(method, path, body=data, headers=headers or {})
        resp = conn.getresponse()
        raw = resp.read()
        conn.close()
        if flaky and self.rng.random() < RESPONSE_LOSS:
            raise SimulatedTimeout(path)      # work done, confirmation lost
        return json.loads(raw) if raw else {}

    def with_retries(self, method: str, path: str, body: dict | None = None,
                     headers: dict | None = None) -> tuple[bool, int]:
        """Retry loop. Returns (client_saw_success, attempts_made)."""
        attempts = 0
        for _ in range(1 + MAX_RETRIES):
            attempts += 1
            try:
                self.request(method, path, body, headers)
                return True, attempts
            except SimulatedTimeout:
                time.sleep(RETRY_DELAY_S)
        return False, attempts


def charge_orders(client: FlakyClient, use_key: bool) -> dict:
    STATE.reset_payments()
    gave_up = 0
    for i in range(NUM_ORDERS):
        headers = {"Idempotency-Key": f"order-{i}"} if use_key else {}
        ok, _ = client.with_retries(
            "POST", "/charge", {"order_id": i, "amount": 100}, headers)
        if not ok:
            gave_up += 1
    charges = [r for r in STATE.ledger if r["type"] == "charge"]
    charged_orders = {r["order_id"] for r in charges}
    doubles = len(charges) - len(charged_orders)
    ghost = sum(1 for i in range(NUM_ORDERS)
                if i in charged_orders) - (NUM_ORDERS - gave_up)
    return {"charges": len(charges), "orders_charged": len(charged_orders),
            "doubles": doubles, "gave_up": gave_up,
            "ghost_charges": max(ghost, 0)}


def experiment_1_and_2(client: FlakyClient) -> None:
    print("=" * 78)
    print(f"EXPERIMENTS 1+2 — POST /charge for {NUM_ORDERS} orders, "
          f"{RESPONSE_LOSS:.0%} response loss, {MAX_RETRIES} retries")
    print("=" * 78)
    naive = charge_orders(client, use_key=False)
    keyed = charge_orders(client, use_key=True)

    print(f"  {'strategy':<26} {'ledger charges':>14} {'orders charged':>14} "
          f"{'DOUBLE charges':>14} {'client gave up':>14}")
    for label, r in (("naive retry (no key)", naive),
                     ("Idempotency-Key + store", keyed)):
        print(f"  {label:<26} {r['charges']:>14} {r['orders_charged']:>14} "
              f"{r['doubles']:>14} {r['gave_up']:>14}")
    print(f"\n  -> naive: every retried attempt charged the card again — "
          f"{naive['doubles']} double charges;")
    print(f"     {naive['ghost_charges']} order(s) where the client saw "
          f"FAILURE but money moved anyway.")
    print(f"     keyed: server replayed the stored response instead of "
          f"re-executing — {keyed['doubles']} doubles.")

    # Refunds: DELETE is idempotent by contract — retries should be harmless.
    refunds_expected = min(NUM_REFUNDS, keyed["charges"])
    for n in range(1, refunds_expected + 1):
        client.with_retries("DELETE", f"/charge/ch_{n:04d}")
    refunds = sum(1 for r in STATE.ledger if r["type"] == "refund")
    tag = "(idempotent — retries safe)" if not NON_IDEMPOTENT_DELETE \
        else "(NON-idempotent — E4 mode)"
    print(f"\n  DELETE /charge refunds: expected {refunds_expected}, "
          f"ledger shows {refunds} {tag}\n")


def paginate_offset(client: FlakyClient, budget_pages: int) -> list[int]:
    seen: list[int] = []
    for page in range(budget_pages):
        body = client.request(
            "GET", f"/orders?offset={page * PAGE_SIZE}&limit={PAGE_SIZE}",
            flaky=False)
        seen += [o["id"] for o in body["orders"]]
        for _ in range(INSERTS_PER_PAGE):     # live traffic between pages
            STATE.insert_order()
    return seen


def paginate_cursor(client: FlakyClient) -> list[int]:
    seen: list[int] = []
    cursor: int | None = None
    while True:
        path = f"/orders?limit={PAGE_SIZE}"
        if cursor is not None:
            path += f"&before_id={cursor}"
        body = client.request("GET", path, flaky=False)
        rows = [o["id"] for o in body["orders"]]
        if not rows:
            return seen
        seen += rows
        cursor = body["next_cursor"]
        for _ in range(INSERTS_PER_PAGE):
            STATE.insert_order()


def experiment_3_pagination(client: FlakyClient) -> None:
    print("=" * 78)
    print(f"EXPERIMENT 3 — paginate {ORDERS_SEEDED} orders (newest-first), "
          f"{INSERTS_PER_PAGE} new orders arrive between pages")
    print("=" * 78)
    budget = ORDERS_SEEDED // PAGE_SIZE       # pages a batch job would plan

    STATE.seed_orders(ORDERS_SEEDED)
    snapshot = {o["id"] for o in STATE.orders}
    off = paginate_offset(client, budget)
    off_dupes = len(off) - len(set(off))
    off_missed = len(snapshot - set(off))

    STATE.seed_orders(ORDERS_SEEDED)
    snapshot = {o["id"] for o in STATE.orders}
    cur = paginate_cursor(client)
    cur_dupes = len(cur) - len(set(cur))
    cur_missed = len(snapshot - set(cur))

    print(f"  {'method':<22} {'rows fetched':>12} {'duplicates':>10} "
          f"{'missed':>7}   verdict")
    print(f"  {'offset pagination':<22} {len(off):>12} {off_dupes:>10} "
          f"{off_missed:>7}   drift: inserts push rows down -> re-read")
    print(f"  {'cursor (seek by id)':<22} {len(cur):>12} {cur_dupes:>10} "
          f"{cur_missed:>7}   stable: cursor pins the position")
    print("\n  -> offset pages are positions, not identities: every insert at")
    print("     the head shifts the window, so a batch job double-processes")
    print("     (double-ships!) rows and never reaches the tail. The cursor")
    print("     seeks by id, so concurrent inserts cannot move the window.\n")


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    client = FlakyClient(server.server_address[1], random.Random(SEED))

    experiment_1_and_2(client)
    experiment_3_pagination(client)
    server.shutdown()
    print("Done. Now do the README exercises: predict, edit CONFIG, "
          "re-run, compare.")


if __name__ == "__main__":
    main()
