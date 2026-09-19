"""Resume computation, truncated/corrupted files, --repair, resume verification (5.6.6, 5.6.7)."""

import json

import pytest

import parse_attempts as pa
import run_experiment as rx
from tests.conftest import Clock, fake_prompt


def rec(event, idx, attempt, **kw):
    base = {"event": event, "run_id": "t", "pass": 1, "order_index": idx, "utterance_id": 1,
            "condition": "baseline", "repeat": 1, "attempt": attempt}
    base.update(kw)
    return base


def write_jsonl(path, records, trailing=b""):
    path.write_bytes(b"".join(json.dumps(r).encode() + b"\n" for r in records) + trailing)


SYNTHETIC = [
    rec("attempt_started", 0, 1, started_at="2026-09-18T00:00:00+00:00"),
    rec("attempt_completed", 0, 1, completed_seq=1, completed_at="2026-09-18T00:00:05+00:00",
        outcome="success", http_status=200),
    rec("attempt_started", 1, 1, started_at="2026-09-18T00:00:06+00:00"),
    rec("attempt_completed", 1, 1, completed_seq=2, completed_at="2026-09-18T00:00:07+00:00",
        outcome="retryable_error", planned_wait_sec=4.0, wait_source="backoff"),
    rec("attempt_started", 1, 2, started_at="2026-09-18T00:00:11+00:00"),   # interrupted
    rec("attempt_started", 2, 1, started_at="2026-09-18T00:00:12+00:00"),
    rec("attempt_completed", 2, 1, completed_seq=3, completed_at="2026-09-18T00:00:13+00:00",
        outcome="retryable_error", planned_wait_sec=None, wait_source=None),
    rec("attempt_started", 2, 2, started_at="2026-09-18T00:00:14+00:00"),
    rec("attempt_completed", 2, 2, completed_seq=4, completed_at="2026-09-18T00:00:15+00:00",
        outcome="invalid_response", planned_wait_sec=None, wait_source=None),
    rec("attempt_started", 2, 3, started_at="2026-09-18T00:00:16+00:00"),
    rec("attempt_completed", 2, 3, completed_seq=5, completed_at="2026-09-18T00:00:17+00:00",
        outcome="retryable_error", planned_wait_sec=None, wait_source=None),
]
CALLS = rx.plan_pass1([1], rx.PASS_SEEDS[1])   # 18 calls; only 0..2 appear above


def test_truncated_last_line_is_detected_then_scan_after_repair(tmp_path):
    path = tmp_path / "attempts_pass1.jsonl"
    write_jsonl(path, SYNTHETIC, trailing=b'{"event": "attempt_started", "order_in')
    with pytest.raises(pa.TruncatedLastLine) as ex:
        pa.read_jsonl_strict(path)
    assert ex.value.text.startswith(b'{"event"') and ex.value.offset == len(path.read_bytes()) - len(ex.value.text)

    assert rx.repair(tmp_path, 1, now=Clock()) == 0
    backups = list(tmp_path.glob("attempts_pass1.jsonl.bak-*"))
    assert len(backups) == 1 and backups[0].read_bytes().endswith(b'"order_in')   # backup keeps the damage
    assert path.read_bytes().endswith(b"}\n") and len(pa.read_jsonl_strict(path)) == len(SYNTHETIC)
    log = [json.loads(l) for l in (tmp_path / "recovery_log.jsonl").read_text().splitlines()]
    assert len(log) == 1 and log[0]["bytes_removed"] == len(b'{"event": "attempt_started", "order_in')
    assert log[0]["removed_text"] == '{"event": "attempt_started", "order_in'
    assert log[0]["file"] == "attempts_pass1.jsonl" and log[0]["backup"] == backups[0].name

    states, seq = rx.scan_attempts(pa.read_jsonl_strict(path), CALLS)
    assert seq == 5
    assert states[0].terminated and states[0].has_success and states[0].next_attempt == 2
    # call 1: attempt 2 interrupted -> next attempt 3, no prev completed, last completed carries wait
    assert (states[1].terminated, states[1].next_attempt, states[1].prev_completed_at) == (False, 3, None)
    assert states[1].last_completed["planned_wait_sec"] == 4.0
    # call 2: three attempts exhausted without success -> terminated
    assert states[2].terminated and not states[2].has_success and states[2].next_attempt == 4
    assert states[2].prev_completed_at == "2026-09-18T00:00:17+00:00"
    assert not states[3].terminated and states[3].next_attempt == 1 and states[3].last_completed is None


def test_interrupted_third_attempt_counts_as_exhausted(tmp_path):
    records = SYNTHETIC[:5] + [rec("attempt_started", 1, 3, started_at="2026-09-18T00:01:00+00:00")]
    states, _ = rx.scan_attempts(records, CALLS)
    assert states[1].terminated and states[1].next_attempt == 4 and not states[1].has_success


