"""Lab 0009 — Design Rep.

Your first full timed system-design rep, running the 4-step Interview OS
from Lesson 0009. Run:  python3 design_rep.py

Interactive mode walks all four steps against a real prompt, times each
step (the clock only reads when YOU end a step — no busy-waiting), then
scores you on a 12-dimension rubric and saves everything to rep-notes.txt.

Run  python3 design_rep.py --demo  to preview the problem, the step
structure, and the full rubric without starting the clock.

Rule of the lab: SPEAK your answers aloud. Type only bullet notes —
the terminal is your whiteboard margin, not your mouth.
"""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime

# ---------------------------------------------------------------- CONFIG
PROBLEM = (
    "Design a health-check/heartbeat service that monitors 100,000 servers\n"
    "and alerts within 30 seconds of a server going silent."
)

NOTES_FILENAME = "rep-notes.txt"
MAX_SCORE_PER_DIMENSION = 2
ON_TIME_SLACK_MIN = 2.0   # a step within budget + this slack still counts as on time
# -----------------------------------------------------------------------


@dataclass(frozen=True)
class Step:
    name: str
    budget_min: int
    prompts: tuple[str, ...]


STEPS: tuple[Step, ...] = (
    Step(
        name="Step 1 · Clarify",
        budget_min=5,
        prompts=(
            "Who consumes the alerts, and how many rules/users are there?",
            "Functional requirements: what MUST the system do? Write 3+.",
            "Non-functional requirements: detection SLO, availability, scale.",
            "What is explicitly OUT of scope? Say it, then note it.",
        ),
    ),
    Step(
        name="Step 2 · Estimate",
        budget_min=5,
        prompts=(
            "Heartbeats/sec at 100k servers (pick an interval; show the math).",
            "Storage per day if you keep every heartbeat. Powers of ten only.",
            "Bandwidth in and out. Does one box survive this? Say why not.",
            "Mark each number you will REUSE in steps 3-4 with an arrow.",
        ),
    ),
    Step(
        name="Step 3 · High-level design",
        budget_min=15,
        prompts=(
            "Boxes and arrows aloud: ingestion -> detection -> alerting.",
            "API sketch: 3-5 endpoints with verbs (POST /heartbeat, ...).",
            "Data model sketch: entities, keys, and which store holds each.",
            "Narrate at least one trade-off WHILE drawing ('...because...').",
        ),
    ),
    Step(
        name="Step 4 · Deep dive + scale",
        budget_min=20,
        prompts=(
            "Pick 1-2 components; apply the toolkit: replication, sharding,",
            "  caching, queues. Justify each with a Step-2 number.",
            "Name the bottleneck and one failure mode UNPROMPTED. Mitigate.",
            "Close: what metric pages a human? What would more time buy?",
        ),
    ),
)

RUBRIC: tuple[str, ...] = (
    "Functional requirements: 3+ named and written down",
    "Non-functional requirements: SLOs stated with numbers",
    "Out-of-scope list stated explicitly before designing",
    "Estimates computed: QPS, storage, bandwidth all present",
    "Estimates USED: at least one number justified a decision",
    "API sketched: 3-5 endpoints with verbs",
    "Data model sketched: entities, keys, chosen stores",
    "Trade-off stated with an explicit 'because'",
    "Bottleneck named unprompted",
    "Failure mode named unprompted, with a mitigation",
    "Close included monitoring and 'with more time...'",
    "Time discipline: every step within ~2 min of budget",
)

SCORE_GUIDE = "0 = missed entirely, 1 = partial/vague, 2 = done crisply"


def lab_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def print_problem() -> None:
    print("=" * 72)
    print("THE PROBLEM (read it aloud, twice)")
    print("=" * 72)
    print(PROBLEM)
    print()


def print_structure() -> None:
    print("=" * 72)
    print("THE 4-STEP STRUCTURE (Lesson 0009)")
    print("=" * 72)
    for step in STEPS:
        print(f"\n{step.name}  —  budget {step.budget_min} min")
        for prompt in step.prompts:
            print(f"    - {prompt}")
    total = sum(s.budget_min for s in STEPS)
    print(f"\nTotal budget: {total} min (the real round is ~50).")
    print()


def print_rubric() -> None:
    print("=" * 72)
    print(f"SELF-SCORING RUBRIC — 12 dimensions, {SCORE_GUIDE}")
    print("=" * 72)
    for i, dim in enumerate(RUBRIC, 1):
        print(f"  {i:>2}. {dim}")
    max_total = len(RUBRIC) * MAX_SCORE_PER_DIMENSION
    print(f"\nMax score: {max_total}. Bands: 0-11 raw rep, 12-17 getting there,")
    print("18-21 interview-ready shape, 22-24 suspiciously generous scoring.")
    print()


