"""build_main_sample on synthetic frame / dev_targets tables (no real data/, no git, no API).

The synthetic frame has the real frame.csv columns (source_id, source_row_id,
Transcript, Speaker, Sentence, eligible) and 60 rows, 8 of them ineligible;
5 eligible rows are development targets. The expected frame size and n are
passed as arguments, so the 150,627 / 300 constants of the real run are not
exercised here. Git calls are replaced by callables passed to run().
"""

import json

import pandas as pd
import pytest

import build_main_sample as bms

INELIGIBLE = {3, 10, 22, 30, 41, 45, 50, 59}
DEV = {0, 7, 12, 25, 38}
N_ROWS = 60
N = 10


def make_inputs(tmp_path, dev=DEV):
    ids = list(range(N_ROWS))
    frame = pd.DataFrame({
        "source_id": ids,
        "source_row_id": [i + 100 for i in ids],
        "Transcript": "t.xlsx",
        "Speaker": "T",
        "Sentence": ["" if i in INELIGIBLE else f"utterance {i}" for i in ids],
        "eligible": [i not in INELIGIBLE for i in ids],
    })
    frame_path = tmp_path / "frame.csv"
    frame.to_csv(frame_path, index=False)
    dev_path = tmp_path / "dev_targets.csv"
    pd.DataFrame({"source_id": sorted(dev), "selection_reason": "category_random"}).to_csv(dev_path, index=False)
    return frame_path, dev_path


EXPECTED_FRAME = N_ROWS - len(INELIGIBLE) - len(DEV)   # 60 - 8 - 5 = 47


def run_in(tmp_path, seed, tag="a", *, expected=EXPECTED_FRAME, n=N, status="", dev=DEV, date="2026-09-24"):
    frame_path, dev_path = make_inputs(tmp_path, dev)
    out_dir = tmp_path / tag
    return bms.run(seed, date, frame_path=frame_path, dev_path=dev_path,
                   out_path=out_dir / "main_targets.csv", manifest_dir=out_dir,
                   expected_frame_size=expected, n=n,
                   status_fn=lambda: status, head_fn=lambda: "deadbeef"), out_dir


def test_wrong_frame_size_stops_without_writing(tmp_path):
    with pytest.raises(bms.SampleError, match="sampling frame has 47 ids, expected 46"):
        run_in(tmp_path, 1, expected=46)
    assert not (tmp_path / "a" / "main_targets.csv").exists()
    assert not list((tmp_path / "a").glob("*.json")) if (tmp_path / "a").exists() else True


def test_overlap_check_fails_when_dev_targets_are_not_removed():
    eligible = set(range(20))
    dev = {1, 2, 3}
    drawn = bms.draw(sorted(eligible), seed=5, n=15)          # frame not reduced by D
    checks = bms.post_checks(drawn, eligible, dev, n=15)
    assert checks["drawn_disjoint_from_dev_targets"] is False
    with pytest.raises(bms.SampleError, match="drawn_disjoint_from_dev_targets"):
        bms.require_checks(checks)


def test_same_seed_reproduces_same_ids_and_file(tmp_path):
    m1, d1 = run_in(tmp_path, 20260924, "a")
    m2, d2 = run_in(tmp_path, 20260924, "b")
    ids1 = pd.read_csv(d1 / "main_targets.csv")["source_id"].tolist()
    ids2 = pd.read_csv(d2 / "main_targets.csv")["source_id"].tolist()
    assert set(ids1) == set(ids2)
    assert (d1 / "main_targets.csv").read_bytes() == (d2 / "main_targets.csv").read_bytes()
    assert m1["output_sha256"] == m2["output_sha256"]


def test_different_seed_gives_different_set(tmp_path):
    _, d1 = run_in(tmp_path, 1, "a")
    _, d2 = run_in(tmp_path, 2, "b")
    ids1 = set(pd.read_csv(d1 / "main_targets.csv")["source_id"])
    ids2 = set(pd.read_csv(d2 / "main_targets.csv")["source_id"])
    assert ids1 != ids2


def test_output_is_sorted_single_column_n_rows(tmp_path):
    m, d = run_in(tmp_path, 7)
    out = pd.read_csv(d / "main_targets.csv", keep_default_na=False, na_values=[""])
    assert list(out.columns) == ["source_id"]
    assert len(out) == N == m["output_count"]
    ids = out["source_id"].tolist()
    assert ids == sorted(ids)
    assert not set(ids) & DEV and not set(ids) & INELIGIBLE
    assert m["checks"] == {"len_drawn_equals_n": True, "drawn_ids_unique": True,
                           "drawn_subset_of_eligible": True, "drawn_disjoint_from_dev_targets": True}


def test_existing_output_is_not_overwritten(tmp_path):
    _, d = run_in(tmp_path, 7, "a")
    before = (d / "main_targets.csv").read_bytes()
    with pytest.raises(bms.SampleError, match="already exists"):
        run_in(tmp_path, 8, "a")
    assert (d / "main_targets.csv").read_bytes() == before


def test_dirty_tree_writes_nothing(tmp_path):
    with pytest.raises(bms.SampleError, match="not clean"):
        run_in(tmp_path, 7, "a", status=" M scripts/x.py\n")
    assert not (tmp_path / "a").exists()


def test_manifest_contents(tmp_path):
    m, d = run_in(tmp_path, 20260924)
    on_disk = json.loads((d / "main-sample-manifest-2026-09-24.json").read_text(encoding="utf-8"))
    assert on_disk["seed"] == 20260924
    assert on_disk["rng"] == {"generator": "numpy.random.Generator", "bit_generator": "PCG64"}
    assert on_disk["choice"] == {"size": N, "replace": False, "shuffle": True}
    import numpy as np
    assert on_disk["numpy_version"] == np.__version__
    assert on_disk["frame_sha256"] == bms.sha256_file(tmp_path / "frame.csv")
    assert on_disk["output_sha256"] == bms.sha256_file(d / "main_targets.csv") == m["output_sha256"]
    assert on_disk["frame_size"] == EXPECTED_FRAME and on_disk["eligible_count"] == N_ROWS - len(INELIGIBLE)
    assert on_disk["dev_targets_count"] == len(DEV) and on_disk["dev_targets_not_in_eligible"] == []
    assert on_disk["run_commit"] == "deadbeef" and on_disk["working_tree_clean"] is True
    assert on_disk["freeze_commit"] == "ed13ec2"
    assert len(on_disk["script_sha256"]) == 64
