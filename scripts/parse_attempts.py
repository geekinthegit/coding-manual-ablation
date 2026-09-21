"""Parse attempts JSONL files into labels.csv and final_labels.csv (5.6.8).

Reads every runs/<run_id>/attempts_passN.jsonl present (N = 1, 2, 3) without
modifying them and writes, deterministically and re-runnably:

* labels.csv        one row per attempt_completed record: run_id, pass,
                    utterance_id, condition, repeat, attempt, category, valid.
* final_labels.csv  one row per (utterance_id, condition): run_id,
                    utterance_id, condition, final_label (empty when none),
                    status in {resolved, tie_pending, unresolved_tie,
                    insufficient_valid_repeats}, valid_repeats, repeats_used.

outcome, invalid_reason and category are re-derived from raw_response with
validation.validate_body -- the same function the runner used -- and the run
is refused if the re-derived values differ from the recorded ones.

Aggregation (5.4.2 plurality, 5.4.3 tie, 5.4.8 insufficient valid repeats)
is implemented here. run_experiment.py calls parse_run() and then reads the
tie_pending rows of final_labels.csv to build the pass 2 / pass 3 call lists;
it does not aggregate in memory.

Usage (repository root):
    python scripts/parse_attempts.py --run-id <run_id>          # writes both files
    python scripts/parse_attempts.py --run-id <run_id> --ties   # also prints tie_pending pairs
"""

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from validation import validate_body

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = REPO_ROOT / "runs"

LABEL_COLUMNS = ["run_id", "pass", "utterance_id", "condition", "repeat", "attempt", "category", "valid"]
FINAL_COLUMNS = ["run_id", "utterance_id", "condition", "final_label", "status", "valid_repeats", "repeats_used"]
STATUSES = ("resolved", "tie_pending", "unresolved_tie", "insufficient_valid_repeats")
PASSES = (1, 2, 3)     # pass 1 = planned repeats; 2, 3 = first and second tie-break (5.4.3)

R_PLANNED = 3          # 5.4.1
MAX_TIE_BREAKS = 2     # 5.4.3: at most 2 additional calls
MAX_REPEATS = R_PLANNED + MAX_TIE_BREAKS   # 5
MIN_VALID_REPEATS = 2  # 5.4.8


class TruncatedLastLine(Exception):
    """Only the final record is incomplete; --repair may remove it (5.6.7)."""

    def __init__(self, path: Path, offset: int, text: bytes):
        super().__init__(f"{path}: incomplete final record ({len(text)} bytes)")
        self.path, self.offset, self.text = path, offset, text


class CorruptedFile(Exception):
    """A non-final record fails to parse; resume is refused (5.6.7)."""


def read_jsonl_strict(path: Path) -> list[dict]:
    """Parse a JSONL file; raise TruncatedLastLine / CorruptedFile as 5.6.7."""
    data = path.read_bytes()
    if not data:
        return []
    ends_with_newline = data.endswith(b"\n")
    segments = data.split(b"\n")
    if ends_with_newline:
        segments = segments[:-1]
    records: list[dict] = []
    offset = 0
    last = len(segments) - 1
    for i, seg in enumerate(segments):
        try:
            rec = json.loads(seg.decode("utf-8"))
            if not isinstance(rec, dict):
                raise ValueError("record is not an object")
        except (ValueError, UnicodeDecodeError) as exc:
            if i == last:
                raise TruncatedLastLine(path, offset, seg) from exc
            raise CorruptedFile(f"{path}: record {i + 1} fails to parse: {exc}") from exc
        records.append(rec)
        offset += len(seg) + 1
    return records


