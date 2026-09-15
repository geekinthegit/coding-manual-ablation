"""Probe candidate placeholder symbols against the procedural criteria of
Decision Log 3.2.2 / 3.2.3, without any API call.

For every candidate symbol and construction rule (A contiguous, B
space-separated; see manual_sites.make_filler) the script reports:
  (a) standalone grouping: tokens produced by symbol * n, n = 1..40,
      and by (' ' + symbol) * n;
  (b) constructibility: whether, with all sites of a condition replaced
      at once, per-site repeat counts exist that reproduce the original
      token count of every site, the index of the first preserved token
      after every site, and the total token count of the full prompt
      (manual_sites.fit_repeats), for all four conditions;
  (d) marker boundary: in the fitted text, a token starts exactly at the
      replaced span of every marker line (the marker is not merged with
      the filler).
Criterion (c), no markdown syntax, is applied by the candidate list.

Nothing here reads agreement results; the choice is made on this report.

Output: reports/symbol-probe-<date>.txt
Usage (repository root, conda base with tiktoken 0.14.0):
    python scripts/probe_symbols.py
"""

import sys
from datetime import datetime

import tiktoken

from build_inputs import git_commit_hash
from manual_sites import (
    ENCODING_NAME, EXAMPLE_SOURCE_ID, LETTER_CONDITION, REPORTS_DIR,
    build_manual, fit_repeats, make_filler, measure, parse_sites, read_lines,
)

# Excluded beforehand (criterion c or reuse of manual content):
#   # - * > + ` [ ] ( ) _   (markdown syntax)   digits   x X and other letters
CANDIDATES = [".", "~", "=", "|", "%", "^", ";", ":", "@", "&", "?"]
RULES = ["A", "B"]
N_MAX = 40


def grouping_table(enc, symbol: str) -> tuple[list[int], list[int]]:
    """Return token counts for symbol*n and (' '+symbol)*n, n=1..N_MAX."""
    contig = [len(enc.encode(symbol * n, disallowed_special=())) for n in range(1, N_MAX + 1)]
    spaced = [len(enc.encode((" " + symbol) * n, disallowed_special=())) for n in range(1, N_MAX + 1)]
    return contig, spaced


def main() -> int:
    enc = tiktoken.get_encoding(ENCODING_NAME)
    lines = read_lines()
    sites = parse_sites(lines)
    base_text, base_spans = build_manual(lines, sites, None)
    baseline = measure(enc, base_text, base_spans, EXAMPLE_SOURCE_ID)
    marker_sites = [s["site_id"] for s in sites if s["preserved_prefix"]]

    now = datetime.now().astimezone()
    out = [
        "Placeholder symbol probe",
        f"Generated at: {now.isoformat(timespec='seconds')}",
        f"Script commit: {git_commit_hash()}",
        f"tiktoken {tiktoken.__version__}, encoding {ENCODING_NAME}",
        f"Context example source_id: {EXAMPLE_SOURCE_ID}; baseline total tokens {baseline['total']}",
        f"Candidates: {' '.join(repr(c) for c in CANDIDATES)}",
        "",
    ]
    summary = []
    for sym in CANDIDATES:
        contig, spaced = grouping_table(enc, sym)
        out += [
            "=" * 72,
            f"Symbol {sym!r}",
            f"  (a) tokens for symbol*n, n=1..{N_MAX}:       {contig}",
            f"      one char = one token for all n: {contig == list(range(1, N_MAX + 1))}",
            f"  (a) tokens for (' '+symbol)*n, n=1..{N_MAX}: {spaced}",
            f"      one ' sym' = one token for all n: {spaced == list(range(1, N_MAX + 1))}",
        ]
        for rule in RULES:
            verdict = True
            reasons = []
            for letter, cond in LETTER_CONDITION.items():
                fit = fit_repeats(enc, lines, sites, baseline, letter, sym, rule)
                if fit["ok"]:
                    fitted, spans = build_manual(
                        lines, sites, letter,
                        {sid: make_filler(next(s["replaced_text"] for s in sites if s["site_id"] == sid),
                                          sym, rule, n) for sid, n in fit["n"].items()})
                    m = measure(enc, fitted, spans, EXAMPLE_SOURCE_ID)
                    bad_marker = [sid for sid in fit["n"] if sid in marker_sites
                                  and not m["sites"][sid]["start_clean"]]
                    ns = sorted(set(fit["n"].values()))
                    out.append(f"  rule {rule} {cond:28s} (b) OK  iterations={fit['iterations']:2d}  "
                               f"n range={ns[0]}..{ns[-1]}  (d) marker merged at sites: {bad_marker or 'none'}")
                    if bad_marker:
                        verdict = False
                        reasons.append(f"{cond}: marker merged with filler at {len(bad_marker)} sites")
                else:
                    verdict = False
                    reasons.append(f"{cond}: " + "; ".join(fit["failures"][:3]))
                    out.append(f"  rule {rule} {cond:28s} (b) FAIL after {fit['iterations']} iterations")
                    out += [f"        {f}" for f in fit["failures"][:5]]
            summary.append((sym, rule, verdict, reasons))
        out.append("")

    out += ["=" * 72, "Summary (symbol, rule, passes b+d for all four conditions):"]
    for sym, rule, ok, reasons in summary:
        out.append(f"  {sym!r} rule {rule}: {'PASS' if ok else 'FAIL'}" + ("" if ok else "  -- " + " | ".join(reasons)))

    REPORTS_DIR.mkdir(exist_ok=True)
    report = REPORTS_DIR / f"symbol-probe-{now:%Y-%m-%d}.txt"
    report.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))
    print(f"\nWrote {report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
