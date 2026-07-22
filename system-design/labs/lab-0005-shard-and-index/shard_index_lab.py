"""Lab 0005 — Shard and Index.

Three experiments that turn Lesson 0005's claims into things you've seen
with your own eyes. Run:  python3 shard_index_lab.py

  1. A 300k-row messages table: point + range queries WITHOUT an index
     vs WITH one, with EXPLAIN QUERY PLAN receipts.
  2. Composite index ordering: (user_id, created_at) vs (created_at, user_id)
     for "last 50 messages of user X".
  3. Sharding by hash(user_id) % 4: balanced under uniform activity, a hot
     shard under Zipf activity, and a cross-shard top-10 query that forces
     scatter-gather.

Stdlib only. Uses in-memory SQLite plus temp files that clean themselves up.
Then do the exercises in README.md — edit the CONFIG block and predict the
output BEFORE re-running.
"""

from __future__ import annotations

import random
import sqlite3
import tempfile
import time
import zlib
from pathlib import Path

# ---------------------------------------------------------------- CONFIG
# The exercises in README.md ask you to change these and predict results.
N_ROWS = 300_000          # messages generated per workload
N_USERS = 2_000           # distinct users
CONVS_PER_USER = 20       # conversations per user
DAYS_OF_DATA = 30         # created_at spread
RANGE_HOURS = 6           # width of the range query in experiment 1
LAST_N = 50               # "last N messages of user X" in experiment 2
N_SHARDS = 4              # experiment 3
ZIPF_EXPONENT = 1.2       # 0 = uniform activity; higher = more skew
TIMING_REPEATS = 5        # each query timed this many times, best kept
SEED = 7
# -----------------------------------------------------------------------

BASE_TS = 1_700_000_000
SPAN_S = DAYS_OF_DATA * 86_400


def make_rows(rng: random.Random, user_ids: list[int]) -> list[tuple]:
    """(user_id, conversation_id, created_at, body) for each user id given."""
    return [
        (u,
         u * 100 + rng.randrange(CONVS_PER_USER),
         BASE_TS + rng.randrange(SPAN_S),
         f"m{i}")
        for i, u in enumerate(user_ids)
    ]


def fresh_db(path: str = ":memory:") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA journal_mode=OFF")
    conn.execute("PRAGMA synchronous=OFF")
    return conn


def create_messages_table(conn: sqlite3.Connection, name: str, rows: list[tuple]) -> None:
    conn.execute(f"CREATE TABLE {name} (user_id INT, conversation_id INT, "
                 "created_at INT, body TEXT)")
    conn.executemany(f"INSERT INTO {name} VALUES (?,?,?,?)", rows)
    conn.commit()


def best_ms(conn: sqlite3.Connection, sql: str, params: tuple) -> tuple[float, int]:
    """Best-of-TIMING_REPEATS wall time in ms, plus row count returned."""
    best, n = float("inf"), 0
    for _ in range(TIMING_REPEATS):
        t0 = time.perf_counter()
        n = len(conn.execute(sql, params).fetchall())
        best = min(best, (time.perf_counter() - t0) * 1000.0)
    return best, n


def plan_of(conn: sqlite3.Connection, sql: str, params: tuple) -> str:
    rows = conn.execute("EXPLAIN QUERY PLAN " + sql, params).fetchall()
    return "; ".join(r[3] for r in rows)


def shard_of(user_id: int) -> int:
    return zlib.crc32(str(user_id).encode()) % N_SHARDS


# ---------------------------------------------------------- EXPERIMENT 1
def experiment_1_index_vs_scan(conn: sqlite3.Connection) -> None:
    print("=" * 78)
    print(f"EXPERIMENT 1 — index vs full scan on a {N_ROWS:,}-row messages table")
    print("=" * 78)
    target_conv = 123_400 + 3          # a real conversation of user 1234
    t0 = BASE_TS + 15 * 86_400
    queries = [
        ("point lookup",
         "SELECT * FROM messages WHERE conversation_id = ?", (target_conv,)),
        (f"range ({RANGE_HOURS}h of {DAYS_OF_DATA}d)",
         "SELECT * FROM messages WHERE created_at BETWEEN ? AND ?",
         (t0, t0 + RANGE_HOURS * 3600)),
    ]

    before = [(label, *best_ms(conn, sql, p), plan_of(conn, sql, p))
              for label, sql, p in queries]

    t_ix = time.perf_counter()
    conn.execute("CREATE INDEX ix_conv ON messages(conversation_id)")
    conn.execute("CREATE INDEX ix_created ON messages(created_at)")
    conn.commit()
    ix_ms = (time.perf_counter() - t_ix) * 1000.0

    print(f"{'query':<22} {'no index':>10} {'with index':>11} {'speedup':>8}  rows")
    for (label, sql, p), (_, ms0, n0, plan0) in zip(queries, before):
        ms1, _ = best_ms(conn, sql, p)
        print(f"{label:<22} {ms0:>8.2f}ms {ms1:>9.3f}ms {ms0 / ms1:>7.0f}x  {n0:>5}")
        print(f"  plan before: {plan0}")
        print(f"  plan after : {plan_of(conn, sql, p)}")
    print(f"\n  -> building the two indexes itself cost {ix_ms:.0f} ms of writes —")
    print("     write amplification is the permanent rent for these reads.\n")


