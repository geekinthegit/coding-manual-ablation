"""Main-analysis entry point: score a completed run and write its report (6, 4.2, 5.2.3).

Usage:
    python scripts/score_run.py --run-id <run_id> [--scoring-labels <path>] [--runs-dir <dir>]

Steps (main):
1. scorer.load_table: entry checks of 6.1.1 (Refused) and the join of human
   and final labels; Refused and ValueError propagate so the process exits
   with a non-zero status.
2. Point estimates: standalone κ for every condition (6.1.1) and the paired
   contrast for each condition in PAIRED_CONDITIONS (6.1.2).
3. Bootstrap with scorer.N_REPLICATES and scorer.BOOTSTRAP_SEED only (6.2.1);
   the 18 statistics of statistic_keys are summarised with
   summarize_replicates against their point estimates (6.2.2, 6.2.3).
4. Repeated-call diagnostics per condition (4.2).
5. runs/<run_id>/score_report.txt and runs/<run_id>/score_summary.json are
   written, overwriting earlier ones. The replicate arrays are not saved and
   no other file under the run directory is touched.

The text report is rendered from the same dictionary that is written as
JSON, so the two files cannot disagree. Floats are shown with four decimals
in the text and unrounded in the JSON; None is null; numpy types are never
put into the JSON (json.dumps is called without a fallback encoder).
"""

import argparse
import json
import platform
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

import scorer
from build_inputs import CONDITIONS, git_commit_hash
from parse_attempts import RUNS_DIR
from paths import REPO_ROOT
from repeat_diagnostics import diagnostics_from_run
from run_experiment import sha256_file
from scorer import (
    BASELINE, CATEGORIES, MISSING_STATUSES, PAIRED_CONDITIONS, IntervalSummary, KappaResult,
    bootstrap_replicates, delta_key, draw_indices, load_table, paired, paired_baseline_key,
    paired_key, standalone, standalone_key, statistic_keys, summarize_replicates,
)

DEFAULT_SCORING_LABELS = REPO_ROOT / "data" / "scoring_labels.csv"
REPORT_NAME = "score_report.txt"
SUMMARY_NAME = "score_summary.json"

# Fixed interpretive notes printed with every report (6.5, 3.3, 6.1.2).
NOTES = [
    "No new contrast is formed between the four delta-kappa estimates; the negative control is "
    "neither subtracted from nor used as a threshold for the replacement conditions; names-only has "
    "no delta-kappa (6.5, 3.3).",
    "Where a comparison has missing final labels, its delta-kappa is the agreement difference on the "
    "observed paired set, not the complete 300-item estimand (6.1.2).",
]


def fmt(x: float | None) -> str:
    """Four-decimal text form of a statistic; None is 'not estimable' (6.2.2)."""
    return "not estimable" if x is None else format(x, ".4f")


def fmt_ratio(x: float | None) -> str:
    """Four-decimal text form of a descriptive ratio; None is 'unavailable' (4.2.5)."""
    return "unavailable" if x is None else format(x, ".4f")


def kappa_dict(k: KappaResult) -> dict:
    """JSON-ready view of a KappaResult without the confusion table."""
    return {"n": k.n, "agree": k.agree, "S": k.S, "p_o": k.p_o, "p_e": k.p_e, "kappa": k.kappa}


def interval_text(s: dict) -> str:
    """One text fragment for an IntervalSummary dict: CI or withheld reason, then undefined count (6.2.2)."""
    if s["lower"] is None:
        ci = f"95% CI withheld ({s['withheld_reason']})"
    else:
        ci = f"95% CI [{fmt(s['lower'])}, {fmt(s['upper'])}]"
        if s["degenerate"]:
            ci += " degenerate"
    return f"{ci}; undefined {s['undefined_count']}/{s['n_replicates']} ({format(s['undefined_proportion'], '.4f')})"


