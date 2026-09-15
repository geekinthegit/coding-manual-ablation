"""Replacement sites in manual/chapter1.txt and placeholder construction.

Shared by build_manifest.py, probe_symbols.py, build_conditions.py and
check_token_matching.py. No API calls; no human labels are read.

Site definition (Decision Log 3.1.7, 3.1.8, 3.2.2)
--------------------------------------------------
A site is one physical line of manual/chapter1.txt whose text is replaced
in one condition. The preserved prefix is the structural marker only
(U+25A0 or U+27A2, without the following space); the replaced span runs
from the character after the marker (the space) to the end of the line.
Lines without a marker (definition paragraphs, T:/S: continuation lines)
are replaced in full. The newline that ends the line is preserved
verbatim; for token accounting the measured span is the replaced text
PLUS that newline, so that a tokenizer which glues a newline to the last
character (e.g. ".\n" as one token) is handled consistently: the repeat
count is chosen so that "filler + newline" yields the same number of
tokens as "original text + newline".

Rationale for putting the space inside the replaced span: in o200k_base
a space attaches to the token that follows it, so a marker-only prefix is
where a token boundary can fall; the manifest records whether it does.

Conditions (letters follow 3.1.3):
    a  negative_control          1.1 first paragraph (1 site)
    e  definition_replacement    first paragraph under each move heading (6)
    g  example_replacement       square items in 1.3-1.5, S:/T: continuation
                                 lines, and the two '➢ Examples:' lines
                                 (63 items on 72 lines)
    h  exclusion_rule_replacement arrow items in 1.6 (11)

Placeholder construction rules (candidates; one is fixed in 3.2.2)
------------------------------------------------------------------
    A  contiguous repeat:      lead + symbol * n
    B  space-separated repeat: lead + symbol + (' ' + symbol) * (n - 1)
where lead is ' ' when the replaced span starts with a space (marker
lines) and '' otherwise. n is chosen per site so that the number of
tokens starting inside the span equals the original count when the whole
prompt is tokenised (search in fit_repeats()).
"""

import csv
from pathlib import Path

from build_inputs import MANUAL_HEADER, REPO_ROOT, prompt_parts

ARROW = "\u27a2"  # ➢
SQUARE = "\u25a0"  # ■
ENCODING_NAME = "o200k_base"
EXAMPLE_SOURCE_ID = 7  # fixed context example for token checks

MANUAL_DIR = REPO_ROOT / "manual"
DATA_DIR = REPO_ROOT / "data"
REPORTS_DIR = REPO_ROOT / "reports"
BASELINE_FILE = MANUAL_DIR / "chapter1.txt"
MANIFEST_FILE = DATA_DIR / "replacement_manifest.csv"

CONDITION_LETTER = {
    "negative_control": "a",
    "definition_replacement": "e",
    "example_replacement": "g",
    "exclusion_rule_replacement": "h",
}
LETTER_CONDITION = {v: k for k, v in CONDITION_LETTER.items()}
CONDITION_FILES = {
    "baseline": BASELINE_FILE,
    **{c: MANUAL_DIR / f"chapter1_{c}.txt" for c in CONDITION_LETTER},
}

# Expected site counts per 3.1.3 (items) and per physical line.
EXPECTED_ITEMS = {"a": 1, "e": 6, "g": 63, "h": 11}
EXPECTED_LINES = {"a": 1, "e": 6, "g": 72, "h": 11}

SECTION_HEADINGS = [
    "1.1 Introduction to Teacher Talk Moves",
    "1.2 Categories and Talk Moves",
    "1.3 Accountability to the Learning Community",
    "1.4 Accountability to Content Knowledge",
    "1.5 Accountability to Rigorous Thinking",
    "1.6 What is not coded",
]
MOVE_HEADINGS = [
    "Keeping Everyone Together",
    "Getting Students to Relate to Another\u2019s Ideas",
    "Restating",
    "Pressing for Accuracy",
    "Revoicing",
    "Pressing for Reasoning",
]

