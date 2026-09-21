"""Scorer entry check: refuse to analyse a run that is not complete (6.1.1).

This module currently holds only require_run_complete(). The kappa
computation, the bootstrap, the report and the CLI are not implemented here
yet. Nothing under the run directory is written by this module.

What is reused, never re-implemented
------------------------------------
* Termination of a call (5.6, Terms; 5.4.7): run_experiment.require_pass_terminated.
* Final-label aggregation (5.4, 5.6.8): parse_attempts.labels_from_records,
  final_rows and write_final_labels.
* The refusal exception: run_experiment.Refused.
"""

import json
import tempfile
from pathlib import Path

from parse_attempts import (
    PASSES, final_rows, labels_from_records, read_final_labels, read_jsonl_strict,
    write_final_labels,
)
from run_experiment import Refused, manifest_pairs, require_pass_terminated


def present_passes(run_dir: Path) -> list[int]:
    """Pass numbers with a manifest or an attempts file under run_dir (check 0 of 6.1.1)."""
    return [n for n in PASSES
            if (run_dir / f"manifest_pass{n}.json").exists() or (run_dir / f"attempts_pass{n}.jsonl").exists()]


def rederived_final_labels_csv(run_dir: Path, passes: list[int]) -> bytes:
    """final_labels.csv as the parser would write it now, from the attempts files of `passes`.

    Uses the parse_attempts functions in the order parse_run() uses them
    (labels_from_records -> final_rows -> write_final_labels) but writes to a
    temporary directory, so the run directory is only read. Parser errors
    (TruncatedLastLine, CorruptedFile, ValueError) propagate unchanged.
    """
    records: list[dict] = []
    for n in passes:
        records.extend(read_jsonl_strict(run_dir / f"attempts_pass{n}.jsonl"))
    rows = labels_from_records(records)
    run_ids = {r["run_id"] for r in rows}
    if len(run_ids) != 1:
        raise Refused(f"check C (stale file): attempt records carry run_ids {sorted(run_ids)}, expected exactly one")
    finals = final_rows(rows, run_ids.pop())
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "final_labels.csv"
        write_final_labels(finals, path)
        return path.read_bytes()


def require_run_complete(run_dir: Path) -> None:
    """Refuse analysis unless the run is complete and final_labels.csv is current (6.1.1).

    The checks run in this order and the first failure raises Refused with the
    check name and the reason:

    * Check 0 (pass layout, 5.6.9): a pass is present when its manifest or its
      attempts file exists. Pass 1 must be present and the present passes must
      be 1..k without a gap.
    * Check A (termination, 6.1.1 revision 2026-09-21; 5.6, Terms): every call of
      every present pass must be terminated, i.e. have a valid response or 3
      exhausted attempts (5.4.7). run_experiment.require_pass_terminated decides
      this from the manifest and attempts file of each pass; its Refused is
      propagated unchanged. final_labels.csv cannot show an open call, which is
      why this check reads the attempt records.
    * Check C (stale file, 6.1.1 revision 2026-09-21; 5.6.8): final_labels.csv
      must exist and be byte-identical to what the parser would now write from
      all attempts files present, so a file from an earlier, partial parse is
      not analysed.
    * Check B (coverage, 6.1.1): no row may be tie_pending, and every
      (utterance_id, condition) pair of the pass 1 call list must appear exactly
      once. An absent row is an incomplete record state, not a missing label.

    Returns None when every check passes. Nothing under run_dir is written.
    """
    run_dir = Path(run_dir)

    # Check 0: pass layout.
    passes = present_passes(run_dir)
    if 1 not in passes:
        raise Refused(f"check 0 (pass layout): pass 1 is not present under {run_dir}")
    if passes != list(range(1, len(passes) + 1)):
        raise Refused(f"check 0 (pass layout): present passes {passes} are not contiguous from 1")

    # Check A: termination of every call of every present pass.
    for n in passes:
        require_pass_terminated(run_dir, n)

    # Check C: final_labels.csv equals the current aggregation of the attempts files.
    final_path = run_dir / "final_labels.csv"
    if not final_path.exists():
        raise Refused(f"check C (stale file): {final_path} does not exist; run parse_attempts.py (5.6.8)")
    if final_path.read_bytes() != rederived_final_labels_csv(run_dir, passes):
        raise Refused(f"check C (stale file): {final_path} differs from the aggregation of the attempts "
                      f"files present; rerun parse_attempts.py after the last pass (5.6.8)")

    # Check B: coverage against the pass 1 call list.
    finals = read_final_labels(final_path)
    pending = [(r["utterance_id"], r["condition"]) for r in finals if r["status"] == "tie_pending"]
    if pending:
        raise Refused(f"check B (coverage): {len(pending)} tie_pending rows remain (first {pending[:5]}); "
                      f"the next tie-break pass has not run")
    manifest = json.loads((run_dir / "manifest_pass1.json").read_text(encoding="utf-8"))
    expected = manifest_pairs(manifest)
    counts: dict[tuple[int, str], int] = {}
    for r in finals:
        key = (r["utterance_id"], r["condition"])
        counts[key] = counts.get(key, 0) + 1
    missing = sorted(p for p in expected if counts.get(p, 0) == 0)
    duplicated = sorted(p for p in expected if counts.get(p, 0) > 1)
    if missing or duplicated:
        raise Refused(f"check B (coverage): pass 1 pairs without a final_labels.csv row: {missing[:5]} "
                      f"({len(missing)} total); pairs with more than one row: {duplicated[:5]} "
                      f"({len(duplicated)} total)")
    return None
