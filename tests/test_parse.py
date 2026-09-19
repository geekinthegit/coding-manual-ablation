"""parse_attempts.py: labels from records, 5.4 aggregation, tie list, pass 2 preparation."""

import json

import pytest

import parse_attempts as pa
import run_experiment as rx
from tests.conftest import FakeRaw, fake_prompt, make_runner, ok_body, read_records


def completed(uid, cond, repeat, attempt, outcome, body=None, **kw):
    r = {"event": "attempt_completed", "run_id": "t", "pass": 1, "order_index": 0, "utterance_id": uid,
         "condition": cond, "repeat": repeat, "attempt": attempt, "completed_seq": 1,
         "outcome": outcome, "invalid_reason": None, "http_status": 200 if body is not None else 500,
         "raw_response": body}
    r.update(kw)
    return r


def label_row(uid, cond, repeat, category, valid=True, attempt=1):
    return {"run_id": "t", "pass": 1, "utterance_id": uid, "condition": cond, "repeat": repeat,
            "attempt": attempt, "category": category, "valid": valid}


def test_labels_from_records_rederives_and_sorts():
    recs = [
        completed(2, "baseline", 1, 1, "success", ok_body("Revoicing")),
        completed(1, "baseline", 2, 2, "success", ok_body(" Restating ")),
        completed(1, "baseline", 2, 1, "retryable_error"),
        completed(1, "baseline", 1, 1, "invalid_response", ok_body(category="x"), invalid_reason="label_not_in_enum"),
        {"event": "attempt_started", "order_index": 0},
    ]
    rows = pa.labels_from_records(recs)
    assert [(r["utterance_id"], r["repeat"], r["attempt"], r["category"], r["valid"]) for r in rows] == [
        (1, 1, 1, "", False), (1, 2, 1, "", False), (1, 2, 2, "Restating", True), (2, 1, 1, "Revoicing", True)]


def test_labels_refuse_when_recorded_outcome_disagrees_with_body():
    bad = completed(1, "baseline", 1, 1, "success", ok_body(category="not a label"))
    with pytest.raises(ValueError, match="differs from re-derived"):
        pa.labels_from_records([bad])
    no_body = completed(1, "baseline", 1, 1, "success")
    with pytest.raises(ValueError, match="without an HTTP 200 body"):
        pa.labels_from_records([no_body])


def test_aggregate_plurality_tie_and_insufficient():
    rows = [
        # 3-0 -> final
        *[label_row(1, "baseline", r, "Restating") for r in (1, 2, 3)],
        # 2-1 -> final (plurality == majority)
        label_row(2, "baseline", 1, "Restating"), label_row(2, "baseline", 2, "Revoicing"),
        label_row(2, "baseline", 3, "Restating"),
        # 1-1-1 -> tie pending (repeats used 3 < 5)
        label_row(3, "baseline", 1, "Restating"), label_row(3, "baseline", 2, "Revoicing"),
        label_row(3, "baseline", 3, "Not coded"),
        # one invalid repeat, remaining 1-1 -> tie pending (5.4.8 bullet 1)
        label_row(4, "baseline", 1, "Restating"), label_row(4, "baseline", 2, "", valid=False),
        label_row(4, "baseline", 2, "", valid=False, attempt=2), label_row(4, "baseline", 3, "Revoicing"),
        # only one valid repeat -> insufficient
        label_row(5, "baseline", 1, "Restating"), label_row(5, "baseline", 2, "", valid=False),
        label_row(5, "baseline", 3, "", valid=False),
        # tie persisting through repeat 5 -> unresolved
        label_row(6, "baseline", 1, "Restating"), label_row(6, "baseline", 2, "Revoicing"),
        label_row(6, "baseline", 3, "Not coded"), label_row(6, "baseline", 4, "Pressing for Accuracy"),
        label_row(6, "baseline", 5, "Pressing for Reasoning"),
        # tie broken by repeat 4 -> final
        label_row(7, "baseline", 1, "Restating"), label_row(7, "baseline", 2, "Revoicing"),
        label_row(7, "baseline", 3, "Not coded"), label_row(7, "baseline", 4, "Revoicing"),
    ]
    agg = pa.aggregate(rows)
    assert agg[(1, "baseline")]["status"] == "resolved" and agg[(1, "baseline")]["final_label"] == "Restating"
    assert agg[(2, "baseline")]["final_label"] == "Restating"
    assert agg[(3, "baseline")]["status"] == "tie_pending" and agg[(3, "baseline")]["final_label"] is None
    assert agg[(4, "baseline")]["status"] == "tie_pending" and agg[(4, "baseline")]["valid_repeats"] == 2
    assert agg[(5, "baseline")]["status"] == "insufficient_valid_repeats"
    assert agg[(6, "baseline")]["status"] == "unresolved_tie" and agg[(6, "baseline")]["repeats_used"] == 5
    assert agg[(7, "baseline")]["final_label"] == "Revoicing"
    assert pa.tie_pairs(rows) == [(3, "baseline"), (4, "baseline")]