MANIFEST_COLUMNS = [
    "site_id", "line_no", "condition", "item_id", "unit_type",
    "preserved_prefix", "replaced_text", "original_token_count",
    "boundary_start_clean", "newline_separate_token",
]


def read_lines(path: Path = BASELINE_FILE) -> list[str]:
    """Return the manual as a list of lines (no trailing newlines)."""
    text = path.read_text(encoding="utf-8")
    assert text.endswith("\n"), f"{path} must end with a newline"
    lines = text[:-1].split("\n")
    assert all(l.strip() for l in lines), "blank line in manual"
    return lines


def split_site(line: str) -> tuple[str, str]:
    """Return (preserved_prefix, replaced_text) for one site line."""
    if line[0] in (SQUARE, ARROW):
        return line[0], line[1:]
    return "", line


def parse_sites(lines: list[str]) -> list[dict]:
    """Return the replacement sites of the baseline manual, in file order."""
    sec = {h: lines.index(h) for h in SECTION_HEADINGS}
    moves = [lines.index(m) for m in MOVE_HEADINGS]
    i13, i16 = sec[SECTION_HEADINGS[2]], sec[SECTION_HEADINGS[5]]

    sites: list[dict] = []
    item_counter = {k: 0 for k in EXPECTED_ITEMS}

    def add(idx: int, cond: str, unit_type: str, new_item: bool) -> None:
        if new_item:
            item_counter[cond] += 1
        prefix, replaced = split_site(lines[idx])
        sites.append({
            "site_id": len(sites) + 1,
            "line_no": idx + 1,
            "condition": cond,
            "item_id": f"{cond}{item_counter[cond]:02d}",
            "unit_type": unit_type,
            "preserved_prefix": prefix,
            "replaced_text": replaced,
        })

    # a: 1.1 first paragraph
    add(sec[SECTION_HEADINGS[0]] + 1, "a", "paragraph", True)
    # e: definition paragraph under each move heading
    for m in moves:
        add(m + 1, "e", "paragraph", True)
    # g: examples in 1.3-1.5
    for idx in range(i13 + 1, i16):
        l = lines[idx]
        if l == f"{ARROW} Examples:":
            add(idx, "g", "examples_label", True)
        elif l.startswith(SQUARE):
            add(idx, "g", "square_item", True)
        elif l.startswith(("S:", "T:")):
            assert lines[idx - 1].startswith(SQUARE), f"line {idx + 1}: speaker line not after a square item"
            add(idx, "g", "speaker_line", False)
    # h: exclusion rules in 1.6
    for idx in range(i16 + 1, len(lines)):
        if lines[idx].startswith(ARROW):
            add(idx, "h", "arrow_item", True)

    sites.sort(key=lambda s: s["line_no"])
    for n, s in enumerate(sites, start=1):
        s["site_id"] = n
    assert item_counter == EXPECTED_ITEMS, item_counter
    per_line = {k: sum(s["condition"] == k for s in sites) for k in EXPECTED_LINES}
    assert per_line == EXPECTED_LINES, per_line
    assert len({s["line_no"] for s in sites}) == len(sites), "duplicate site line"
    return sites


def make_filler(replaced_text: str, symbol: str, rule: str, n: int) -> str:
    """Return the placeholder text for one site under rule A or B."""
    assert n >= 1, n
    lead = " " if replaced_text.startswith(" ") else ""
    if rule == "A":
        return lead + symbol * n
    if rule == "B":
        return lead + symbol + (" " + symbol) * (n - 1)
    raise ValueError(rule)


