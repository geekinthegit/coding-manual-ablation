"""Check manual/chapter1.txt against the component inventory in
decisions/03-1-manual-component-definition.md (3.1.3).

File format assumption (transcription rule B): one segmentation unit per
line -- section heading, move heading, paragraph, arrow (U+27A2) item,
square (U+25A0) item, numbered sub-item -- with speaker lines (S:/T:)
inside an example on separate lines. No blank lines.

Every check prints PASS or FAIL with observed vs expected values.
Reference counts (items not subject to replacement) are printed as INFO
and do not affect the exit status. Exit status is 1 if any check FAILs.

Usage (from the repository root):
    python scripts/check_manual.py
"""

import re
import sys

from paths import MANUAL_FILE

ARROW = "\u27a2"  # ➢
SQUARE = "\u25a0"  # ■

SECTION_HEADINGS = [
    "1.1 Introduction to Teacher Talk Moves",
    "1.2 Categories and Talk Moves",
    "1.3 Accountability to the Learning Community",
    "1.4 Accountability to Content Knowledge",
    "1.5 Accountability to Rigorous Thinking",
    "1.6 What is not coded",
]

# Move headings as they appear in the manual body (not the 1.2 list, not
# tags.py), in document order. Expected square-item counts per 3.1.3.
MOVES = [
    ("Keeping Everyone Together", 19),
    ("Getting Students to Relate to Another\u2019s Ideas", 10),
    ("Restating", 3),
    ("Pressing for Accuracy", 13),
    ("Revoicing", 5),
    ("Pressing for Reasoning", 11),
]

EXPECTED = {
    "square_total": 61,
    "exclusion_rules": 11,
    "examples_label_lines": 2,
    "restating_tags": 3,
    "revoicing_tags": 5,
    "background_sentences": 3,
}

# Reference counts (3.1.3 types b and c; not replaced in any condition).
REFERENCE = {
    "1.1 arrow items (type b)": 1,
    "1.1 numbered sub-items (type b)": 2,
    "1.2 square items (type c)": 3,
    "1.2 move-list arrow items (type c)": 6,
}

results = []


def check(name, observed, expected):
    ok = observed == expected
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}: observed={observed!r} expected={expected!r}")


def info(name, observed, reference=None):
    tail = "" if reference is None else f" reference={reference!r}"
    print(f"INFO  {name}: observed={observed!r}{tail}")


