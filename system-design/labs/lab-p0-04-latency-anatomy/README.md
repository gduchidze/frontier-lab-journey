# Lab p0-04 — Latency Anatomy

Companion to [Lesson p0-04](../../lessons/p0-04-networking.html). The lesson claims that network latency is mostly *round trips you chose to pay*, not wire speed. Here you measure it. Rule of the lab: **predict before you run.** Write your prediction down; the gap between prediction and output is where the learning is.

```bash
python3 latency_anatomy_lab.py
```

Three experiments: (1) real sockets — a new TCP connection per request vs one reused connection, (2) page-load handshake math for HTTP/1.1 close / keep-alive / HTTP/2 / HTTP/3 across three RTTs, (3) the time-to-first-byte ladder from TCP+TLS 1.2 down to a pooled connection.

Runs in well under a minute. Experiment 1 is a real measurement (numbers vary per machine); experiments 2 and 3 are exact RTT arithmetic — your hand math must match the program to the millisecond.

## Exercises

All edits happen in the `CONFIG` block at the top of `latency_anatomy_lab.py`.

### E1 — Price the handshake
Predict: in experiment 1, roughly how many times slower is "new conn every request" than "one reused connection" on *your* machine — 2x, 10x, 100x? Run and compare mean and p99. Then predict what happens to the ratio if `PAYLOAD_BYTES = 16_384` (hint: setup cost is fixed; transfer cost is not). Edit, re-run, compare, restore.

### E2 — Downgrade TLS
Set `TLS_VERSION = "1.2"`. Predict *by hand*, before running: the new HTTP/1.1 `Connection: close` page-load time at RTT = 150 ms (formula: ceil(24/6) x (setup+1) x RTT), and the new "TCP + TLS 1.2" row in experiment 3. Re-run and check yourself to the millisecond. Restore to `"1.3"`.

### E3 — The mobile page
A resource-heavy page: `RESOURCES = 100`, RTT = 150 ms (last scenario). Predict the ordering and rough size of the four strategy totals first. Which strategy improves *most* over its 24-resource value, and why does HTTP/2 barely move? Re-run and compare. Restore.

### E4 — When the server is the bottleneck
Set `SERVER_THINK_MS = 200`. Predict: does the HTTP/3-vs-HTTP/1.1-close gap (in *ratio* terms) grow or shrink at RTT = 10 ms? What does this tell you about when protocol optimization matters vs when you should go profile the backend? Re-run, compare, restore.

### E5 — Stretch: measure a real handshake
Replace localhost with the internet: use `socket.create_connection(("example.com", 443))` timed with `time.perf_counter()` for 20 iterations, then wrap the socket with `ssl.create_default_context().wrap_socket(sock, server_hostname="example.com")` and time the TLS handshake separately. Compare TCP-connect time vs TLS-handshake time vs your ping RTT. Does TLS cost ~1 RTT or ~2 on your stack?

## Deliverable

A short note (5 lines) answering E1–E4: prediction vs observed, one sentence each. Bring it to the next session — wrong predictions are the most useful thing you can bring, and they become learning records.
