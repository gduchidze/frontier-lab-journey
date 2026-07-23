"""Lab 0022 — Chunk and Sync.

Four experiments that turn Lesson 0022's chunking claims into things
you've seen with your own eyes. Run:  python3 sync_lab.py

A synthetic "file" (random bytes, seeded → identical every run) is
chunked two ways:

  fixed  — fixed-size blocks (Dropbox's real choice, scaled down from
           4 MB to 8 KB so the run takes milliseconds)
  cdc    — content-defined chunking: a Rabin-lite polynomial rolling
           hash over the last WINDOW bytes; a chunk boundary is cut
           wherever (hash & MASK) == MASK, so boundaries are a pure
           function of local CONTENT, not of position.

Each block is named by its SHA-256 hash — content addressing. A block
whose hash the server has already seen costs nothing to "upload".
We then edit the file and measure which blocks change under each
scheme. The star of the show is Experiment 3: a ONE-BYTE insert near
the start of the file.

Then do the exercises in README.md — they all involve editing the
CONFIG block below and predicting the output BEFORE re-running.
"""

from __future__ import annotations

import hashlib
import random

# ---------------------------------------------------------------- CONFIG
# The exercises in README.md ask you to change these and predict results.
SEED = 22
FILE_SIZE = 256 * 1024      # synthetic file: 256 KB (stands in for ~1 GB)
FIXED_BLOCK = 8 * 1024      # fixed-size block (stands in for Dropbox's 4 MB)
CDC_MIN = 2 * 1024          # CDC: never cut a chunk smaller than this
CDC_MAX = 32 * 1024         # CDC: force a cut at this size
CDC_MASK_BITS = 13          # boundary prob 1/2^13 per byte → ~8 KB avg chunk
WINDOW = 48                 # rolling-hash window (bytes of context per boundary)
MODIFY_SPAN = 4 * 1024      # Experiment 2: bytes overwritten mid-file
INSERT_POS = 1024           # Experiment 3: where the insert lands
INSERT_SIZE = 1             # Experiment 3: how many bytes get inserted
SIMILAR_SPANS = 3           # Experiment 4: rewritten 8 KB spans in file B
SIMILAR_APPEND = 16 * 1024  # Experiment 4: bytes appended to file B
# -----------------------------------------------------------------------

BASE = 257
M64 = (1 << 64) - 1
MASK = (1 << CDC_MASK_BITS) - 1
POW = pow(BASE, WINDOW - 1, 1 << 64)


def block_id(chunk: bytes) -> str:
    """Content address: the block IS its hash. Equal content, equal ID."""
    return hashlib.sha256(chunk).hexdigest()


def fixed_chunks(data: bytes) -> list[bytes]:
    """Fixed-size chunking: cut every FIXED_BLOCK bytes from position 0."""
    return [data[i:i + FIXED_BLOCK] for i in range(0, len(data), FIXED_BLOCK)]


def cdc_chunks(data: bytes) -> list[bytes]:
    """Content-defined chunking with a polynomial rolling hash.

    The hash covers only the trailing WINDOW bytes, so whether a byte
    position is a boundary depends on the 48 bytes before it — nothing
    else. Insert bytes upstream and downstream boundaries re-appear at
    the same CONTENT, just shifted in position: the block hashes after
    the edit region are unchanged.
    """
    chunks: list[bytes] = []
    start = 0
    h = 0
    for i, b in enumerate(data):
        if i - start < WINDOW:          # window still filling for this chunk
            h = (h * BASE + b) & M64
        else:                           # slide: drop oldest byte, add new one
            h = ((h - data[i - WINDOW] * POW) * BASE + b) & M64
        size = i - start + 1
        if size >= CDC_MAX or (size >= CDC_MIN and (h & MASK) == MASK):
            chunks.append(data[start:i + 1])
            start, h = i + 1, 0
    if start < len(data):
        chunks.append(data[start:])
    return chunks


def upload_cost(old: list[bytes], new: list[bytes]) -> tuple[int, int]:
    """Blocks and bytes of `new` whose hash the server hasn't seen in `old`."""
    known = {block_id(c) for c in old}
    fresh = [c for c in new if block_id(c) not in known]
    return len(fresh), sum(len(c) for c in fresh)


def row(scheme: str, old: list[bytes], new: list[bytes], total: int) -> None:
    n_blocks, n_bytes = upload_cost(old, new)
    print(f"  {scheme:<7}  {len(new):>7}  {n_blocks:>10}  "
          f"{n_bytes:>12,}  {n_bytes / total:>9.1%}")


def header() -> None:
    print(f"  {'scheme':<7}  {'blocks':>7}  {'re-upload':>10}  "
          f"{'bytes up':>12}  {'% of file':>9}")