def labels_from_records(records: list[dict]) -> list[dict]:
    """One label row per attempt_completed, validity re-derived (5.6.8).

    5.6.8 requires the parser to re-derive outcome, invalid_reason and category
    from raw_response with the same function the runner used, and to refuse to
    write when the result differs from what was recorded. The refusal is not a
    way of correcting the record. A disagreement means the runner and the parser
    applied different validity rules (5.4.4, 5.4.5), so no label in the file
    could be attributed to a known rule; raising here prevents the derived files
    from existing at all and leaves the attempts JSONL as the only source of
    truth. Silently preferring either side would hide exactly the defect that
    re-derivation exists to detect.

    An outcome of success or invalid_response without an HTTP 200 body is
    refused for the same reason: 5.4.5 defines both only on a 200 body, so such
    a record cannot have been produced by the specified rule.

    Exception (5.6.8, added 2026-09-21): a record whose recorded outcome is
    fatal_error is not re-derived even when it carries an HTTP 200 body, and
    yields a row with no category and valid False. Such a record comes from an
    unexpected exception after the response was received (5.6.5); the runner
    did not establish validity at call time, so the body is kept in the record
    for inspection and is not counted as a label.
    """
    rows = []
    for rec in records:
        if rec.get("event") != "attempt_completed":
            continue
        outcome = rec["outcome"]
        category = None
        if outcome == "fatal_error":
            pass                                    # never re-derived (5.6.8, 2026-09-21)
        elif rec.get("http_status") == 200 and rec.get("raw_response") is not None:
            derived = validate_body(rec["raw_response"])
            if (derived.outcome, derived.invalid_reason) != (outcome, rec.get("invalid_reason")):
                raise ValueError(
                    f"recorded outcome {outcome}/{rec.get('invalid_reason')} differs from "
                    f"re-derived {derived.outcome}/{derived.invalid_reason} "
                    f"(order_index {rec['order_index']}, attempt {rec['attempt']})"
                )
            category = derived.category
        elif outcome in ("success", "invalid_response"):
            raise ValueError(
                f"outcome {outcome} without an HTTP 200 body (order_index {rec['order_index']})"
            )
        rows.append({
            "run_id": rec["run_id"],
            "pass": rec["pass"],
            "utterance_id": rec["utterance_id"],
            "condition": rec["condition"],
            "repeat": rec["repeat"],
            "attempt": rec["attempt"],
            "category": category if category is not None else "",
            "valid": outcome == "success",
        })
    rows.sort(key=lambda r: (r["pass"], r["utterance_id"], r["condition"], r["repeat"], r["attempt"]))
    return rows


