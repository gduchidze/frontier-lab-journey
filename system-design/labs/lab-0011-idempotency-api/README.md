# Lab 0011 — Idempotency API Lab

Companion to [Lesson 0011](../../lessons/0011-api-design-deep.html). Everything the lesson claimed — the double-charge problem, Stripe-style idempotency keys, pagination drift under live inserts — you now verify against a real (tiny) HTTP server running in a thread. Rule of the lab: **predict before you run.** Write your prediction down; the gap between prediction and output is where the learning is.

```bash
python3 idempotency_lab.py
```

Three experiments: (1) a client POSTs `/charge` for 200 orders while the network "eats" 30% of responses and the client naively retries — count the double charges in the ledger, (2) the identical traffic with an `Idempotency-Key` header and a server-side key store — zero doubles, plus retried `DELETE` refunds staying safe because DELETE is idempotent by contract, (3) offset pagination over an orders table while new orders keep arriving between pages — duplicated and missed rows — versus a cursor that seeks by id, which stays clean.

The trick that makes it honest: "response loss" is simulated **after** the server has done the work. The money moved; the confirmation didn't. That is exactly what a client timeout on POST looks like from the server's side.

## Exercises

All edits happen in the `CONFIG` block at the top of `idempotency_lab.py`.

### E1 — Predict the double-charge count
With `RESPONSE_LOSS = 0.30` and `MAX_RETRIES = 3`, each order is attempted until a response arrives (max 4 attempts), and *every attempt charges*. Expected attempts per order = 1 + 0.3 + 0.3² + 0.3³ ≈ 1.417, so ≈ 0.417 × 200 ≈ **83 expected doubles**. The run shows ~90 (sampling noise). Now predict the doubles at `RESPONSE_LOSS = 0.5`, run, compare. Then restore.

### E2 — Break the key store with TTL
Shrink `IDEMPOTENCY_TTL_S` from `60.0` to `0.001` — now smaller than `RETRY_DELAY_S` (0.01 s), so the key expires *inside the retry window*. Predict the keyed row's DOUBLE-charges column before running. Lesson: an idempotency key store must outlive the longest plausible retry (Stripe prunes keys after 24 h, not milliseconds). Restore.

### E3 — Raise the insert rate during offset pagination
Predict how `duplicates` and `missed` change when `INSERTS_PER_PAGE` goes from `4` to `10` (one insert per row served!). Run, compare, and explain why the cursor row *still* shows 0/0. Then try `0` — with no concurrent inserts, why do offset and cursor tie?

### E4 — Make DELETE non-idempotent
Set `NON_IDEMPOTENT_DELETE = True`. The server now appends a refund record on *every* DELETE instead of checking the ledger first. Predict the refund count (50 charges refunded, 30% response loss, retries) before running. This is what any retried non-idempotent endpoint does to your books — POST just gets the blame because it is non-idempotent *by default*.

### E5 — Stretch: webhook with HMAC + redelivery dedup
Add a `POST /webhook` consumer endpoint and a `deliver_webhook()` helper that signs the JSON body with `hmac.new(secret, body, hashlib.sha256)` in an `X-Signature` header (compare with `hmac.compare_digest`, never `==`). Deliver each event twice (at-least-once redelivery) and make the consumer keep a `seen_event_ids` set so the second delivery is a no-op. You have now implemented both halves of the Stripe/GitHub webhook contract: verify, then dedupe.

## Deliverable

A short note (5 lines) answering E1–E4: prediction vs observed, one sentence each. Bring it to the next session — wrong predictions are the most useful thing you can bring, and they become learning records.
