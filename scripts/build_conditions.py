"""Generate the four condition manuals under manual/ (git-ignored).

Uses the symbol and construction rule fixed in Decision Log 3.2.2
(SYMBOL, RULE below) and the per-site repeat counts found by
manual_sites.fit_repeats so that every site keeps its original token
count in the full prompt. baseline is manual/chapter1.txt unchanged.

Assertions
  * every line outside the condition's sites is byte-identical to the
    baseline line;
  * every site line keeps its preserved prefix;
  * the manifest's site set equals the parsed site set.

Outputs
    manual/chapter1_<condition>.txt for the four replacement conditions
    data/placeholder_plan.csv            (site_id, condition, n, filler)
    reports/build-conditions-<date>.txt

Usage (repository root, conda base with tiktoken 0.14.0):
    python scripts/build_conditions.py
"""

import csv
import sys
from datetime import datetime

import tiktoken

from build_inputs import git_commit_hash
from manual_sites import (
    CONDITION_FILES, DATA_DIR, ENCODING_NAME, EXAMPLE_SOURCE_ID, LETTER_CONDITION,
    REPORTS_DIR, build_manual, fit_repeats, make_filler, measure, parse_sites,
    read_lines, read_manifest,
)

# [decided YYYY-MM-DD, Decision Log 3.2.2] -- fill in after the probe.
SYMBOL: str | None = "%"  # [decided 2026-09-15, Decision Log 3.2.2]
RULE: str | None = "B"

PLAN_FILE = DATA_DIR / "placeholder_plan.csv"


def main() -> int:
    assert SYMBOL and RULE in ("A", "B"), "set SYMBOL and RULE from Decision Log 3.2.2 first"
    enc = tiktoken.get_encoding(ENCODING_NAME)
    lines = read_lines()
    sites = parse_sites(lines)
    manifest = read_manifest()
    assert [(r["site_id"], r["line_no"], r["condition"], r["replaced_text"]) for r in manifest] == \
        [(s["site_id"], s["line_no"], s["condition"], s["replaced_text"]) for s in sites], \
        "manifest does not match the parsed sites; rebuild the manifest"
    base_text, base_spans = build_manual(lines, sites, None)
    baseline = measure(enc, base_text, base_spans, EXAMPLE_SOURCE_ID)
    for r in manifest:
        assert baseline["sites"][r["site_id"]]["count"] == r["original_token_count"], r["site_id"]

    now = datetime.now().astimezone()
    out = [
        "Condition manual generation",
        f"Generated at: {now.isoformat(timespec='seconds')}",
        f"Script commit: {git_commit_hash()}",
        f"tiktoken {tiktoken.__version__}, encoding {ENCODING_NAME}",
        f"Symbol {SYMBOL!r}, rule {RULE}",
        "",
    ]
    plan_rows = []
    for letter, cond in LETTER_CONDITION.items():
        fit = fit_repeats(enc, lines, sites, baseline, letter, SYMBOL, RULE)
        if not fit["ok"]:
            out.append(f"{cond}: FAILED to fit repeat counts")
            out += [f"  {f}" for f in fit["failures"]]
            print("\n".join(out))
            return 1
        fillers = {sid: make_filler(next(s["replaced_text"] for s in sites if s["site_id"] == sid),
                                    SYMBOL, RULE, n) for sid, n in fit["n"].items()}
        text, _ = build_manual(lines, sites, letter, fillers)
        new_lines = text[:-1].split("\n")
        assert len(new_lines) == len(lines)
        site_lines = {s["line_no"]: s for s in sites if s["condition"] == letter}
        for i, (old, new) in enumerate(zip(lines, new_lines), start=1):
            if i in site_lines:
                assert new.startswith(site_lines[i]["preserved_prefix"]), i
                assert new != old, f"site line {i} unchanged"
            else:
                assert new == old, f"non-site line {i} changed"
        path = CONDITION_FILES[cond]
        path.write_text(text, encoding="utf-8")
        assert path.read_bytes() == text.encode("utf-8")
        ns = sorted(fit["n"].values())
        out.append(f"{cond}: wrote {path.relative_to(path.parents[1])}  sites={len(fit['n'])}  "
                   f"n min/max={ns[0]}/{ns[-1]}  iterations={fit['iterations']}")
        for sid, n in sorted(fit["n"].items()):
            plan_rows.append({"site_id": sid, "condition": letter, "n": n, "filler": fillers[sid]})

    with PLAN_FILE.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["site_id", "condition", "n", "filler"])
        w.writeheader()
        w.writerows(plan_rows)
    out.append(f"Wrote {PLAN_FILE.relative_to(PLAN_FILE.parents[1])} ({len(plan_rows)} sites)")
    REPORTS_DIR.mkdir(exist_ok=True)
    report = REPORTS_DIR / f"build-conditions-{now:%Y-%m-%d}.txt"
    report.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))
    print(f"Wrote {report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
