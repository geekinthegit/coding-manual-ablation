"""score_run: report and JSON output on a terminated, parsed synthetic run (no API calls).

The run is built with the helpers of tests/test_scorer_entry.py and
tests/test_repeat_diagnostics.py: utterances 1 and 2, every call Not coded,
parsed with the real parser. The bootstrap runs with the module constants
(10,000 replicates); the table has two records, so it is quick. One scored
run is shared by the tests that read its outputs.
"""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

import score_run
import scorer
from build_inputs import CONDITIONS
from paths import REPO_ROOT
from tests.test_repeat_diagnostics import completed_run, write_scoring_labels
from tests.test_scorer_entry import RUN_ID, always, prepare_run, run_pass1

SCRIPT = REPO_ROOT / "scripts" / "score_run.py"
LABEL_ROWS = [(1, 1, 0), (2, 2, 1)]


@pytest.fixture(scope="module")
def scored(tmp_path_factory):
    """Run score_run.main once on a completed synthetic run; return (run_dir, report text, summary dict)."""
    tmp_path = tmp_path_factory.mktemp("scored")
    with pytest.MonkeyPatch.context() as mp:
        run_dir = completed_run(tmp_path, mp)
    labels_path = tmp_path / "scoring_labels.csv"
    write_scoring_labels(labels_path, LABEL_ROWS)
    rc = score_run.main(["--run-id", RUN_ID, "--runs-dir", str(tmp_path), "--scoring-labels", str(labels_path)])
    assert rc == 0
    report = (run_dir / score_run.REPORT_NAME).read_text(encoding="utf-8")
    summary = json.loads((run_dir / score_run.SUMMARY_NAME).read_text(encoding="utf-8"))
    return run_dir, report, summary


# --- 1. both files, header values (5.2.3, 6.2.1) ---------------------------------------

def test_outputs_exist_and_header_carries_bootstrap_conditions(scored):
    run_dir, report, summary = scored
    assert (run_dir / score_run.REPORT_NAME).exists()
    assert (run_dir / score_run.SUMMARY_NAME).exists()
    h = summary["header"]
    assert h["n_replicates"] == scorer.N_REPLICATES
    assert h["seed"] == scorer.BOOTSTRAP_SEED
    assert h["numpy_version"] == np.__version__
    assert h["run_id"] == RUN_ID and h["n_records"] == 2
    head = "\n".join(report.splitlines()[:12])
    assert str(scorer.N_REPLICATES) in head
    assert str(scorer.BOOTSTRAP_SEED) in head
    assert np.__version__ in head
    assert set(summary) == {"header", "standalone", "paired", "marginals_confusion", "repeat_diagnostics", "notes"}
    assert set(summary["standalone"]) == set(CONDITIONS)
    assert set(summary["paired"]) == set(scorer.PAIRED_CONDITIONS)


# --- 2. text and JSON agree at four decimals (6.1.1) -------------------------------------

def test_text_kappa_matches_json_at_four_decimals(scored):
    _, report, summary = scored
    lines = report.splitlines()
    for c in CONDITIONS:
        k = summary["standalone"][c]["kappa"]
        shown = "not estimable" if k is None else format(k, ".4f")
        cond_lines = [ln for ln in lines if ln.startswith(f"{c}: n=")]
        assert len(cond_lines) == 1, c
        assert f"kappa={shown}" in cond_lines[0]


# --- 3. unparsed run: non-zero exit, no outputs (6.1.1) -----------------------------------

def test_unparsed_run_exits_nonzero_without_outputs(tmp_path, monkeypatch):
    run_dir = prepare_run(tmp_path, monkeypatch, ids=(1, 2))
    run_pass1(run_dir, always("Not coded"))          # terminated but not parsed: no final_labels.csv
    labels_path = tmp_path / "scoring_labels.csv"
    write_scoring_labels(labels_path, LABEL_ROWS)
    proc = subprocess.run([sys.executable, str(SCRIPT), "--run-id", RUN_ID, "--runs-dir", str(tmp_path),
                           "--scoring-labels", str(labels_path)], capture_output=True, text=True)
    assert proc.returncode != 0
    assert "Refused" in proc.stderr
    assert not (run_dir / score_run.REPORT_NAME).exists()
    assert not (run_dir / score_run.SUMMARY_NAME).exists()


# --- 4. plain JSON types ---------------------------------------------------------------------

def test_summary_is_plain_json(scored):
    _, _, summary = scored
    json.dumps(summary)                                    # no numpy types survived the round trip
    assert type(summary["header"]["n_replicates"]) is int
    assert type(summary["header"]["seed"]) is int
    for c in CONDITIONS:
        k = summary["standalone"][c]["kappa"]
        assert k is None or type(k) is float
        assert type(summary["standalone"][c]["n"]) is int
        iv = summary["standalone"][c]["interval"]
        assert type(iv["undefined_count"]) is int and type(iv["undefined_proportion"]) is float
    for c in scorer.PAIRED_CONDITIONS:
        d = summary["paired"][c]["delta"]["value"]
        assert d is None or type(d) is float
