"""Build data/replacement_manifest.csv from manual/chapter1.txt.

For every replacement site (see manual_sites.py) the manifest records the
line number, condition, item id, preserved prefix, replaced text, and the
number of o200k_base tokens that start inside the replaced span when the
full baseline prompt (build_inputs.build_prompt, source_id 7) is
tokenised. Substrings are never tokenised on their own.

Outputs
    data/replacement_manifest.csv                (git-ignored; manual text)
    reports/replacement-manifest-summary-<date>.txt

Usage (repository root, conda base with tiktoken 0.14.0):
    python scripts/build_manifest.py
"""

import sys
from datetime import datetime

import tiktoken

from build_inputs import git_commit_hash
from manual_sites import (
    ENCODING_NAME, EXAMPLE_SOURCE_ID, EXPECTED_ITEMS, EXPECTED_LINES,
    LETTER_CONDITION, MANIFEST_FILE, REPORTS_DIR,
    build_manual, measure, parse_sites, read_lines, write_manifest,
)


def main() -> int:
    enc = tiktoken.get_encoding(ENCODING_NAME)
    lines = read_lines()
    sites = parse_sites(lines)
    manual_text, spans = build_manual(lines, sites, None)
    baseline = measure(enc, manual_text, spans, EXAMPLE_SOURCE_ID)
    write_manifest(sites, baseline)

    now = datetime.now().astimezone()
    out = [
        "Replacement manifest summary",
        f"Generated at: {now.isoformat(timespec='seconds')}",
        f"Script commit: {git_commit_hash()}",
        f"tiktoken {tiktoken.__version__}, encoding {ENCODING_NAME}",
        f"Context example source_id: {EXAMPLE_SOURCE_ID}",
        f"Baseline prompt total tokens: {baseline['total']}",
        f"Manifest: {MANIFEST_FILE.relative_to(MANIFEST_FILE.parents[1])} ({len(sites)} sites)",
        "",
        "Sites per condition (items / lines / original tokens in replaced spans incl. newline):",
    ]
    for letter, cond in LETTER_CONDITION.items():
        cs = [s for s in sites if s["condition"] == letter]
        items = len({s["item_id"] for s in cs})
        toks = sum(baseline["sites"][s["site_id"]]["count"] for s in cs)
        out.append(f"  {letter} {cond:28s} items={items:2d} (expected {EXPECTED_ITEMS[letter]:2d})  "
                   f"lines={len(cs):2d} (expected {EXPECTED_LINES[letter]:2d})  tokens={toks}")
    unclean_start = [s["line_no"] for s in sites if not baseline["sites"][s["site_id"]]["start_clean"]]
    glued = [s["line_no"] for s in sites if not baseline["sites"][s["site_id"]]["newline_separate"]]
    out += [
        "",
        "Token counts are for the replaced text plus the line's newline (see manual_sites.py).",
        f"Sites whose span start is not a token boundary: {len(unclean_start)} {unclean_start}",
        f"Sites whose newline is glued to the preceding token in the original: {len(glued)} {glued}",
        "",
        "Per-site token counts (site_id line condition item tokens):",
    ]
    for s in sites:
        out.append(f"  {s['site_id']:3d} {s['line_no']:4d} {s['condition']} {s['item_id']} "
                   f"{baseline['sites'][s['site_id']]['count']:3d}")
    REPORTS_DIR.mkdir(exist_ok=True)
    report = REPORTS_DIR / f"replacement-manifest-summary-{now:%Y-%m-%d}.txt"
    report.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out[:16]))
    print(f"\nWrote {MANIFEST_FILE}\nWrote {report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