def write_labels(rows: list[dict], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LABEL_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def read_labels(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["pass"] = int(r["pass"])
        r["utterance_id"] = int(r["utterance_id"])
        r["repeat"] = int(r["repeat"])
        r["attempt"] = int(r["attempt"])
        r["valid"] = r["valid"] == "True"
    return rows


def aggregate(rows: list[dict]) -> dict[tuple[int, str], dict]:
    """Apply 5.4.2 / 5.4.3 / 5.4.8 to label rows.

    Returns, per (utterance_id, condition): final_label (str or None), status in
    STATUSES, valid_repeats, repeats_used (highest repeat number seen), counts.
    "tie_pending" means a further tie-break call is allowed (repeats_used < 5).
    Whether the planned repeats are terminated is a runner question (5.6.6);
    this function only aggregates the rows it is given.
    """
    by_pair: dict[tuple[int, str], list[dict]] = defaultdict(list)
    for r in rows:
        by_pair[(r["utterance_id"], r["condition"])].append(r)

    out: dict[tuple[int, str], dict] = {}
    for pair, prs in sorted(by_pair.items()):
        valid_by_repeat: dict[int, str] = {}
        for r in prs:
            if r["valid"]:
                if r["repeat"] in valid_by_repeat:
                    raise ValueError(f"two valid attempts for repeat {r['repeat']} of {pair}")
                valid_by_repeat[r["repeat"]] = r["category"]
        repeats_used = max(r["repeat"] for r in prs)
        counts = Counter(valid_by_repeat.values())
        result = {"final_label": None, "status": None, "valid_repeats": len(valid_by_repeat),
                  "repeats_used": repeats_used, "counts": dict(counts)}
        if len(valid_by_repeat) < MIN_VALID_REPEATS:
            result["status"] = "insufficient_valid_repeats"
        else:
            top = max(counts.values())
            leaders = sorted(label for label, c in counts.items() if c == top)
            if len(leaders) == 1:
                result["final_label"] = leaders[0]
                result["status"] = "resolved"
            elif repeats_used < MAX_REPEATS:
                result["status"] = "tie_pending"
            else:
                result["status"] = "unresolved_tie"
        out[pair] = result
    return out


def tie_pairs(rows: list[dict]) -> list[tuple[int, str]]:
    """(utterance_id, condition) pairs that need a tie-break call (5.4.3)."""
    return [pair for pair, res in aggregate(rows).items() if res["status"] == "tie_pending"]


def final_rows(rows: list[dict], run_id: str) -> list[dict]:
    """final_labels.csv rows in the column order 5.6.8 fixes.

    Flattens aggregate() into the file's columns. A pair with no final label
    gets the empty string, never a category, so that the 5.4.8 cases stay
    distinguishable from the substantive label Not coded; the reason is carried
    by status, which is why status is written even when a label exists.
    """
    out = []
    for (uid, cond), res in aggregate(rows).items():
        out.append({"run_id": run_id, "utterance_id": uid, "condition": cond,
                    "final_label": res["final_label"] if res["final_label"] is not None else "",
                    "status": res["status"], "valid_repeats": res["valid_repeats"],
                    "repeats_used": res["repeats_used"]})
    return out


def write_final_labels(rows: list[dict], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FINAL_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def read_final_labels(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["utterance_id"] = int(r["utterance_id"])
        r["valid_repeats"] = int(r["valid_repeats"])
        r["repeats_used"] = int(r["repeats_used"])
        if r["status"] not in STATUSES:
            raise ValueError(f"{path}: unknown status {r['status']!r}")
    return rows


def tie_pending_pairs(path: Path) -> list[tuple[int, str]]:
    """(utterance_id, condition) with status tie_pending, from final_labels.csv (5.6.8).

    5.6.8 makes the written file, not an in-memory aggregation, the source of
    the pass 2 and pass 3 call lists (5.4.3), so this reads back what was
    written; tie_pairs() serves callers that already hold the rows. Going
    through the file keeps the selection auditable afterwards and lets the
    manifest record that file's sha256 (5.6.2), which resume verification then
    checks.
    """
    return sorted((r["utterance_id"], r["condition"]) for r in read_final_labels(path)
                  if r["status"] == "tie_pending")


def attempts_files(run_dir: Path) -> list[Path]:
    return [p for p in (run_dir / f"attempts_pass{n}.jsonl" for n in PASSES) if p.exists()]


def parse_run(run_dir: Path, run_id: str | None = None) -> tuple[list[dict], list[dict]]:
    """Read every attempts file present and write the two derived files (5.6.8).

    Deterministic and re-runnable as 5.6.8 requires: the attempts files are
    never modified, and re-running after a later pass only widens the input set.
    That is how the pass 2 and pass 3 tie lists (5.4.3) are produced and why
    5.6.8 has the parser run once more after the last pass before any analysis.
    Reading all passes together, rather than one file at a time, is what lets
    repeats 4 and 5 be aggregated with repeats 1 to 3 for the same pair.

    Errors from the attempts files (TruncatedLastLine, CorruptedFile) propagate
    unchanged so the caller can apply the 5.6.7 repair rule. ValueError marks a
    missing attempts file or a record that disagrees with its own body; repair
    must not touch the latter, since it is not damage to the file.
    """
    files = attempts_files(run_dir)
    if not files:
        raise ValueError(f"no attempts files under {run_dir}")
    records: list[dict] = []
    for path in files:
        records.extend(read_jsonl_strict(path))
    rows = labels_from_records(records)
    run_ids = {r["run_id"] for r in rows}
    if run_id is None:
        if len(run_ids) != 1:
            raise ValueError(f"records carry run_ids {sorted(run_ids)}; pass run_id explicitly")
        run_id = run_ids.pop()
    elif run_ids - {run_id}:
        raise ValueError(f"records carry run_ids {sorted(run_ids)}, expected {run_id}")
    finals = final_rows(rows, run_id)
    write_labels(rows, run_dir / "labels.csv")
    write_final_labels(finals, run_dir / "final_labels.csv")
    return rows, finals


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--ties", action="store_true", help="print tie_pending pairs after writing the files")
    args = ap.parse_args(argv)

    run_dir = RUNS_DIR / args.run_id
    try:
        rows, finals = parse_run(run_dir, args.run_id)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"wrote {run_dir / 'labels.csv'}: {len(rows)} attempt rows")
    print(f"wrote {run_dir / 'final_labels.csv'}: {len(finals)} (utterance, condition) rows")
    for status, n in sorted(Counter(r["status"] for r in finals).items()):
        print(f"  {status}: {n}")
    if args.ties:
        for uid, cond in tie_pending_pairs(run_dir / "final_labels.csv"):
            print(f"tie_pending\t{uid}\t{cond}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
