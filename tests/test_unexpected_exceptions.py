"""Unexpected exceptions during an attempt (5.6.5, 5.6.7, 5.6.8; added 2026-09-21). No API calls.

Two paths are covered: an exception that execute() turns into a fatal_error
record, and an exception that escapes process_call so that no attempt_completed
exists and the worker itself stops the run.
"""

import pytest

import parse_attempts as pa
import run_experiment as rx
from tests.conftest import FakeRaw, make_runner, ok_body, read_records


def by_event(records, event):
    return [r for r in records if r.get("event") == event]


def raise_runtime(prompt, n):
    raise RuntimeError("synthetic failure inside the client")


def test_client_exception_is_recorded_as_fatal_error_and_stops_run(tmp_path):
    runner, path, _ = make_runner(tmp_path, raise_runtime, ids=(1,))
    summary = runner.run()
    recs = read_records(path)
    started, completed = by_event(recs, "attempt_started"), by_event(recs, "attempt_completed")
    assert len(started) == 1 and len(completed) == 1
    c = completed[0]
    assert c["outcome"] == "fatal_error" and c["invalid_reason"] is None
    assert c["error"] == {"type": "RuntimeError", "message": "synthetic failure inside the client",
                          "retry_after": None}
    assert c["http_status"] is None and c["raw_response"] is None and c["openai_request_id"] is None
    assert c["openai_error_code"] is None and c["openai_error_type"] is None
    assert recs[-1]["event"] == "run_stopped" and recs[-1]["reason"] == "fatal_error"
    assert recs[-1]["triggering"] == {"order_index": started[0]["order_index"], "attempt": 1}
    assert [r["event"] for r in recs] == ["attempt_started", "attempt_completed", "run_stopped"]
    assert summary["stopped"]["reason"] == "fatal_error" and summary["terminated"] == 0


def run_with_validation_exception(tmp_path):
    """A run whose first attempt receives a 200 body and then fails inside validate_body."""
    body = ok_body("Restating")
    with pytest.MonkeyPatch.context() as mp:
        def boom(text):
            raise ValueError("validation exploded")
        mp.setattr(rx, "validate_body", boom)
        runner, path, _ = make_runner(tmp_path, lambda p, n: FakeRaw(body, request_id="req_v"), ids=(1,))
        runner.run()
    return path, body


def test_exception_after_response_keeps_body_and_status(tmp_path):
    path, body = run_with_validation_exception(tmp_path)
    recs = read_records(path)
    c = by_event(recs, "attempt_completed")[0]
    assert c["outcome"] == "fatal_error"
    assert c["error"]["type"] == "ValueError" and c["error"]["message"] == "validation exploded"
    assert c["http_status"] == 200 and c["raw_response"] == body and c["openai_request_id"] == "req_v"
    assert recs[-1]["event"] == "run_stopped" and recs[-1]["reason"] == "fatal_error"


def test_parser_does_not_rederive_fatal_error_record_with_200_body(tmp_path):
    path, body = run_with_validation_exception(tmp_path)
    recs = read_records(path)
    rows = pa.labels_from_records(recs)                      # would raise if re-derived: body says success
    assert len(rows) == 1
    assert rows[0]["category"] == "" and rows[0]["valid"] is False
    (pair, res), = pa.aggregate(rows).items()
    assert res["status"] == "insufficient_valid_repeats" and res["valid_repeats"] == 0
    assert res["repeats_used"] == 1 and res["final_label"] is None
    # the other outcomes keep their re-derivation and refusal rules
    fake_success = dict(recs[1], outcome="success", http_status=None, raw_response=None)
    with pytest.raises(ValueError, match="without an HTTP 200 body"):
        pa.labels_from_records([fake_success])


def test_resume_continues_with_next_attempt_and_aggregates_normally(tmp_path):
    path, _ = run_with_validation_exception(tmp_path)
    first = read_records(path)
    idx = by_event(first, "attempt_started")[0]["order_index"]
    runner, path2, _ = make_runner(tmp_path, lambda p, n: FakeRaw(ok_body("Restating")), ids=(1,),
                                   records=first)
    assert path2 == path
    assert runner.states[idx].next_attempt == 2 and not runner.states[idx].terminated
    summary = runner.run()
    assert summary["stopped"] is None and summary["terminated"] == summary["total"] == 18
    recs = read_records(path)
    attempts_of_idx = [(r["attempt"], r["outcome"]) for r in by_event(recs, "attempt_completed")
                       if r["order_index"] == idx]
    assert attempts_of_idx == [(1, "fatal_error"), (2, "success")]
    rows = pa.labels_from_records(recs)
    call = runner.calls[idx]
    res = pa.aggregate(rows)[(call["utterance_id"], call["condition"])]
    assert res["status"] == "resolved" and res["final_label"] == "Restating" and res["valid_repeats"] == 3


def test_unwritable_completed_record_stops_run_without_new_attempts(tmp_path, capsys):
    runner, path, _ = make_runner(tmp_path, lambda p, n: FakeRaw(ok_body()), ids=(1,))

    def unwritable(rec, stop_reason=None):
        raise OSError("disk full")
    runner.record_completed = unwritable
    summary = runner.run()
    assert runner.stopped and runner.stop_info["reason"] == "fatal_error"
    recs = read_records(path)
    started = by_event(recs, "attempt_started")
    assert len(started) == 1 and by_event(recs, "attempt_completed") == []
    assert runner.stop_info["completed_seq_at_stop"] == 0
    assert runner.stop_info["triggering"] == {"order_index": started[0]["order_index"], "attempt": 1}
    assert recs[-1]["event"] == "run_stopped" and recs[-1]["reason"] == "fatal_error"
    assert summary["stopped"]["reason"] == "fatal_error" and summary["terminated"] == 0
    err = capsys.readouterr().err
    assert "OSError" in err and "disk full" in err
    # the interrupted attempt is consumed on resume (5.6.6): next attempt is 2
    states, seq = rx.scan_attempts(recs, list(runner.calls.values()))
    assert states[started[0]["order_index"]].next_attempt == 2 and seq == 0


def test_failed_run_stopped_write_is_reported_not_buried(tmp_path, capsys):
    runner, path, _ = make_runner(tmp_path, raise_runtime, ids=(1,))
    original_append = runner._append

    def append_but_not_run_stopped(rec):
        if rec.get("event") == "run_stopped":
            raise OSError("cannot append run_stopped")
        original_append(rec)
    runner._append = append_but_not_run_stopped
    summary = runner.run()
    assert summary["stopped"]["reason"] == "fatal_error" and summary["stopped"]["written"] is False
    assert "cannot append run_stopped" in capsys.readouterr().err
    assert [r["event"] for r in read_records(path)] == ["attempt_started", "attempt_completed"]
