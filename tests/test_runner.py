"""Runner behaviour (5.6.4, 5.6.5, 5.6.7) with a fake client; no network."""

import threading
import time

import run_experiment as rx
from tests.conftest import (
    Clock, FakeRaw, connection_error, make_runner, ok_body, read_records, status_error,
)


def by_event(records, event):
    return [r for r in records if r["event"] == event]


def test_success_path_records_both_events_and_fields(tmp_path):
    runner, path, client = make_runner(tmp_path, lambda p, n: FakeRaw(ok_body("Restating")))
    summary = runner.run()
    recs = read_records(path)
    assert summary["stopped"] is None and summary["terminated"] == summary["total"] == 18
    started, completed = by_event(recs, "attempt_started"), by_event(recs, "attempt_completed")
    assert len(started) == len(completed) == 18
    s, c = started[0], completed[0]
    assert s["attempt"] == 1 and s["actual_wait_sec"] is None and s["request_params"]["model"] == rx.MODEL
    assert s["prompt_sha256"] == runner.prompts[(s["utterance_id"], s["condition"])][1]
    assert c["outcome"] == "success" and c["invalid_reason"] is None and c["http_status"] == 200
    assert c["openai_request_id"] == "req_ok" and c["raw_response"] == ok_body("Restating")
    assert c["finish_reason"] == "stop" and c["response_model"] == rx.MODEL
    assert c["planned_wait_sec"] is None and c["wait_source"] is None
    assert [r["completed_seq"] for r in completed] == list(range(1, 19))
    # every request went through the 5.3 request path
    assert all(r["response_format"]["json_schema"]["name"] == "talkmove_category" for r in client.requests)
    assert all(r["temperature"] == 0 and r["reasoning_effort"] == "none" for r in client.requests)


