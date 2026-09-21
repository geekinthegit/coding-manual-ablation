"""scorer.require_run_complete: the entry checks of 6.1.1 on synthetic runs (no API calls).

Runs are built with the real pass 1 planner (prepare_pass1), the real Runner
with a fake client, and the real parser, so the attempt records have exactly
the shape the experiment produces.
"""

import json

import pytest

import parse_attempts as pa
import run_experiment as rx
import scorer
from tests.conftest import FakeRaw, fake_prompt, make_runner, ok_body, read_records, status_error

RUN_ID = "r1"
SETTINGS = rx.Settings(1, 30.0, 2.0, 60.0, 100)


def prepare_run(tmp_path, monkeypatch, ids=(1, 2)):
    """A run directory with prompts.jsonl and manifest_pass1.json for `ids` (nothing executed)."""
    monkeypatch.setattr(rx, "git_commit_hash", lambda: "abc123")
    inp = tmp_path / "ids.csv"
    inp.write_text("source_id\n" + "".join(f"{i}\n" for i in ids), encoding="utf-8")
    run_dir = tmp_path / RUN_ID
    run_dir.mkdir()
    rx.prepare_pass1(run_dir, RUN_ID, inp, SETTINGS, builder=fake_prompt)
    return run_dir


def always(category):
    return lambda prompt, n: FakeRaw(ok_body(category))


def fail_third_repeat_of(target_prompt):
    """Raise a retryable 500 on the third call for `target_prompt` (its repeat 3, block order 1 -> 2 -> 3)."""
    def handler(prompt, n):
        if prompt == target_prompt and n == 2:
            raise status_error(500)
        return FakeRaw(ok_body("Not coded"))
    return handler


def run_pass1(run_dir, handler, records=None, **over):
    runner, attempts, _ = make_runner(run_dir, handler, calls=json.loads(
        (run_dir / "manifest_pass1.json").read_text())["calls"], run_id=RUN_ID, records=records, **over)
    runner.run()
    return attempts


def final_status(run_dir, uid, cond):
    rows = pa.read_final_labels(run_dir / "final_labels.csv")
    return [r["status"] for r in rows if (r["utterance_id"], r["condition"]) == (uid, cond)]


def test_terminated_pass1_with_current_final_labels_passes(tmp_path, monkeypatch):
    run_dir = prepare_run(tmp_path, monkeypatch)
    run_pass1(run_dir, always("Not coded"))
    pa.parse_run(run_dir, RUN_ID)
    assert scorer.require_run_complete(run_dir) is None


def test_open_repeat3_looks_resolved_in_final_labels_but_is_refused(tmp_path, monkeypatch):
    run_dir = prepare_run(tmp_path, monkeypatch)
    # failure_threshold=1: the first retryable error stops the run, leaving repeat 3 of
    # (1, baseline) with one failed attempt and no further attempt (not terminated).
    run_pass1(run_dir, fail_third_repeat_of(fake_prompt(1, "baseline")), failure_threshold=1)
    pa.parse_run(run_dir, RUN_ID)
    assert final_status(run_dir, 1, "baseline") == ["resolved"]        # 2 valid repeats agree
    with pytest.raises(rx.Refused, match="pass 1 not fully terminated"):
        scorer.require_run_complete(run_dir)


def test_tie_pending_row_is_refused_even_when_all_calls_terminated(tmp_path, monkeypatch):
    run_dir = prepare_run(tmp_path, monkeypatch, ids=(1,))
    answers = iter(["Restating", "Revoicing", "Not coded"])

    def handler(prompt, n):
        if prompt == fake_prompt(1, "baseline"):
            return FakeRaw(ok_body(next(answers)))
        return FakeRaw(ok_body("Not coded"))

    run_pass1(run_dir, handler)
    pa.parse_run(run_dir, RUN_ID)
    assert final_status(run_dir, 1, "baseline") == ["tie_pending"]
    rx.require_pass_terminated(run_dir, 1)                              # check A alone passes
    with pytest.raises(rx.Refused, match="check B .*tie_pending"):
        scorer.require_run_complete(run_dir)