def run_demo() -> None:
    print_problem()
    print_structure()
    print_rubric()
    print("Demo over. When ready to sweat: python3 design_rep.py")


def collect_step_notes(step: Step) -> list[str]:
    """Read bullet notes until an empty line ends the step."""
    print("Type bullet notes (one per line). Press Enter on an empty line")
    print("to END the step and stop its clock.\n")
    notes: list[str] = []
    while True:
        line = input("  * ").strip()
        if not line:
            return notes
        notes.append(line)


def run_step(step: Step) -> tuple[list[str], float]:
    print("=" * 72)
    print(f"{step.name}  —  budget {step.budget_min} min. SPEAK ALOUD; type bullets.")
    print("=" * 72)
    for prompt in step.prompts:
        print(f"  - {prompt}")
    print()
    started = time.perf_counter()
    notes = collect_step_notes(step)
    elapsed_min = (time.perf_counter() - started) / 60.0
    over = elapsed_min - step.budget_min
    verdict = "ON BUDGET" if over <= ON_TIME_SLACK_MIN else f"OVER by {over:.1f} min"
    print(f"\n  -> elapsed {elapsed_min:.1f} min of {step.budget_min} min budget: {verdict}\n")
    return notes, elapsed_min


def read_score(index: int, dimension: str) -> int:
    while True:
        raw = input(f"  {index:>2}. {dimension}\n      score [0-2]: ").strip()
        if raw in ("0", "1", "2"):
            return int(raw)
        print("      Please enter 0, 1, or 2.")


def collect_scores() -> list[int]:
    print("=" * 72)
    print(f"SELF-SCORING — {SCORE_GUIDE}")
    print("Be harsh. Inflated scores only cheat the person retaking this rep.")
    print("=" * 72)
    return [read_score(i, dim) for i, dim in enumerate(RUBRIC, 1)]


def format_report(step_notes: list[tuple[Step, list[str], float]],
                  scores: list[int]) -> str:
    lines: list[str] = []
    lines.append("=" * 72)
    lines.append(f"DESIGN REP — {datetime.now().isoformat(timespec='seconds')}")
    lines.append("Problem: " + PROBLEM.replace("\n", " "))
    lines.append("=" * 72)
    for step, notes, elapsed_min in step_notes:
        lines.append(f"\n{step.name} (budget {step.budget_min} min, "
                     f"actual {elapsed_min:.1f} min)")
        if notes:
            lines.extend(f"  * {note}" for note in notes)
        else:
            lines.append("  (no notes typed)")
    total = sum(scores)
    max_total = len(RUBRIC) * MAX_SCORE_PER_DIMENSION
    lines.append(f"\nRUBRIC SCORES — total {total}/{max_total}")
    for dim, score in zip(RUBRIC, scores):
        lines.append(f"  [{score}] {dim}")
    lines.append("")
    return "\n".join(lines)


def save_report(report: str) -> str:
    path = os.path.join(lab_dir(), NOTES_FILENAME)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(report + "\n")
    return path


def run_interactive() -> None:
    print_problem()
    print("You are about to run all 4 steps against the clock.")
    print("Speak every answer aloud. The terminal takes bullet notes only.")
    input("\nPress Enter to start Step 1 (the clock starts immediately)... ")
    print()

    step_notes: list[tuple[Step, list[str], float]] = []
    for step in STEPS:
        notes, elapsed_min = run_step(step)
        step_notes.append((step, notes, elapsed_min))

    scores = collect_scores()
    report = format_report(step_notes, scores)
    path = save_report(report)

    total = sum(scores)
    max_total = len(RUBRIC) * MAX_SCORE_PER_DIMENSION
    print("\n" + report)
    print(f"Saved to {path}")
    print(f"\nFinal: {total}/{max_total}. Bring {NOTES_FILENAME} to the next "
          "session — low scores are the deliverable, not a problem.")


def main() -> None:
    if "--demo" in sys.argv[1:]:
        run_demo()
        return
    try:
        run_interactive()
    except (KeyboardInterrupt, EOFError):
        print("\n\nRep aborted — nothing saved. An unfinished rep still taught "
              "you where your clock breaks. Run it again when ready.")


if __name__ == "__main__":
    main()