def analyse(run_dir: Path, scoring_labels_path: Path) -> dict:
    """Run steps 1-4 and return the JSON-ready summary (6.1, 6.2, 6.5, 4.2, 5.2.3).

    Keys: header, standalone, paired, marginals_confusion, repeat_diagnostics,
    notes. Interval summaries use the IntervalSummary field names. Every
    value is a Python int, float, str, None, list or dict.
    """
    loaded = load_table(run_dir, scoring_labels_path)
    table = loaded.table

    # Step 2: point estimates.
    standalone_results = {c: standalone(table, c) for c in CONDITIONS}
    paired_results = {c: paired(table, c) for c in PAIRED_CONDITIONS}
    point: dict[str, float | None] = {}
    for c in CONDITIONS:
        point[standalone_key(c)] = standalone_results[c].result.kappa
    for c in PAIRED_CONDITIONS:
        p = paired_results[c]
        point[paired_baseline_key(c)] = p.baseline.kappa
        point[paired_key(c)] = p.result.kappa
        point[delta_key(c)] = p.delta_kappa

    # Step 3: bootstrap with the module constants only (6.2.1).
    draws = draw_indices(len(table))
    reps = bootstrap_replicates(table, draws)
    intervals: dict[str, dict] = {k: asdict(summarize_replicates(reps.values[k], point[k]))
                                  for k in statistic_keys()}

    # Step 4: repeated-call diagnostics (4.2).
    diagnostics = diagnostics_from_run(run_dir)

    header = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_commit": git_commit_hash(),
        "run_id": run_dir.name,
        "run_dir": str(run_dir),
        "final_labels_sha256": loaded.final_labels_sha256,
        "labels_sha256": sha256_file(run_dir / "labels.csv"),
        "scoring_labels_sha256": loaded.scoring_labels_sha256,
        "scoring_labels_path": str(scoring_labels_path),
        "n_records": len(table),
        "n_replicates": reps.n_replicates,
        "seed": reps.seed,
        "numpy_version": reps.numpy_version,
        "python_version": platform.python_version(),
    }

    standalone_out = {}
    marginals_out = {}
    for c in CONDITIONS:
        k = standalone_results[c].result
        standalone_out[c] = {**kappa_dict(k), "interval": intervals[standalone_key(c)]}
        marginals_out[c] = {
            "n": k.n,
            "categories": list(CATEGORIES),
            "human_marginal": {h: sum(k.confusion[h].values()) for h in CATEGORIES},
            "predicted_marginal": {p: sum(k.confusion[h][p] for h in CATEGORIES) for p in CATEGORIES},
            "confusion": [[k.confusion[h][p] for p in CATEGORIES] for h in CATEGORIES],
        }

    paired_out = {}
    for c in PAIRED_CONDITIONS:
        p = paired_results[c]
        paired_out[c] = {
            "original_n": p.original_n, "paired_n": p.paired_n,
            "both": p.both, "baseline_only": p.baseline_only,
            "condition_only": p.condition_only, "neither": p.neither,
            "missing_baseline": dict(p.missing_baseline),
            "missing_condition": dict(p.missing_condition),
            "discordant": p.discordant,
            "baseline": {**kappa_dict(p.baseline), "interval": intervals[paired_baseline_key(c)]},
            "condition": {**kappa_dict(p.result), "interval": intervals[paired_key(c)]},
            "delta": {"value": p.delta_kappa, "interval": intervals[delta_key(c)]},
        }

    return {
        "header": header,
        "standalone": standalone_out,
        "paired": paired_out,
        "marginals_confusion": marginals_out,
        "repeat_diagnostics": {c: asdict(diagnostics[c]) for c in CONDITIONS},
        "notes": list(NOTES),
    }