def build_manual(lines: list[str], sites: list[dict], condition_letter: str | None,
                 fillers: dict[int, str] | None = None) -> tuple[str, dict[int, tuple[int, int]]]:
    """Assemble the manual text for one condition and return site spans.

    Returns (manual_text, spans) where spans maps site_id -> (start, end)
    character offsets of the measured span within manual_text: from the
    first replaced character up to and including the line's newline (end
    exclusive). Sites of other conditions are returned
    too, with their original spans. With condition_letter None the
    baseline is returned unchanged.
    """
    by_line = {s["line_no"]: s for s in sites}
    out: list[str] = []
    spans: dict[int, tuple[int, int]] = {}
    pos = 0
    for idx, line in enumerate(lines, start=1):
        s = by_line.get(idx)
        if s is None:
            text = line
        else:
            body = s["replaced_text"]
            if condition_letter is not None and s["condition"] == condition_letter:
                body = fillers[s["site_id"]]
            text = s["preserved_prefix"] + body
            start = pos + len(s["preserved_prefix"])
            spans[s["site_id"]] = (start, start + len(body) + 1)  # + newline
        out.append(text)
        pos += len(text) + 1  # newline
    return "\n".join(out) + "\n", spans


def assemble_prompt(manual_text: str, source_id: int = EXAMPLE_SOURCE_ID) -> tuple[str, int]:
    """Return (full prompt text, offset of manual_text inside it).

    Uses build_inputs.prompt_parts for the baseline condition and swaps
    the manual section, so task/context/output are exactly what the
    experiment sends. manual_text's trailing newline is stripped as in
    build_inputs.load_manual.
    """
    parts = prompt_parts(source_id, "baseline")
    manual_body = manual_text.rstrip("\n")
    parts["manual"] = MANUAL_HEADER + "\n" + manual_body
    full = "\n\n".join(parts.values())
    offset = len(parts["task"]) + 2 + len(MANUAL_HEADER) + 1
    assert full[offset:offset + len(manual_body)] == manual_body
    return full, offset


def token_starts(enc, text: str) -> list[int]:
    """Tokenise text and return the start character offset of every token."""
    tokens = enc.encode(text, disallowed_special=())
    decoded, offsets = enc.decode_with_offsets(tokens)
    assert decoded == text, "decode_with_offsets round trip failed"
    return offsets


def measure(enc, manual_text: str, spans: dict[int, tuple[int, int]],
            source_id: int = EXAMPLE_SOURCE_ID) -> dict:
    """Tokenise the full prompt and measure every site span.

    Returns {"total": int, "sites": {site_id: {"count", "next_index",
    "start_clean", "newline_separate"}}}. count = tokens whose start offset
    lies in [start, end) (end = after the newline); next_index = index of
    the first token starting at or after end, i.e. the first preserved
    token of the next line; start_clean = a token starts exactly at start;
    newline_separate = a token starts exactly at the newline character
    (False means the newline is glued to the preceding token).
    """
    full, off = assemble_prompt(manual_text, source_id)
    starts = token_starts(enc, full)
    result = {"total": len(starts), "sites": {}}
    start_set = set(starts)
    for sid, (a, b) in spans.items():
        a += off
        b += off
        count = sum(1 for s in starts if a <= s < b)
        next_index = next((i for i, s in enumerate(starts) if s >= b), len(starts))
        result["sites"][sid] = {
            "count": count,
            "next_index": next_index,
            "start_clean": a in start_set,
            "newline_separate": (b - 1) in start_set,
        }
    return result


