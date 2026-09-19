"""5.6.1 block shuffle, 5.6.3 prompt determinism, manifest/prompts preparation."""

import json

import pytest

import run_experiment as rx
from build_inputs import CONDITIONS, FRAME_FILE, MANUAL_FILES, ROWS_ALL_FILE
from tests.conftest import fake_prompt


def test_plan_pass1_blocks_and_reproducibility():
    ids = [5, 9, 12]
    calls = rx.plan_pass1(ids, 20260918)
    n_pairs = len(ids) * len(CONDITIONS)
    assert len(calls) == 3 * n_pairs
    assert [c["order_index"] for c in calls] == list(range(len(calls)))
    # block order fixed 1 -> 2 -> 3, each block holds every pair exactly once
    for r in (1, 2, 3):
        block = [c for c in calls if c["repeat"] == r]
        assert [c["order_index"] for c in block] == list(range((r - 1) * n_pairs, r * n_pairs))
        assert sorted((c["utterance_id"], c["condition"]) for c in block) == \
            sorted((u, c) for u in ids for c in CONDITIONS)
    assert rx.plan_pass1(ids, 20260918) == calls                # same seed, same list
    assert rx.plan_pass1(ids, 20260919) != calls                # different seed, different order
    within = [(c["utterance_id"], c["condition"]) for c in calls if c["repeat"] == 1]
    assert within != sorted(within)                             # actually shuffled


def test_plan_tiebreak_single_block_per_pass():
    pairs = [(3, "baseline"), (1, "names_only"), (2, "baseline")]
    assert rx.PASS_SEEDS == {1: 20260918, 2: 20260919, 3: 20260920}
    p2, p3 = rx.plan_tiebreak(pairs, 2), rx.plan_tiebreak(pairs, 3)
    assert {c["repeat"] for c in p2} == {4} and {c["repeat"] for c in p3} == {5}
    for calls in (p2, p3):
        assert sorted((c["utterance_id"], c["condition"]) for c in calls) == sorted(pairs)
        assert [c["order_index"] for c in calls] == [0, 1, 2]
    assert rx.plan_tiebreak(list(reversed(pairs)), 2) == p2          # input order irrelevant
    assert [(c["utterance_id"], c["condition"]) for c in p2] != \
        [(c["utterance_id"], c["condition"]) for c in p3]             # different seeds, different order


def test_write_prompts_is_byte_identical(tmp_path):
    pairs = [(2, "baseline"), (1, "names_only"), (1, "baseline")]
    a, b = tmp_path / "a.jsonl", tmp_path / "b.jsonl"
    out1 = rx.write_prompts(a, pairs, fake_prompt)
    out2 = rx.write_prompts(b, pairs, fake_prompt)
    assert a.read_bytes() == b.read_bytes() and out1 == out2
    loaded = rx.load_prompts(a)
    assert loaded == out1 and len(loaded) == 3
    # a tampered prompt body is detected by the recomputed sha256
    lines = a.read_text(encoding="utf-8").splitlines()
    rec = json.loads(lines[0]); rec["prompt"] += " "
    a.write_text("\n".join([json.dumps(rec), *lines[1:]]) + "\n", encoding="utf-8")
    with pytest.raises(rx.Refused):
        rx.load_prompts(a)


needs_data = pytest.mark.skipif(
    not (FRAME_FILE.exists() and ROWS_ALL_FILE.exists() and all(p.exists() for p in MANUAL_FILES.values())),
    reason="derived data/ and manual/ files not present",
)


@needs_data
def test_real_build_prompt_is_deterministic():
    from build_inputs import build_prompt
    for cond in CONDITIONS:
        first, second = build_prompt(7, cond), build_prompt(7, cond)
        assert first == second and first
        assert rx.sha256_text(first) == rx.sha256_text(second)


def test_prepare_pass1_writes_manifest_and_prompts(tmp_path, monkeypatch):
    monkeypatch.setattr(rx, "git_commit_hash", lambda: "abc123")
    inp = tmp_path / "ids.csv"
    inp.write_text("source_id\n3\n1\n", encoding="utf-8")
    run_dir = tmp_path / "run"; run_dir.mkdir()
    m = rx.prepare_pass1(run_dir, "r1", inp, rx.Settings(4, 30.0, 2.0, 60.0, 10), builder=fake_prompt)
    assert m["seed"] == 20260918 and m["n_calls"] == 2 * 6 * 3 and m["git_commit"] == "abc123"
    assert m["calls"] == rx.plan_pass1([3, 1], 20260918)
    assert m["request_params"]["model"] == rx.MODEL and "messages" not in m["request_params"]
    assert m["sdk_settings"] == {"max_retries": 0, "timeout": 30.0}
    assert m["prompts_sha256"] == rx.sha256_file(run_dir / "prompts.jsonl")
    assert m["input_file"]["sha256"] == rx.sha256_file(inp)
    assert rx.manifest_pairs(m) == set(rx.load_prompts(run_dir / "prompts.jsonl"))
    assert (run_dir / "manifest_pass1.json").exists()
