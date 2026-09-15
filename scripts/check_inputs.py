"""Verify prompts produced by build_inputs.py for a list of target source_ids.

Checks, per source_id and per condition
---------------------------------------
1. Neither input CSV carries a label column (checked once).
2. The Context block has exactly one [TARGET] line, it is a teacher line,
   and it sits at the expected position within the window.
3. Window size equals min(7, rows available before) + 1 + min(7, rows
   available after), where availability is computed here independently from
   rows_all.csv (same Transcript, within +/-7 of the target).
4. Every context line starts with "T:" or "S:" (after the target marker).
5. No gold leaks: the task instruction and the Context block contain no
   "Tag"/"StudentTag", no "Tag <number>" pattern, no category name, and no
   "nan"/"[MISSING]" stand-in for empty text. Category names must appear
   exactly once each in the output instruction. The manual section is not
   scanned for category names because the real manual defines them.
6. The Context block is byte-identical across all conditions.
7. build_prompt() equals the blank-line join of prompt_parts().

Usage
-----
    python scripts/check_inputs.py 123 456 789
    python scripts/check_inputs.py --ids-file path/to/file.csv   # column source_id

The second form is intended for the full-sample check before the main run.
"""

import argparse
import re

import pandas as pd

from build_inputs import (
    CATEGORY_NAMES,
    CONDITIONS,
    CONTEXT_HEADER,
    CONTEXT_RADIUS,
    FORBIDDEN_COLUMNS,
    FRAME_FILE,
    ROWS_ALL_FILE,
    TARGET_MARKER,
    build_prompt,
    get_tables,
    prompt_parts,
)

GOLD_PATTERNS = [
    re.compile(r"StudentTag"),
    re.compile(r"\bTag\b"),
    re.compile(r"\bTag\s*[:=]?\s*\d"),
    re.compile(r"\[MISSING\]"),
    re.compile(r"^(\[TARGET\] )?[TS]:\s*nan\s*$", re.MULTILINE),
]


def parse_ids(args: argparse.Namespace) -> list[int]:
    ids = [int(x) for x in args.source_ids]
    if args.ids_file:
        table = pd.read_csv(args.ids_file, keep_default_na=False, na_values=[""])
        ids += [int(x) for x in table["source_id"]]
    assert ids, "no source_id given"
    return ids


def available_rows(source_id: int, rows_all: pd.DataFrame) -> tuple[int, int]:
    """Count same-Transcript rows within +/-7 of the target, before and after."""
    transcript = rows_all.at[source_id, "Transcript"]
    lo = max(0, source_id - CONTEXT_RADIUS)
    hi = min(len(rows_all) - 1, source_id + CONTEXT_RADIUS)
    same = rows_all.loc[lo:hi, "Transcript"] == transcript
    before = int(same.loc[lo:source_id - 1].sum()) if source_id > lo else 0
    after = int(same.loc[source_id + 1:hi].sum()) if source_id < hi else 0
    return before, after


def scan_gold(text: str, section: str, problems: list[str]) -> None:
    for pat in GOLD_PATTERNS:
        if pat.search(text):
            problems.append(f"{section}: gold-like pattern {pat.pattern!r}")
    for name in CATEGORY_NAMES:
        if name in text:
            problems.append(f"{section}: category name {name!r}")


def check_one(source_id: int, rows_all: pd.DataFrame) -> list[str]:
    problems: list[str] = []
    contexts = {}
    for condition in CONDITIONS:
        parts = prompt_parts(source_id, condition, rows_all)
        contexts[condition] = parts["context"]
        if build_prompt(source_id, condition, rows_all) != "\n\n".join(parts.values()):
            problems.append(f"{condition}: build_prompt != joined parts")
        scan_gold(parts["task"], f"{condition}/task", problems)
        for name in CATEGORY_NAMES:
            if parts["output"].count(name) != 1:
                problems.append(f"{condition}/output: category {name!r} count != 1")

    if len({c.encode() for c in contexts.values()}) != 1:
        problems.append("Context block differs across conditions")

    context = contexts["baseline"]
    lines = context.split("\n")
    if lines[0] != CONTEXT_HEADER:
        problems.append(f"missing header line {CONTEXT_HEADER!r}")
    body = lines[1:]
    scan_gold(context, "context", problems)

    target_idx = [i for i, line in enumerate(body) if line.startswith(TARGET_MARKER)]
    if context.count("[TARGET]") != 1 or len(target_idx) != 1:
        problems.append(f"[TARGET] count = {context.count('[TARGET]')}")
    else:
        target_line = body[target_idx[0]]
        if not target_line.startswith(TARGET_MARKER + "T:"):
            problems.append("target line is not a teacher line")
        expected_text = str(rows_all.at[source_id, "Sentence"])
        if target_line != f"{TARGET_MARKER}T: {expected_text}":
            problems.append("target line text != rows_all Sentence")

    before, after = available_rows(source_id, rows_all)
    expected_n = min(CONTEXT_RADIUS, before) + 1 + min(CONTEXT_RADIUS, after)
    if len(body) != expected_n:
        problems.append(f"window size {len(body)} != expected {expected_n}")
    if len(target_idx) == 1 and target_idx[0] != min(CONTEXT_RADIUS, before):
        problems.append(f"target position {target_idx[0]} != expected {min(CONTEXT_RADIUS, before)}")

    for line in body:
        stripped = line[len(TARGET_MARKER):] if line.startswith(TARGET_MARKER) else line
        if not (stripped.startswith("T:") or stripped.startswith("S:")):
            problems.append(f"line without speaker marker: {line!r}")
    return problems


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_ids", nargs="*")
    parser.add_argument("--ids-file")
    args = parser.parse_args()
    ids = parse_ids(args)

    frame, rows_all = get_tables()  # load_tables() already asserts row agreement
    for name, table in (("frame.csv", frame), ("rows_all.csv", rows_all)):
        assert not FORBIDDEN_COLUMNS & set(table.columns), f"label column in {name}"
    print(f"Input files: {FRAME_FILE.name}, {ROWS_ALL_FILE.name}; no label columns.")

    eligible = set(int(x) for x in frame.loc[frame["eligible"], "source_id"])
    all_pass = True
    for sid in ids:
        if sid not in eligible:
            print(f"source_id {sid} | FAIL | not an eligible target")
            all_pass = False
            continue
        problems = check_one(sid, rows_all)
        status = "PASS" if not problems else "FAIL"
        all_pass &= not problems
        print(f"source_id {sid} | {status}" + ("" if not problems else " | " + "; ".join(problems)))

    assert all_pass, "input checks failed"
    print(f"All checks passed for {len(ids)} target(s) x {len(CONDITIONS)} conditions.")


if __name__ == "__main__":
    main()