# ---------------------------------------------------------- EXPERIMENT 2
def experiment_2_composite_order(conn: sqlite3.Connection, rows: list[tuple]) -> None:
    print("=" * 78)
    print(f"EXPERIMENT 2 — composite ordering: last {LAST_N} messages of user X")
    print("=" * 78)
    create_messages_table(conn, "msg_good", rows)
    create_messages_table(conn, "msg_bad", rows)
    conn.execute("CREATE INDEX ix_good ON msg_good(user_id, created_at)")
    conn.execute("CREATE INDEX ix_bad  ON msg_bad(created_at, user_id)")
    conn.commit()

    sql = ("SELECT created_at, body FROM {t} WHERE user_id = ? "
           "ORDER BY created_at DESC LIMIT ?")
    params = (1234, LAST_N)
    results = {}
    for label, table in [("(user_id, created_at)", "msg_good"),
                         ("(created_at, user_id)", "msg_bad")]:
        q = sql.format(t=table)
        ms, n = best_ms(conn, q, params)
        results[label] = ms
        print(f"index {label:<22} {ms:>9.3f} ms   ({n} rows)")
        print(f"  plan: {plan_of(conn, q, params)}")
    ratio = results["(created_at, user_id)"] / results["(user_id, created_at)"]
    print(f"\n  -> same data, same query, columns swapped: {ratio:.0f}x slower.")
    print("     Equality column first, range/sort column last — or the index")
    print("     is a phone book you are reading by first name.\n")


# ---------------------------------------------------------- EXPERIMENT 3
def experiment_3_sharding(rng: random.Random, uniform_rows: list[tuple]) -> None:
    print("=" * 78)
    print(f"EXPERIMENT 3 — {N_SHARDS} shards by hash(user_id) % {N_SHARDS}")
    print("=" * 78)
    weights = [1.0 / (rank ** ZIPF_EXPONENT) for rank in range(1, N_USERS + 1)]
    zipf_users = rng.choices(range(N_USERS), weights=weights, k=N_ROWS)
    zipf_rows = make_rows(rng, zipf_users)

    with tempfile.TemporaryDirectory(prefix="lab0005_shards_") as tmp:
        paths = [Path(tmp) / f"shard_{i}.db" for i in range(N_SHARDS)]
        for label, rows in [("uniform activity", uniform_rows),
                            (f"zipf activity (s={ZIPF_EXPONENT})", zipf_rows)]:
            shards = [fresh_db(str(p)) for p in paths]
            buckets: list[list[tuple]] = [[] for _ in range(N_SHARDS)]
            for row in rows:
                buckets[shard_of(row[0])].append(row)
            for conn, bucket in zip(shards, buckets):
                conn.execute("DROP TABLE IF EXISTS messages")
                create_messages_table(conn, "messages", bucket)
            print(f"per-shard row counts — {label}:")
            for i, conn in enumerate(shards):
                (count,) = conn.execute("SELECT COUNT(*) FROM messages").fetchone()
                pct = 100.0 * count / N_ROWS
                print(f"  shard {i}: {count:>7,} rows  {pct:5.1f}%  {'#' * int(pct)}")
            if "zipf" in label:
                scatter_gather_top10(shards)
            for conn in shards:
                conn.close()
        print(f"  (temp shard files under {tmp} — deleted automatically)\n")


def scatter_gather_top10(shards: list[sqlite3.Connection]) -> None:
    print("\ncross-shard query: top 10 most active users overall")
    print("  no shard can answer alone -> scatter to all "
          f"{N_SHARDS} shards, gather, merge:")
    merged: list[tuple[int, int]] = []
    for i, conn in enumerate(shards):
        top = conn.execute("SELECT user_id, COUNT(*) c FROM messages "
                           "GROUP BY user_id ORDER BY c DESC LIMIT 10").fetchall()
        print(f"  shard {i} local top-1: user {top[0][0]:>4} ({top[0][1]:,} msgs)"
              f"   [1 of {N_SHARDS} queries]")
        merged.extend(top)
    merged.sort(key=lambda t: -t[1])
    global_top = ", ".join(f"u{u}:{c:,}" for u, c in merged[:10])
    print(f"  merged global top-10: {global_top}")
    print(f"  -> {N_SHARDS} queries + a merge for one question. Lesson 0001's "
          "fan-out math now applies to your database.\n")


def main() -> None:
    rng = random.Random(SEED)
    uniform_users = [rng.randrange(N_USERS) for _ in range(N_ROWS)]
    uniform_rows = make_rows(rng, uniform_users)

    conn = fresh_db()
    print(f"building {N_ROWS:,}-row messages table "
          f"({N_USERS:,} users, {DAYS_OF_DATA} days)...\n")
    create_messages_table(conn, "messages", uniform_rows)

    experiment_1_index_vs_scan(conn)
    experiment_2_composite_order(conn, uniform_rows)
    conn.close()
    experiment_3_sharding(rng, uniform_rows)
    print("Done. Now do the README exercises: predict, edit CONFIG, re-run, compare.")


if __name__ == "__main__":
    main()