def test_exhausted_tiebreak_call_counts_as_a_round():
    """5.4.3 (2026-09-19): an exhausted repeat 4 consumes a round; still tied -> pass 3 (repeat 5)."""
    tied = [label_row(1, "baseline", 1, "Restating"), label_row(1, "baseline", 2, "Revoicing"),
            label_row(1, "baseline", 3, "Not coded")]
    r4_exhausted = [label_row(1, "baseline", 4, "", valid=False, attempt=a) for a in (1, 2, 3)]
    agg = pa.aggregate(tied + r4_exhausted)[(1, "baseline")]
    assert (agg["status"], agg["repeats_used"], agg["valid_repeats"]) == ("tie_pending", 4, 3)
    assert pa.tie_pairs(tied + r4_exhausted) == [(1, "baseline")]          # pass 3 target
    r5_exhausted = [label_row(1, "baseline", 5, "", valid=False, attempt=a) for a in (1, 2, 3)]
    agg = pa.aggregate(tied + r4_exhausted + r5_exhausted)[(1, "baseline")]
    assert (agg["status"], agg["repeats_used"], agg["final_label"]) == ("unresolved_tie", 5, None)


def test_two_valid_attempts_in_one_repeat_is_an_error():
    rows = [label_row(1, "baseline", 1, "Restating"), label_row(1, "baseline", 1, "Revoicing", attempt=2)]
    with pytest.raises(ValueError):
        pa.aggregate(rows)


def test_labels_csv_roundtrip(tmp_path):
    rows = [label_row(1, "baseline", 1, "Restating"), label_row(1, "baseline", 2, "", valid=False)]
    path = tmp_path / "labels.csv"
    pa.write_labels(rows, path)
    assert path.read_text(encoding="utf-8").splitlines()[0] == ",".join(pa.LABEL_COLUMNS)
    assert pa.read_labels(path) == rows