def render_report(summary: dict) -> str:
    """Text report from the summary dict, section by section (5.2.3, 6.1, 6.2, 6.5, 4.2)."""
    h = summary["header"]
    lines = [
        "Score report",
        f"Generated at: {h['generated_at']}",
        f"Script commit: {h['git_commit']}",
        f"Run id: {h['run_id']}",
        f"Run directory: {h['run_dir']}",
        f"final_labels.csv sha256: {h['final_labels_sha256']}",
        f"labels.csv sha256: {h['labels_sha256']}",
        f"scoring_labels.csv sha256: {h['scoring_labels_sha256']} ({h['scoring_labels_path']})",
        f"n_records: {h['n_records']}",
        f"Bootstrap: n_replicates {h['n_replicates']}, seed {h['seed']}, numpy {h['numpy_version']}",
        f"Python: {h['python_version']}",
        "",
        "== Standalone kappa per condition (6.1.1, 6.2.2) ==",
    ]
    for c in CONDITIONS:
        s = summary["standalone"][c]
        lines.append(f"{c}: n={s['n']} P_o={fmt(s['p_o'])} P_e={fmt(s['p_e'])} kappa={fmt(s['kappa'])}; "
                     f"{interval_text(s['interval'])}")

    lines += ["", "== Paired contrasts against baseline (6.1.2, 6.2.2, 6.2.3) =="]
    for c in PAIRED_CONDITIONS:
        p = summary["paired"][c]
        mb, mc = p["missing_baseline"], p["missing_condition"]
        lines.append(f"-- {c} vs {BASELINE} --")
        lines.append(f"original n={p['original_n']} paired n={p['paired_n']} both={p['both']} "
                     f"baseline only={p['baseline_only']} condition only={p['condition_only']} "
                     f"neither={p['neither']}")
        lines.append("missing baseline: " + " ".join(f"{s}={mb[s]}" for s in MISSING_STATUSES)
                     + "; missing condition: " + " ".join(f"{s}={mc[s]}" for s in MISSING_STATUSES))
        lines.append(f"baseline kappa (paired set)={fmt(p['baseline']['kappa'])}; "
                     f"{interval_text(p['baseline']['interval'])}")
        lines.append(f"condition kappa (paired set)={fmt(p['condition']['kappa'])}; "
                     f"{interval_text(p['condition']['interval'])}")
        d = p["delta"]["interval"]
        delta_line = f"delta kappa={fmt(p['delta']['value'])}; {interval_text(d)}"
        if d["degenerate"]:
            delta_line += f" (paired n={p['paired_n']}, discordant={p['discordant']})"
        lines.append(delta_line)
        lines.append(f"discordant final labels on paired set={p['discordant']}")

    lines += ["", "== Marginals and confusion per condition, standalone analysis set (6.5) =="]
    for c in CONDITIONS:
        m = summary["marginals_confusion"][c]
        lines.append(f"-- {c} (n={m['n']}) --")
        lines.append("human marginal: " + ", ".join(f"{cat}={m['human_marginal'][cat]}" for cat in CATEGORIES))
        lines.append("predicted marginal: " + ", ".join(f"{cat}={m['predicted_marginal'][cat]}" for cat in CATEGORIES))
        lines.append("confusion (rows human, columns predicted, tag order 0-6):")
        for cat, row in zip(CATEGORIES, m["confusion"]):
            lines.append(f"  {cat:28s} " + " ".join(f"{v:4d}" for v in row))

    lines += ["", "== Repeated-call diagnostics per condition (4.2) =="]
    for c in CONDITIONS:
        d = summary["repeat_diagnostics"][c]
        den, nfin = d["initial_valid_denominator"], d["items_with_final_label"]
        lines.append(f"-- {c} --")
        lines.append(f"n_items={d['n_items']} initial_valid_denominator={den} "
                     f"items_lacking_all_initial_valid={d['items_lacking_all_initial_valid']}")
        lines.append(f"pattern 3/3={d['pattern_3_3']} ({fmt_ratio(d['pattern_3_3_share'])}) "
                     f"2/1={d['pattern_2_1']} ({fmt_ratio(d['pattern_2_1_share'])}) "
                     f"1/1/1={d['pattern_1_1_1']} ({fmt_ratio(d['pattern_1_1_1_share'])}); denominator {den}")
        lines.append(f"unanimity_rate={fmt_ratio(d['unanimity_rate'])} (denominator {den})")
        lines.append(f"mean_agreement_with_final={fmt_ratio(d['mean_agreement_with_final'])} "
                     f"(items_with_final_label {nfin})")
        lines.append(f"items_with_tie={d['items_with_tie']} additional_calls_total={d['additional_calls_total']} "
                     f"calls_repeat_4={d['calls_repeat_4']} calls_repeat_5={d['calls_repeat_5']}")
        lines.append(f"unresolved_tie={d['unresolved_tie']} "
                     f"insufficient_valid_repeats={d['insufficient_valid_repeats']}")

    lines += ["", "== Notes =="]
    lines += summary["notes"]
    return "\n".join(lines) + "\n"


def write_outputs(run_dir: Path, summary: dict) -> tuple[Path, Path]:
    """Write score_report.txt and score_summary.json under run_dir, overwriting (step 5)."""
    report_path = run_dir / REPORT_NAME
    summary_path = run_dir / SUMMARY_NAME
    text = json.dumps(summary, indent=2, ensure_ascii=False)   # no default=: numpy types would raise
    report_path.write_text(render_report(summary), encoding="utf-8")
    summary_path.write_text(text + "\n", encoding="utf-8")
    return report_path, summary_path


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Score a completed run: kappa, delta kappa, bootstrap CIs, 4.2 diagnostics.")
    ap.add_argument("--run-id", required=True, help="run directory name under --runs-dir")
    ap.add_argument("--scoring-labels", type=Path, default=DEFAULT_SCORING_LABELS,
                    help=f"human labels CSV (default {DEFAULT_SCORING_LABELS})")
    ap.add_argument("--runs-dir", type=Path, default=RUNS_DIR,
                    help=f"directory holding the run directories (default {RUNS_DIR})")
    args = ap.parse_args(argv)
    run_dir = args.runs_dir / args.run_id
    summary = analyse(run_dir, args.scoring_labels)
    report_path, summary_path = write_outputs(run_dir, summary)
    print(f"wrote {report_path}")
    print(f"wrote {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