def fit_repeats(enc, lines: list[str], sites: list[dict], baseline: dict,
                condition_letter: str, symbol: str, rule: str,
                max_iter: int = 200, source_id: int = EXAMPLE_SOURCE_ID) -> dict:
    """Search per-site repeat counts n so that all three checks pass.

    All sites of the condition are replaced simultaneously (adjacent sites
    interact at token boundaries). Starting from n = original count, each
    iteration re-tokenises the full prompt and moves n of every mismatching
    site by +/-1. Returns {"ok": bool, "n": {site_id: n}, "iterations": int,
    "failures": [str]}. A site whose count oscillates or whose n would drop
    below 1 is reported as a failure.
    """
    cond_sites = [s for s in sites if s["condition"] == condition_letter]
    n = {s["site_id"]: baseline["sites"][s["site_id"]]["count"] for s in cond_sites}
    seen: dict[int, set[int]] = {sid: set() for sid in n}
    failures: list[str] = []
    for it in range(1, max_iter + 1):
        fillers = {s["site_id"]: make_filler(s["replaced_text"], symbol, rule, n[s["site_id"]])
                   for s in cond_sites}
        manual_text, spans = build_manual(lines, sites, condition_letter, fillers)
        m = measure(enc, manual_text, spans, source_id)
        bad = []
        for s in cond_sites:
            sid = s["site_id"]
            want = baseline["sites"][sid]
            got = m["sites"][sid]
            if got["count"] != want["count"] or got["next_index"] != want["next_index"]:
                bad.append((sid, want["count"], got["count"], want["next_index"], got["next_index"]))
        if not bad and m["total"] == baseline["total"]:
            return {"ok": True, "n": n, "iterations": it, "failures": [], "manual_text": manual_text}
        if not bad and m["total"] != baseline["total"]:
            failures.append(f"all sites match but total tokens differ: {m['total']} vs {baseline['total']}")
            break
        stuck = False
        for k, (sid, wc, gc, wn, gn) in enumerate(bad):
            if gc == wc and k > 0:
                # count already right; the next_index shift comes from an upstream
                # site (bad is in document order) -- do not move this site yet
                continue
            seen[sid].add(n[sid])
            if gc == wc:
                # first mismatching site with the right count: a boundary effect at
                # this site itself; try +1, then -1
                candidates = [n[sid] + 1, n[sid] - 1]
            else:
                # step proportional to the mismatch, using the current chars-per-token ratio;
                # fall back to +/-1 steps near the target so every n is eventually tried
                step = round((wc - gc) * n[sid] / max(gc, 1))
                if step == 0:
                    step = 1 if gc < wc else -1
                candidates = [n[sid] + step]
                if abs(step) > 1:
                    candidates += [n[sid] + (1 if step > 0 else -1)]
                else:
                    candidates += [n[sid] + 2 * step]
            new = next((c for c in candidates if c >= 1 and c not in seen[sid]), None)
            if new is None:
                failures.append(f"site {sid} (line {next(s['line_no'] for s in cond_sites if s['site_id']==sid)}): "
                                f"cannot reach count={wc} next={wn}; last n={n[sid]} gave count={gc} next={gn}; "
                                f"tried n={sorted(seen[sid])}")
                stuck = True
            else:
                n[sid] = new
        if stuck:
            break
    else:
        failures.append(f"no convergence after {max_iter} iterations; unresolved sites: "
                        + ", ".join(str(b[0]) for b in bad))
    return {"ok": False, "n": n, "iterations": it, "failures": failures, "manual_text": None}


def write_manifest(sites: list[dict], baseline: dict, path: Path = MANIFEST_FILE) -> None:
    """Write data/replacement_manifest.csv (git-ignored: contains manual text)."""
    path.parent.mkdir(exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MANIFEST_COLUMNS)
        w.writeheader()
        for s in sites:
            m = baseline["sites"][s["site_id"]]
            w.writerow({**{k: s[k] for k in MANIFEST_COLUMNS if k in s},
                        "original_token_count": m["count"],
                        "boundary_start_clean": m["start_clean"],
                        "newline_separate_token": m["newline_separate"]})


def read_manifest(path: Path = MANIFEST_FILE) -> list[dict]:
    """Read the manifest back with typed columns."""
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["site_id"] = int(r["site_id"])
        r["line_no"] = int(r["line_no"])
        r["original_token_count"] = int(r["original_token_count"])
        r["boundary_start_clean"] = r["boundary_start_clean"] == "True"
        r["newline_separate_token"] = r["newline_separate_token"] == "True"
    return rows
