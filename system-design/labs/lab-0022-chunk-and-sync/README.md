# Lab 0022 — Chunk and Sync

Companion to [Lesson 0022](../../lessons/0022-file-sync.html). The lesson claims that one inserted byte forces a fixed-chunking client to re-upload nearly the whole file, while content-defined chunking (CDC) re-uploads one block. This lab makes you watch it happen — on a seeded synthetic file, with SHA-256 content addressing doing the dedup bookkeeping exactly the way a sync service would.

```bash
python3 sync_lab.py
```

Everything is stdlib and deterministic (`SEED = 22`): a 256 KB random "file" stands in for your 1 GB video, an 8 KB fixed block stands in for Dropbox's 4 MB one. Four experiments print, in order: baseline chunking stats, an in-place mid-file overwrite, a **1-byte insert near the start**, and cross-file dedup between two similar files. Each block's ID is its SHA-256 hash — a block the "server" has already seen uploads for free.

## Protocol

1. Write the prediction down **before** running or editing. A number, not a vibe.
2. Change one CONFIG value at a time; re-run; compare against your prediction.
3. Mis-predictions are the deliverable, not embarrassments — they mark exactly where your mental model of chunking is wrong.

## Exercises

### E1 — The 1-byte insert

Before the first run, predict in writing: after inserting **one byte** at offset 1,024, what percentage of the file re-uploads under **fixed** chunking, and what percentage under **CDC**? (Hint from the lesson: fixed boundaries are absolute positions; CDC boundaries are functions of the trailing 48 bytes of content.) Run and compare. If your fixed prediction was under 90%, re-read lesson section 5 — the insert-shift problem is the single most-tested fact in this design.

### E2 — Move the insert

Set `INSERT_POS = FILE_SIZE - 4096` (near the end). Predict both re-upload percentages before re-running. Fixed chunking's damage is *positional* — everything downstream of the insert — so what happens when almost nothing is downstream? Then try `INSERT_SIZE = 8192`: does the size of the insert change CDC's cost much? Why not?

### E3 — The block-size dial

Set `FIXED_BLOCK = 1024` and predict: Experiment 2's fixed re-upload %, and Experiment 1's metadata bytes. Smaller blocks mean finer deltas but more hashes to store and more per-block round-trips — this is the metadata-vs-bandwidth trade-off from lesson section 3, and it is why Dropbox picked 4 MB rather than 4 KB. Restore to `8 * 1024` after.

### E4 — Divergence and dedup

In Experiment 4, fixed chunking currently dedups *better* than CDC (in-place rewrites, no shift). Predict what happens to both dedup percentages if you set `SIMILAR_SPANS = 8`, then re-run. Finally, edit `experiment_4_dedup` mentally (or actually): if file B's spans were *inserted* instead of overwritten in place, which scheme's dedup % would collapse? You already have the evidence from E1.

## Deliverable

Your prediction-vs-observed notes for E1–E4 — one line each: *predicted → observed → why the gap*. Bring them to the next session; they seed a learning record. The E1 pair of numbers (fixed vs CDC re-upload after one byte) is the one to memorize: it is the whole argument for content-defined chunking, compressed into two percentages.