def test_final_labels_csv_has_all_four_statuses(tmp_path):
    rows = [
        *[label_row(1, "baseline", r, "Restating") for r in (1, 2, 3)],                       # resolved
        label_row(3, "baseline", 1, "Restating"), label_row(3, "baseline", 2, "Revoicing"),
        label_row(3, "baseline", 3, "Not coded"),                                              # tie_pending
        label_row(5, "baseline", 1, "Restating"), label_row(5, "baseline", 2, "", valid=False),
        label_row(5, "baseline", 3, "", valid=False),                                          # insufficient
        label_row(6, "baseline", 1, "Restating"), label_row(6, "baseline", 2, "Revoicing"),
        label_row(6, "baseline", 3, "Not coded"), label_row(6, "baseline", 4, "Pressing for Accuracy"),
        label_row(6, "baseline", 5, "Pressing for Reasoning"),                                 # unresolved_tie
    ]
    finals = pa.final_rows(rows, "t")
    path = tmp_path / "final_labels.csv"
    pa.write_final_labels(finals, path)
    text = path.read_text(encoding="utf-8").splitlines()
    assert text[0] == "run_id,utterance_id,condition,final_label,status,valid_repeats,repeats_used"
    assert text[1:] == [
        "t,1,baseline,Restating,resolved,3,3",
        "t,3,baseline,,tie_pending,3,3",
        "t,5,baseline,,insufficient_valid_repeats,1,3",
        "t,6,baseline,,unresolved_tie,5,5",
    ]
    back = pa.read_final_labels(path)
    assert [r["status"] for r in back] == ["resolved", "tie_pending", "insufficient_valid_repeats", "unresolved_tie"]
    assert back[0]["final_label"] == "Restating" and back[1]["final_label"] == ""
    assert pa.tie_pending_pairs(path) == [(3, "baseline")]
    assert set(pa.STATUSES) == {"resolved", "tie_pending", "unresolved_tie", "insufficient_valid_repeats"}


@pytest.fixture
def run_after_pass1(tmp_path, monkeypatch):
    """A run directory with pass 1 terminated: (1, baseline) tied 1-1-1, other pairs unanimous."""
    monkeypatch.setattr(rx, "git_commit_hash", lambda: "abc123")
    inp = tmp_path / "ids.csv"
    inp.write_text("source_id\n1\n", encoding="utf-8")
    run_dir = tmp_path / "r1"; run_dir.mkdir()                  # directory name == run_id (CLI layout)
    st = rx.Settings(1, 30.0, 2.0, 60.0, 100)
    rx.prepare_pass1(run_dir, "r1", inp, st, builder=fake_prompt)
    answers = iter(["Restating", "Revoicing", "Not coded"])

    def handler(prompt, n):
        if prompt == fake_prompt(1, "baseline"):
            return FakeRaw(ok_body(next(answers)))
        return FakeRaw(ok_body("Not coded"))

    runner, attempts, _ = make_runner(run_dir, handler, ids=(1,), run_id="r1")
    runner.run()
    return run_dir, st


def run_manifest_pass(run_dir, manifest, handler):
    """Execute one tie-break pass with a fake client over the manifest's call list."""
    runner, attempts, _ = make_runner(run_dir, handler, pass_no=manifest["pass"], calls=manifest["calls"],
                                      run_id=manifest["run_id"])
    runner.run()
    return attempts


NO_CLI = {"concurrency": None, "timeout": None, "backoff_initial": None, "backoff_max": None,
          "failure_threshold": None}


def test_pass2_targets_equal_tie_pending_rows_of_final_labels(run_after_pass1):
    run_dir, st = run_after_pass1
    m2 = rx.prepare_tiebreak_pass(run_dir, "r1", 2, st)
    finals = pa.read_final_labels(run_dir / "final_labels.csv")          # written by the parser
    pending = [(r["utterance_id"], r["condition"]) for r in finals if r["status"] == "tie_pending"]
    assert pending == [(1, "baseline")]
    assert [(c["utterance_id"], c["condition"]) for c in m2["calls"]] == pending
    assert m2["pass"] == 2 and m2["seed"] == 20260919 and m2["n_tie_pairs"] == 1
    assert m2["calls"] == [{"order_index": 0, "utterance_id": 1, "condition": "baseline", "repeat": 4}]
    assert m2["attempts_pass1_sha256"] == rx.sha256_file(run_dir / "attempts_pass1.jsonl")
    assert m2["final_labels_sha256"] == rx.sha256_file(run_dir / "final_labels.csv")
    assert m2["parse_attempts_git_commit"] == "abc123"
    assert m2["prompts_sha256"] == rx.sha256_file(run_dir / "prompts.jsonl")
    assert json.loads((run_dir / "manifest_pass2.json").read_text())["n_calls"] == 1
    assert (run_dir / "labels.csv").exists()

    # resume verification re-derives the tie list from attempts_pass1
    rx.verify_for_resume(run_dir, 2, m2, NO_CLI)
    (run_dir / "attempts_pass1.jsonl").open("ab").write(b'{"event": "note"}\n')
    with pytest.raises(rx.Refused, match="attempts_pass1.jsonl sha256"):
        rx.verify_for_resume(run_dir, 2, m2, NO_CLI)


