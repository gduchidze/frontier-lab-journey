# Lab 0009 — Design Rep

Companion to [Lesson 0009](../../lessons/0009-interview-os.html). Every lab so far verified a claim about *systems*; this one verifies a claim about *you* — that you can execute the 4-step framework under a clock. Rule of the lab: **speak aloud, type only bullets.** The interview is a spoken exam; typing full sentences trains the wrong muscle.

```bash
python3 design_rep.py          # the real thing: timed, scored, saved
python3 design_rep.py --demo   # preview problem, structure, rubric (no clock)
```

The problem: *design a health-check/heartbeat service that monitors 100,000 servers and alerts within 30 seconds of a server going silent.* The harness walks Steps 1–4 with budgets of 5/5/15/20 minutes. Each step shows its prompts, then collects bullet notes; pressing Enter on an empty line ends the step and prints your elapsed time against the budget. At the end you score yourself on a 12-dimension rubric (0–2 each) and everything — notes, per-step times, scores — is appended to `rep-notes.txt` in this directory.

## Protocol

1. Alone in a room, out loud, no pausing. Treat the terminal as the whiteboard margin.
2. Do NOT read the rubric mid-rep. You saw it in `--demo`; internalizing it is the training.
3. Score harshly. `0 = missed`, `1 = vague`, `2 = crisp`. An inflated 22/24 teaches nothing; an honest 13/24 tells you exactly what to drill.

## Exercises

### E1 — Preview
Run `--demo`. Before the real rep, predict your weakest three rubric dimensions in writing. After the rep, compare — mis-predicted weaknesses are the finding.

### E2 — The first rep
Full timed run. Expect to blow the Step 3 budget; almost everyone does on rep one. Do not restart mid-rep — running out of time IS the data.

### E3 — The number audit
Open `rep-notes.txt`. For every number in your Step 2 notes, find the Step 3/4 note that used it. Orphan numbers are the "computed but never used" anti-pattern from the lesson — count yours.

### E4 — Second rep, new problem
Re-run, but substitute your own prompt by editing `PROBLEM` at the top of `design_rep.py` (try: "design a URL shortener handling 100M new links/month"). Compare rubric totals across the two entries in `rep-notes.txt` — the delta, dimension by dimension, is your drill list for Phase 2.

## Deliverable

Your `rep-notes.txt` after at least one full rep (E2). Bring it to the next session — your teacher critiques the scores and the orphan-number count, not the design itself. A 13/24 with honest notes beats a 22/24 with generous ones.