def test_stale_final_labels_refused_until_parser_rerun(tmp_path, monkeypatch):
    run_dir = prepare_run(tmp_path, monkeypatch)
    attempts = run_pass1(run_dir, fail_third_repeat_of(fake_prompt(1, "baseline")), failure_threshold=1)
    pa.parse_run(run_dir, RUN_ID)                                       # parsed while calls are open
    stale = (run_dir / "final_labels.csv").read_bytes()
    run_pass1(run_dir, always("Not coded"), records=read_records(attempts))   # resume: terminate the rest
    rx.require_pass_terminated(run_dir, 1)
    assert (run_dir / "final_labels.csv").read_bytes() == stale         # parser not rerun
    with pytest.raises(rx.Refused, match="check C .*differs"):
        scorer.require_run_complete(run_dir)
    pa.parse_run(run_dir, RUN_ID)
    assert scorer.require_run_complete(run_dir) is None


def test_pass2_manifest_without_attempts_or_attempts_without_manifest_refused(tmp_path, monkeypatch):
    run_dir = prepare_run(tmp_path, monkeypatch)
    run_pass1(run_dir, always("Not coded"))
    pa.parse_run(run_dir, RUN_ID)
    assert scorer.require_run_complete(run_dir) is None
    m2 = run_dir / "manifest_pass2.json"
    m2.write_text('{"pass": 2, "calls": []}\n', encoding="utf-8")       # manifest only
    with pytest.raises(rx.Refused, match="pass 2 has not run"):
        scorer.require_run_complete(run_dir)
    m2.unlink()
    (run_dir / "attempts_pass2.jsonl").write_bytes(b"")                # attempts only
    with pytest.raises(rx.Refused, match="pass 2 has not run"):
        scorer.require_run_complete(run_dir)


def test_pass1_and_pass3_without_pass2_refused(tmp_path, monkeypatch):
    run_dir = prepare_run(tmp_path, monkeypatch)
    run_pass1(run_dir, always("Not coded"))
    pa.parse_run(run_dir, RUN_ID)
    (run_dir / "attempts_pass3.jsonl").write_bytes(b"")
    with pytest.raises(rx.Refused, match=r"check 0 .*\[1, 3\] are not contiguous"):
        scorer.require_run_complete(run_dir)


def test_missing_final_labels_file_refused(tmp_path, monkeypatch):
    run_dir = prepare_run(tmp_path, monkeypatch)
    run_pass1(run_dir, always("Not coded"))
    with pytest.raises(rx.Refused, match="check C .*does not exist"):
        scorer.require_run_complete(run_dir)


def test_pair_terminated_by_interrupted_attempts_has_no_row_and_is_refused(tmp_path, monkeypatch):
    """Check B: 3 interrupted attempts terminate a call (5.6.6) but leave no attempt_completed record."""
    run_dir = prepare_run(tmp_path, monkeypatch)
    calls = json.loads((run_dir / "manifest_pass1.json").read_text())["calls"]
    target = [c for c in calls if (c["utterance_id"], c["condition"]) == (2, "baseline")]
    assert len(target) == 3
    started = [{"event": "attempt_started", "run_id": RUN_ID, "pass": 1, "order_index": c["order_index"],
                "utterance_id": 2, "condition": "baseline", "repeat": c["repeat"], "attempt": a,
                "started_at": "2026-09-18T00:00:00+00:00"} for c in target for a in (1, 2, 3)]
    attempts = run_dir / "attempts_pass1.jsonl"
    attempts.write_bytes(b"".join(json.dumps(r).encode() + b"\n" for r in started))
    run_pass1(run_dir, always("Not coded"), records=started)            # remaining calls terminate normally
    pa.parse_run(run_dir, RUN_ID)
    assert final_status(run_dir, 2, "baseline") == []
    rx.require_pass_terminated(run_dir, 1)                              # check A passes
    with pytest.raises(rx.Refused, match=r"check B .*without a final_labels.csv row: \[\(2, 'baseline'\)\]"):
        scorer.require_run_complete(run_dir)