def test_pass3_selects_only_pairs_still_tied_after_pass2(run_after_pass1):
    run_dir, st = run_after_pass1
    with pytest.raises(rx.Refused, match="pass 2 has not run"):
        rx.prepare_tiebreak_pass(run_dir, "r1", 3, st)                  # no pass 2 yet
    m2 = rx.prepare_tiebreak_pass(run_dir, "r1", 2, st)
    with pytest.raises(rx.Refused, match="pass 2 has not run"):
        rx.prepare_tiebreak_pass(run_dir, "r1", 3, st)                  # manifest but no attempts
    # pass 2: a fourth distinct label keeps (1, baseline) tied 1-1-1-1
    a2 = run_manifest_pass(run_dir, m2, lambda p, n: FakeRaw(ok_body("Pressing for Accuracy")))
    assert read_records(a2)[-1]["repeat"] == 4

    m3 = rx.prepare_tiebreak_pass(run_dir, "r1", 3, st)
    finals = pa.read_final_labels(run_dir / "final_labels.csv")
    assert [(r["utterance_id"], r["condition"], r["status"], r["repeats_used"]) for r in finals
            if r["condition"] == "baseline"] == [(1, "baseline", "tie_pending", 4)]
    assert m3["pass"] == 3 and m3["seed"] == 20260920 and m3["n_tie_pairs"] == 1
    assert m3["calls"] == [{"order_index": 0, "utterance_id": 1, "condition": "baseline", "repeat": 5}]
    assert m3["attempts_pass2_sha256"] == rx.sha256_file(a2)
    assert m3["final_labels_sha256"] == rx.sha256_file(run_dir / "final_labels.csv")
    assert (run_dir / "manifest_pass3.json").exists()
    rx.verify_for_resume(run_dir, 3, m3, NO_CLI)

    # pass 3 resolves it: 2-1-1-1 -> resolved; the parser reads all three attempts files
    a3 = run_manifest_pass(run_dir, m3, lambda p, n: FakeRaw(ok_body("Restating")))
    rows, finals = pa.parse_run(run_dir, "r1")
    assert {r["pass"] for r in rows} == {1, 2, 3}
    base = [r for r in finals if r["condition"] == "baseline"][0]
    assert (base["status"], base["final_label"], base["repeats_used"], base["valid_repeats"]) == \
        ("resolved", "Restating", 5, 5)
    assert pa.tie_pending_pairs(run_dir / "final_labels.csv") == []


def test_pass3_unresolved_after_five_repeats(run_after_pass1):
    run_dir, st = run_after_pass1
    m2 = rx.prepare_tiebreak_pass(run_dir, "r1", 2, st)
    run_manifest_pass(run_dir, m2, lambda p, n: FakeRaw(ok_body("Pressing for Accuracy")))
    m3 = rx.prepare_tiebreak_pass(run_dir, "r1", 3, st)
    run_manifest_pass(run_dir, m3, lambda p, n: FakeRaw(ok_body("Pressing for Reasoning")))
    _, finals = pa.parse_run(run_dir, "r1")
    base = [r for r in finals if r["condition"] == "baseline"][0]
    assert (base["status"], base["final_label"], base["repeats_used"]) == ("unresolved_tie", "", 5)