def main():
    text = MANUAL_FILE.read_text(encoding="utf-8")
    lines = text.splitlines()
    print(f"File: {MANUAL_FILE}")
    print(f"Lines: {len(lines)}\n")

    check("no blank lines", sum(1 for l in lines if l.strip() == ""), 0)

    # --- Section and move headings -------------------------------------
    for h in SECTION_HEADINGS:
        check(f"section heading present exactly once: {h!r}", lines.count(h), 1)
    for name, _ in MOVES:
        check(f"move heading present exactly once: {name!r}", lines.count(name), 1)
    if not all(results):
        print("\nHeading checks failed; remaining checks depend on them. Stopping.")
        return 1

    sec = {h: lines.index(h) for h in SECTION_HEADINGS}
    move_idx = [lines.index(name) for name, _ in MOVES]
    check("move headings in document order", move_idx == sorted(move_idx), True)
    check("all move headings inside 1.3-1.5",
          all(sec[SECTION_HEADINGS[2]] < i < sec[SECTION_HEADINGS[5]] for i in move_idx), True)

    # --- Definition paragraphs and square items per move -----------------
    bounds = move_idx + [sec[SECTION_HEADINGS[5]]]
    square_total = 0
    for (name, expected_sq), start, end in zip(MOVES, bounds, bounds[1:]):
        body = lines[start + 1:end]
        first = body[0] if body else ""
        is_paragraph = bool(first) and first[0] not in (ARROW, SQUARE) and not first.startswith(("S:", "T:"))
        check(f"definition paragraph directly under {name!r}", is_paragraph, True)
        n_sq = sum(l.startswith(SQUARE) for l in body)
        square_total += n_sq
        check(f"square items under {name!r}", n_sq, expected_sq)
    check("square items total in 1.3-1.5", square_total, EXPECTED["square_total"])

    # --- Exclusion rules (1.6) ------------------------------------------
    sec16 = lines[sec[SECTION_HEADINGS[5]] + 1:]
    check("arrow items in 1.6 (exclusion rules)",
          sum(l.startswith(ARROW) for l in sec16), EXPECTED["exclusion_rules"])
    check("no square items in 1.6", sum(l.startswith(SQUARE) for l in sec16), 0)
    check("all non-heading lines in 1.6 are arrow items",
          all(l.startswith(ARROW) for l in sec16), True)
    # Inline quoted examples in 1.6 must sit inside arrow lines, not on their own.
    quoted = [l for l in sec16 if "\u201c" in l]
    check("1.6 lines containing inline quoted examples", len(quoted), 3)
    check("all inline quoted examples in 1.6 are inside arrow items",
          all(l.startswith(ARROW) for l in quoted), True)
    info("1.6 quoted strings total", sum(l.count("\u201c") for l in sec16))

    # --- Example labels and speaker pairs --------------------------------
    check("'\u27a2 Examples:' lines", lines.count(f"{ARROW} Examples:"), EXPECTED["examples_label_lines"])
    check("'(Restating)' occurrences", text.count("(Restating)"), EXPECTED["restating_tags"])
    check("'(Revoicing)' occurrences", text.count("(Revoicing)"), EXPECTED["revoicing_tags"])

    pairs = 0
    for i, l in enumerate(lines[:-1]):
        nxt = lines[i + 1]
        if l.startswith(f"{SQUARE} S:") and nxt.startswith("T:"):
            pairs += 1
        elif l.startswith(f"{SQUARE} T:") and nxt.startswith("S:"):
            pairs += 1
    # 3.1.3 note g estimates 9 (Restating 3 + Revoicing 5 + call-and-response 1).
    check("S:/T: speaker pairs", pairs, 9)
    stray = [l for l in lines if l.startswith(("S:", "T:"))
             and not lines[lines.index(l) - 1].startswith(SQUARE)]
    check("every bare S:/T: line follows a square item line", len(stray), 0)

    # --- Background paragraph (1.1 first paragraph) ----------------------
    bg = lines[sec[SECTION_HEADINGS[0]] + 1]
    check("1.1 first line is a paragraph (not a marked item)",
          bg[0] not in (ARROW, SQUARE), True)
    n_sent = len(re.findall(r"[.!?](?=\s|$)", bg))
    check("background paragraph sentence count", n_sent, EXPECTED["background_sentences"])

    # --- Reference counts (types b, c): not part of PASS/FAIL ------------
    s11 = lines[sec[SECTION_HEADINGS[0]] + 1:sec[SECTION_HEADINGS[1]]]
    s12 = lines[sec[SECTION_HEADINGS[1]] + 1:sec[SECTION_HEADINGS[2]]]
    print()
    info("1.1 arrow items (type b)", sum(l.startswith(ARROW) for l in s11), REFERENCE["1.1 arrow items (type b)"])
    info("1.1 numbered sub-items (type b)", sum(bool(re.match(r"\d\. ", l)) for l in s11),
         REFERENCE["1.1 numbered sub-items (type b)"])
    info("1.2 square items (type c)", sum(l.startswith(SQUARE) for l in s12), REFERENCE["1.2 square items (type c)"])
    arrows12 = [l for l in s12 if l.startswith(ARROW)]
    info("1.2 arrow lines total (lead paragraph is arrow-marked in the source)", len(arrows12))
    info("1.2 move-list arrow items (type c)",
         sum(l.startswith(f"{ARROW} Teacher Talk Move") for l in arrows12),
         REFERENCE["1.2 move-list arrow items (type c)"])
    info("arrow sub-heading lines in 1.3-1.5 (excluding '\u27a2 Examples:')",
         sum(l.startswith(ARROW) and l != f"{ARROW} Examples:"
             for l in lines[sec[SECTION_HEADINGS[2]]:sec[SECTION_HEADINGS[5]]]))
    info("arrow lines in whole file", sum(l.startswith(ARROW) for l in lines))
    info("square lines in whole file", sum(l.startswith(SQUARE) for l in lines))

    n_fail = results.count(False)
    print(f"\nRESULT: {len(results) - n_fail} PASS, {n_fail} FAIL")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