def test_corrupted_middle_line_is_refused(tmp_path):
    path = tmp_path / "attempts_pass1.jsonl"
    lines = [json.dumps(r) for r in SYNTHETIC]
    lines[3] = lines[3][:20]                                   # damage a non-final record
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(pa.CorruptedFile):
        pa.read_jsonl_strict(path)
    assert rx.repair(tmp_path, 1) == 2                         # repair refuses too
    assert not list(tmp_path.glob("*.bak-*")) and not (tmp_path / "recovery_log.jsonl").exists()
    assert path.read_text(encoding="utf-8") == "\n".join(lines) + "\n"   # untouched


def test_repair_is_noop_on_intact_file(tmp_path):
    path = tmp_path / "attempts_pass1.jsonl"
    write_jsonl(path, SYNTHETIC)
    before = path.read_bytes()
    assert rx.repair(tmp_path, 1) == 0
    assert path.read_bytes() == before and not list(tmp_path.glob("*.bak-*"))


def test_empty_file_and_trailing_newline_only(tmp_path):
    path = tmp_path / "a.jsonl"
    path.write_bytes(b"")
    assert pa.read_jsonl_strict(path) == []
    write_jsonl(path, SYNTHETIC[:2])
    assert len(pa.read_jsonl_strict(path)) == 2


@pytest.fixture
def prepared_run(tmp_path, monkeypatch):
    monkeypatch.setattr(rx, "git_commit_hash", lambda: "abc123")
    inp = tmp_path / "ids.csv"
    inp.write_text("source_id\n1\n2\n", encoding="utf-8")
    run_dir = tmp_path / "run"; run_dir.mkdir()
    manifest = rx.prepare_pass1(run_dir, "r1", inp, rx.Settings(4, 30.0, 2.0, 60.0, 10), builder=fake_prompt)
    return run_dir, inp, manifest


def test_resume_verification_passes_on_intact_run(prepared_run):
    run_dir, _, manifest = prepared_run
    prompts = rx.verify_for_resume(run_dir, 1, manifest, {"concurrency": 4, "timeout": None,
                                                          "backoff_initial": None, "backoff_max": None,
                                                          "failure_threshold": None})
    assert len(prompts) == 12


def refusal_message(run_dir, manifest, cli=None):
    cli = cli or {"concurrency": None, "timeout": None, "backoff_initial": None,
                  "backoff_max": None, "failure_threshold": None}
    with pytest.raises(rx.Refused) as ex:
        rx.verify_for_resume(run_dir, 1, manifest, cli)
    return str(ex.value)


def test_resume_refuses_dirty_tree(prepared_run, monkeypatch):
    run_dir, _, manifest = prepared_run
    monkeypatch.setattr(rx, "git_commit_hash", lambda: "abc123-dirty")
    assert "working tree is dirty" in refusal_message(run_dir, manifest)


def test_resume_refuses_other_commit(prepared_run, monkeypatch):
    run_dir, _, manifest = prepared_run
    monkeypatch.setattr(rx, "git_commit_hash", lambda: "def456")
    assert "git commit def456 != manifest abc123" in refusal_message(run_dir, manifest)


def test_resume_refuses_manifest_mismatches(prepared_run):
    run_dir, inp, manifest = prepared_run
    m = json.loads(json.dumps(manifest))
    m["model"] = "gpt-other"
    m["request_params"]["temperature"] = 1
    m["seed"] = 1
    m["calls"][0], m["calls"][1] = m["calls"][1], m["calls"][0]
    msg = refusal_message(run_dir, m)
    for text in ("model gpt-other", "request_params differ", "seed 1 !=", "ordered call list differs"):
        assert text in msg


def test_resume_refuses_changed_input_prompts_and_settings(prepared_run):
    run_dir, inp, manifest = prepared_run
    inp.write_text("source_id\n1\n2\n3\n", encoding="utf-8")
    assert "input file sha256 differs" in refusal_message(run_dir, manifest)
    inp.write_text("source_id\n1\n2\n", encoding="utf-8")

    p = run_dir / "prompts.jsonl"
    lines = p.read_text(encoding="utf-8").splitlines()
    p.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")   # drop one pair
    msg = refusal_message(run_dir, manifest)
    assert "prompts.jsonl sha256 differs" in msg and "set differs" in msg

    rx.write_prompts(p, [(u, c) for u in (1, 2) for c in rx.CONDITIONS], fake_prompt)
    msg = refusal_message(run_dir, manifest, {"concurrency": 8, "timeout": None, "backoff_initial": None,
                                              "backoff_max": 30.0, "failure_threshold": None})
    assert "--concurrency 8 != manifest 4" in msg and "--backoff-max 30.0 != manifest 60.0" in msg


def test_lock_refuses_second_process(tmp_path):
    lock = rx.acquire_lock(tmp_path)
    assert lock.exists()
    with pytest.raises(rx.Refused):
        rx.acquire_lock(tmp_path)
    lock.unlink()
    rx.acquire_lock(tmp_path).unlink()