def test_pass3_not_needed_when_pass2_resolves(run_after_pass1, monkeypatch, capsys):
    run_dir, st = run_after_pass1
    m2 = rx.prepare_tiebreak_pass(run_dir, "r1", 2, st)
    run_manifest_pass(run_dir, m2, lambda p, n: FakeRaw(ok_body("Restating")))   # 2-1-1 -> resolved
    assert rx.prepare_tiebreak_pass(run_dir, "r1", 3, st) is None
    assert not (run_dir / "manifest_pass3.json").exists()
    base = [r for r in pa.read_final_labels(run_dir / "final_labels.csv") if r["condition"] == "baseline"][0]
    assert base["status"] == "resolved" and base["final_label"] == "Restating"

    # through the CLI: says so, writes nothing, exits 0, no client is built
    monkeypatch.setattr(rx, "RUNS_DIR", run_dir.parent)
    rc = rx.main(["--run-id", run_dir.name, "--pass", "3", "--concurrency", "1", "--timeout", "30",
                  "--backoff-initial", "2", "--backoff-max", "60", "--failure-threshold", "100"])
    assert rc == 0 and "pass 3 not needed" in capsys.readouterr().out
    assert not (run_dir / "manifest_pass3.json").exists() and not (run_dir / "run.lock").exists()


def test_pass2_not_needed_when_pass1_has_no_ties(tmp_path, monkeypatch):
    monkeypatch.setattr(rx, "git_commit_hash", lambda: "abc123")
    inp = tmp_path / "ids.csv"
    inp.write_text("source_id\n1\n", encoding="utf-8")
    run_dir = tmp_path / "run"; run_dir.mkdir()
    st = rx.Settings(1, 30.0, 2.0, 60.0, 100)
    rx.prepare_pass1(run_dir, "r1", inp, st, builder=fake_prompt)
    runner, _, _ = make_runner(run_dir, lambda p, n: FakeRaw(ok_body("Not coded")), ids=(1,), run_id="r1")
    runner.run()
    assert rx.prepare_tiebreak_pass(run_dir, "r1", 2, st) is None
    assert not (run_dir / "manifest_pass2.json").exists()
    assert all(r["status"] == "resolved" for r in pa.read_final_labels(run_dir / "final_labels.csv"))


def test_prepare_pass2_refuses_open_pass1_calls(tmp_path, monkeypatch):
    monkeypatch.setattr(rx, "git_commit_hash", lambda: "abc123")
    inp = tmp_path / "ids.csv"
    inp.write_text("source_id\n1\n", encoding="utf-8")
    run_dir = tmp_path / "run"; run_dir.mkdir()
    st = rx.Settings(1, 30.0, 2.0, 60.0, 1)                    # threshold 1: stop on first failure
    rx.prepare_pass1(run_dir, "r1", inp, st, builder=fake_prompt)
    runner, attempts, _ = make_runner(run_dir, lambda p, n: FakeRaw(ok_body(finish="length")),
                                      ids=(1,), failure_threshold=1)
    runner.run()
    assert read_records(attempts)[-1]["event"] == "run_stopped"
    with pytest.raises(rx.Refused, match="pass 1 not fully terminated"):
        rx.prepare_tiebreak_pass(run_dir, "r1", 2, st)
    assert not (run_dir / "final_labels.csv").exists()          # parser not run on an open pass


def test_parse_run_cli_writes_both_files(run_after_pass1, monkeypatch, capsys):
    run_dir, _ = run_after_pass1
    monkeypatch.setattr(pa, "RUNS_DIR", run_dir.parent)
    assert pa.main(["--run-id", run_dir.name, "--ties"]) == 0
    out = capsys.readouterr().out
    assert "final_labels.csv" in out and "tie_pending\t1\tbaseline" in out
    first = (run_dir / "final_labels.csv").read_bytes()
    assert pa.main(["--run-id", run_dir.name]) == 0
    assert (run_dir / "final_labels.csv").read_bytes() == first   # re-runnable, identical