def experiment_1_baseline(data: bytes) -> tuple[list[bytes], list[bytes]]:
    print("=" * 74)
    print("EXPERIMENT 1 — baseline: chunk the same file both ways")
    print("=" * 74)
    fx, cd = fixed_chunks(data), cdc_chunks(data)
    print(f"  file: {len(data):,} bytes (seed={SEED})\n")
    print(f"  {'scheme':<7}  {'blocks':>7}  {'avg block':>10}  {'metadata':>10}")
    for name, chunks in (("fixed", fx), ("cdc", cd)):
        avg = len(data) / len(chunks)
        meta = len(chunks) * 32          # one 32-byte SHA-256 per block
        print(f"  {name:<7}  {len(chunks):>7}  {avg:>8,.0f} B  {meta:>8,} B")
    print("\n  -> Similar block counts, so similar metadata cost. The file's")
    print("     manifest is just this ordered list of 32-byte hashes — that")
    print("     list lives in the metadata DB; the blocks live in blob storage.\n")
    return fx, cd


def experiment_2_modify(data: bytes, fx: list[bytes], cd: list[bytes]) -> None:
    print("=" * 74)
    print(f"EXPERIMENT 2 — overwrite {MODIFY_SPAN:,} bytes mid-file (no size change)")
    print("=" * 74)
    rng = random.Random(SEED + 1)
    mid = len(data) // 2
    edited = data[:mid] + rng.randbytes(MODIFY_SPAN) + data[mid + MODIFY_SPAN:]
    print(f"  edit at offset {mid:,}; file size unchanged\n")
    header()
    row("fixed", fx, fixed_chunks(edited), len(edited))
    row("cdc", cd, cdc_chunks(edited), len(edited))
    print("\n  -> Both schemes shine: positions didn't shift, so only the")
    print("     blocks actually touched by the edit get new hashes. In-place")
    print("     edits are the case fixed chunking was designed for.\n")


def experiment_3_insert(data: bytes, fx: list[bytes], cd: list[bytes]) -> None:
    print("=" * 74)
    print(f"EXPERIMENT 3 — insert {INSERT_SIZE} byte(s) at offset {INSERT_POS:,}")
    print("=" * 74)
    rng = random.Random(SEED + 2)
    edited = data[:INSERT_POS] + rng.randbytes(INSERT_SIZE) + data[INSERT_POS:]
    print(f"  file grew by {INSERT_SIZE} byte(s): "
          f"{len(data):,} → {len(edited):,}\n")
    header()
    row("fixed", fx, fixed_chunks(edited), len(edited))
    row("cdc", cd, cdc_chunks(edited), len(edited))
    print("\n  -> The insert-shift catastrophe: fixed chunking cuts at absolute")
    print("     positions, so one inserted byte shifts EVERY downstream boundary")
    print("     by one — every block after the insert re-hashes and re-uploads.")
    print("     CDC boundaries are functions of content, so they re-align right")
    print("     after the edit and the rest of the file dedups against itself.\n")


def experiment_4_dedup(data: bytes) -> None:
    print("=" * 74)
    print(f"EXPERIMENT 4 — cross-file dedup: file B = A with {SIMILAR_SPANS} "
          f"rewritten spans + {SIMILAR_APPEND // 1024} KB appended")
    print("=" * 74)
    rng = random.Random(SEED + 3)
    b = bytearray(data)
    span = 8 * 1024
    stride = len(data) // (SIMILAR_SPANS + 1)
    for k in range(1, SIMILAR_SPANS + 1):       # rewrite spans in place
        pos = k * stride
        b[pos:pos + span] = rng.randbytes(span)
    file_b = bytes(b) + rng.randbytes(SIMILAR_APPEND)
    print(f"  file A: {len(data):,} B   file B: {len(file_b):,} B "
          f"(two users, similar content)\n")
    print(f"  {'scheme':<7}  {'B blocks':>8}  {'shared':>7}  {'new bytes':>12}  "
          f"{'dedup %':>8}")
    for name, fn in (("fixed", fixed_chunks), ("cdc", cdc_chunks)):
        a_chunks, b_chunks = fn(data), fn(file_b)
        n_new, bytes_new = upload_cost(a_chunks, b_chunks)
        shared = len(b_chunks) - n_new
        dedup = 1 - bytes_new / len(file_b)
        print(f"  {name:<7}  {len(b_chunks):>8}  {shared:>7}  "
              f"{bytes_new:>12,}  {dedup:>8.1%}")
    print("\n  -> Content addressing makes dedup free: user B's client hashes")
    print("     locally, asks the server 'which of these do you have?', and")
    print("     only ships the rest. Note who wins HERE: the spans were")
    print("     rewritten in place (no shift), so fixed chunking dedups")
    print("     better — its damage stays inside neatly aligned blocks, while")
    print("     CDC's bigger, content-cut chunks bleed across the edits. CDC")
    print("     only earns its complexity when file sizes SHIFT (Experiment 3).\n")


def main() -> None:
    rng = random.Random(SEED)
    data = rng.randbytes(FILE_SIZE)
    print(f"(deterministic: seed={SEED}; every run prints identical numbers)\n")
    fx, cd = experiment_1_baseline(data)
    experiment_2_modify(data, fx, cd)
    experiment_3_insert(data, fx, cd)
    experiment_4_dedup(data)
    print("Done. Now do the README exercises: predict, edit CONFIG, re-run, "
          "compare.")


if __name__ == "__main__":
    main()