def test_block_boundary_no_next_block_call_while_retry_pending(tmp_path):
    calls = rx.plan_pass1([1, 2], rx.PASS_SEEDS[1])
    last_block1 = calls[len(calls) // 3 - 1]            # last scheduled call of repeat 1
    target = f"PROMPT uid={last_block1['utterance_id']} cond={last_block1['condition']}"

    def handler(prompt, n):
        if prompt == target and n < 2:                 # first two attempts of that pair fail
            raise status_error(500)
        return FakeRaw(ok_body())

    sleeps = []
    runner, path, _ = make_runner(tmp_path, handler, ids=(1, 2), concurrency=3,
                                  sleeps=sleeps, backoff_initial=0.01, backoff_max=0.02)
    runner.sleep = lambda s: time.sleep(0.03)          # make the retry window real
    runner.run()
    recs = read_records(path)
    pos_last_b1_completed = max(i for i, r in enumerate(recs)
                                if r["event"] == "attempt_completed" and r["repeat"] == 1)
    pos_first_b2_started = min(i for i, r in enumerate(recs)
                               if r["event"] == "attempt_started" and r["repeat"] == 2)
    assert pos_last_b1_completed < pos_first_b2_started
    retried = [r for r in recs if r["event"] == "attempt_completed" and r["repeat"] == 1
               and r["order_index"] == last_block1["order_index"]]
    assert [r["outcome"] for r in retried] == ["retryable_error", "retryable_error", "success"]
    assert retried[0]["wait_source"] == "backoff" and 0.005 <= retried[0]["planned_wait_sec"] <= 0.01


def test_retry_after_within_max_is_honoured(tmp_path):
    def handler(prompt, n):
        if n == 0:
            raise status_error(429, code="rate_limit_exceeded", retry_after="5")
        return FakeRaw(ok_body())
    sleeps = []
    runner, path, _ = make_runner(tmp_path, handler, sleeps=sleeps)
    runner.run()
    first = by_event(read_records(path), "attempt_completed")[0]
    assert first["outcome"] == "retryable_error" and first["http_status"] == 429
    assert first["openai_error_code"] == "rate_limit_exceeded"
    assert first["planned_wait_sec"] == 5.0 and first["wait_source"] == "retry_after"
    assert first["error"]["retry_after"] == "5" and first["openai_request_id"] == "req_err"
    assert sleeps[0] == 5.0


def test_retry_after_exceeding_backoff_max_stops_run(tmp_path):
    def handler(prompt, n):
        raise status_error(429, code="rate_limit_exceeded", retry_after="120")
    sleeps = []
    runner, path, _ = make_runner(tmp_path, handler, sleeps=sleeps, backoff_max=60.0)
    summary = runner.run()
    recs = read_records(path)
    completed = by_event(recs, "attempt_completed")
    assert len(by_event(recs, "attempt_started")) == 1 and len(completed) == 1
    assert completed[0]["outcome"] == "retryable_error"
    assert completed[0]["planned_wait_sec"] == 120.0 and completed[0]["wait_source"] == "retry_after"
    assert sleeps == []                                     # not clipped, not slept
    stopped = recs[-1]
    assert stopped["event"] == "run_stopped" and stopped["reason"] == "retry_after_exceeds_max"
    assert stopped["completed_seq_at_stop"] == 1
    assert stopped["triggering"] == {"order_index": completed[0]["order_index"], "attempt": 1}
    assert summary["stopped"]["reason"] == "retry_after_exceeds_max"


def test_429_quota_code_is_fatal_and_stops(tmp_path):
    def handler(prompt, n):
        raise status_error(429, code="insufficient_quota")
    runner, path, _ = make_runner(tmp_path, handler)
    runner.run()
    recs = read_records(path)
    c = by_event(recs, "attempt_completed")[0]
    assert c["outcome"] == "fatal_error" and c["openai_error_code"] == "insufficient_quota"
    assert recs[-1]["event"] == "run_stopped" and recs[-1]["reason"] == "fatal_error"


def test_non_429_4xx_is_fatal(tmp_path):
    runner, path, _ = make_runner(tmp_path, lambda p, n: (_ for _ in ()).throw(status_error(401)))
    runner.run()
    recs = read_records(path)
    assert by_event(recs, "attempt_completed")[0]["outcome"] == "fatal_error"
    assert recs[-1]["reason"] == "fatal_error"


def test_timeout_is_retryable_with_backoff_then_exhausts(tmp_path):
    runner, path, _ = make_runner(tmp_path, lambda p, n: (_ for _ in ()).throw(connection_error()),
                                  ids=(1,), backoff_initial=2.0, backoff_max=60.0)
    # restrict to one call: mark all others terminated
    for idx, st in runner.states.items():
        if idx != 0:
            st.terminated = True
    runner.remaining = [0]
    runner.run()
    completed = by_event(read_records(path), "attempt_completed")
    assert [c["attempt"] for c in completed] == [1, 2, 3]
    assert all(c["outcome"] == "retryable_error" and c["http_status"] is None for c in completed)
    assert completed[0]["error"]["type"] == "APITimeoutError"
    assert 1.0 <= completed[0]["planned_wait_sec"] <= 2.0        # base 2, equal jitter
    assert 2.0 <= completed[1]["planned_wait_sec"] <= 4.0        # base 4
    assert completed[2]["planned_wait_sec"] is None              # no retry follows attempt 3
    assert runner.states[0].terminated and not runner.states[0].has_success


def test_invalid_response_is_retried_and_counted(tmp_path):
    def handler(prompt, n):
        return FakeRaw(ok_body(category="revoicing") if n == 0 else ok_body("Revoicing"))
    runner, path, _ = make_runner(tmp_path, handler)
    runner.run()
    completed = by_event(read_records(path), "attempt_completed")
    assert completed[0]["outcome"] == "invalid_response"
    assert completed[0]["invalid_reason"] == "label_not_in_enum"
    assert completed[0]["wait_source"] == "backoff"
    assert completed[1]["outcome"] == "success" and completed[1]["attempt"] == 2


def test_failure_threshold_counts_in_seq_order_and_resets_on_success(tmp_path):
    # call 0: fail, success (counter 1 -> 0); call 1: fail x3 (counter 3 -> stop at threshold 3)
    calls = rx.plan_pass1([1], rx.PASS_SEEDS[1])
    p0 = f"PROMPT uid=1 cond={calls[0]['condition']}"
    p1 = f"PROMPT uid=1 cond={calls[1]['condition']}"

    def handler(prompt, n):
        if prompt == p0 and n == 0:
            raise status_error(500)
        if prompt == p1:
            raise status_error(503)
        return FakeRaw(ok_body())

    runner, path, _ = make_runner(tmp_path, handler, failure_threshold=3)
    runner.run()
    recs = read_records(path)
    outcomes = [(r["order_index"], r["attempt"], r["outcome"]) for r in by_event(recs, "attempt_completed")]
    assert outcomes == [(0, 1, "retryable_error"), (0, 2, "success"),
                        (1, 1, "retryable_error"), (1, 2, "retryable_error"), (1, 3, "retryable_error")]
    stopped = recs[-1]
    assert stopped["event"] == "run_stopped" and stopped["reason"] == "failure_threshold"
    assert stopped["completed_seq_at_stop"] == 5 and stopped["triggering"] == {"order_index": 1, "attempt": 3}
    assert len(by_event(recs, "attempt_started")) == 5          # call 2 onward never started


def test_stop_state_is_sticky_and_blocks_new_attempts(tmp_path):
    runner, path, _ = make_runner(tmp_path, lambda p, n: FakeRaw(ok_body()), failure_threshold=1)
    fail = {"event": "attempt_completed", "run_id": "t", "pass": 1, "order_index": 0, "utterance_id": 1,
            "condition": "baseline", "repeat": 1, "attempt": 1, "outcome": "retryable_error"}
    runner.record_completed(dict(fail))
    assert runner.stopped and runner.stop_info["reason"] == "failure_threshold"
    late = dict(fail, attempt=2, outcome="success")
    runner.record_completed(late)                                # late success is recorded ...
    assert runner.stopped and runner.stop_info["completed_seq_at_stop"] == 1   # ... but does not revert
    assert runner.begin_attempt({"event": "attempt_started"}) is False
    assert runner.next_call() is None
    runner.fh.close()
    assert [r["event"] for r in read_records(path)] == ["attempt_completed", "attempt_completed"]


def test_actual_wait_sec_null_on_first_attempt_and_after_interruption(tmp_path):
    calls = rx.plan_pass1([1], rx.PASS_SEEDS[1])
    t0 = "2026-09-18T00:00:00+00:00"
    records = [  # call 0: attempt 1 completed (planned wait 30s), attempt 2 interrupted
        {"event": "attempt_started", "order_index": 0, "attempt": 1, "started_at": t0},
        {"event": "attempt_completed", "order_index": 0, "attempt": 1, "completed_seq": 1,
         "completed_at": "2026-09-18T00:00:10+00:00", "outcome": "retryable_error",
         "planned_wait_sec": 30.0, "wait_source": "backoff"},
        {"event": "attempt_started", "order_index": 0, "attempt": 2, "started_at": "2026-09-18T00:00:20+00:00"},
    ]
    sleeps = []
    clock = Clock(start="2026-09-18T00:00:25+00:00")
    runner, path, _ = make_runner(tmp_path, lambda p, n: FakeRaw(ok_body()), records=records,
                                  sleeps=sleeps, clock=clock)
    for idx, st in runner.states.items():
        if idx != 0:
            st.terminated = True
    runner.remaining = [0]
    runner.run()
    recs = read_records(path)
    started = by_event(recs, "attempt_started")
    assert started[0]["attempt"] == 3                            # interrupted attempt 2 consumed
    assert started[0]["actual_wait_sec"] is None                 # previous attempt has no completed record
    # remaining wait honoured: completed_at 00:00:10 + 30 s = 00:00:40; clock at 00:00:26 -> 14 s
    assert sleeps and abs(sleeps[0] - 14.0) < 1e-6
    assert by_event(recs, "attempt_completed")[-1]["completed_seq"] == 2   # continues numbering


def test_actual_wait_sec_measured_between_attempts(tmp_path):
    def handler(prompt, n):
        if n == 0:
            raise status_error(500)
        return FakeRaw(ok_body())
    runner, path, _ = make_runner(tmp_path, handler, clock=Clock(step=1.0))
    runner.run()
    started = by_event(read_records(path), "attempt_started")
    first = [s for s in started if s["order_index"] == 0]
    assert first[0]["actual_wait_sec"] is None
    assert first[1]["attempt"] == 2 and first[1]["actual_wait_sec"] == 1.0   # one clock tick after completed_at


def test_records_are_fsynced_under_lock(tmp_path, monkeypatch):
    fsyncs = []
    monkeypatch.setattr(rx.os, "fsync", lambda fd: fsyncs.append(fd))
    runner, path, _ = make_runner(tmp_path, lambda p, n: FakeRaw(ok_body()))
    seen_locked = []
    original = runner._append

    def spy(rec):
        seen_locked.append(runner.lock.locked())
        original(rec)
    runner._append = spy
    runner.run()
    assert len(fsyncs) == 36 and all(seen_locked)           # 18 started + 18 completed, all under lock
