"""build_dev_targets on synthetic frame / scoring_labels tables (no real data/, no API).

The synthetic frame covers source_ids 0-41 plus 23541 so that the three
boundary cases of the script exist; Tags cycle 0-6 so every Tag has at least
five eligible rows. A few rows are ineligible to check that they are never
selected.
"""

import pandas as pd
import pytest

import build_dev_targets as bdt
from tags import TAG_TO_CATEGORY

INELIGIBLE = {3, 10, 30}


def make_tables(boundary_ineligible: set[int] = frozenset()) -> tuple[pd.DataFrame, pd.DataFrame]:
    ids = list(range(42)) + [23541]
    ineligible = INELIGIBLE | set(boundary_ineligible)
    frame = pd.DataFrame({
        "source_id": ids,
        "source_row_id": ids,
        "Transcript": "t.xlsx",
        "Speaker": "T",
        "Sentence": ["" if s in ineligible else f"utterance {s}" for s in ids],
        "eligible": [s not in ineligible for s in ids],
    })
    labels = pd.DataFrame({"source_id": ids, "source_row_id": ids, "Tag": [s % 7 for s in ids]})
    return frame, labels


def expected_tag_count(sel: bdt.Selection, tag: int) -> int:
    """N_PER_TAG random rows plus the boundary rows of that Tag that were not also drawn."""
    boundary_rows = sel.rows[sel.rows["selection_reason"] != bdt.RANDOM_REASON]
    extra = sum(1 for r in boundary_rows.itertuples(index=False) if r.Tag == tag and r.source_id not in sel.overlap)
    return bdt.N_PER_TAG + extra


def test_same_seed_gives_same_selection():
    frame, labels = make_tables()
    a = bdt.select_dev_targets(frame, labels)
    b = bdt.select_dev_targets(frame, labels)
    assert a.rows.equals(b.rows)
    assert a.overlap == b.overlap
    assert a.seed == bdt.SEED == 20260923


def test_two_random_rows_per_tag():
    sel = bdt.select_dev_targets(*make_tables())
    for tag in sorted(TAG_TO_CATEGORY):
        assert int((sel.rows["Tag"] == tag).sum()) == expected_tag_count(sel, tag), tag
    assert int((sel.rows["selection_reason"] == bdt.RANDOM_REASON).sum()) == bdt.N_PER_TAG * 7 - len(sel.overlap)


def test_boundary_cases_included_with_their_reasons():
    sel = bdt.select_dev_targets(*make_tables())
    reason = dict(zip(sel.rows["source_id"], sel.rows["selection_reason"]))
    for sid, expected in bdt.BOUNDARY_REASONS.items():
        assert reason[sid] == expected
    assert 14 <= len(sel.rows) <= 17


def test_no_ineligible_rows_and_no_duplicates():
    frame, labels = make_tables()
    sel = bdt.select_dev_targets(frame, labels)
    assert not set(sel.rows["source_id"]) & INELIGIBLE
    assert not sel.rows["source_id"].duplicated().any()
    assert list(sel.rows["source_id"]) == sorted(sel.rows["source_id"])


def test_output_csv_has_two_columns_only(tmp_path):
    sel = bdt.select_dev_targets(*make_tables())
    path = tmp_path / "samples" / "dev_targets.csv"
    bdt.write_targets(sel, path)
    out = pd.read_csv(path, keep_default_na=False, na_values=[""])
    assert list(out.columns) == ["source_id", "selection_reason"]
    assert list(out["source_id"]) == list(sel.rows["source_id"])


@pytest.mark.parametrize("sid", sorted(bdt.BOUNDARY_REASONS))
def test_ineligible_boundary_case_is_an_error(sid):
    frame, labels = make_tables(boundary_ineligible={sid})
    with pytest.raises(ValueError):
        bdt.select_dev_targets(frame, labels)


def test_tag_with_too_few_rows_is_an_error():
    frame, labels = make_tables()
    labels = labels.copy()
    labels.loc[labels["source_id"] != 6, "Tag"] = labels.loc[labels["source_id"] != 6, "Tag"].replace(6, 5)
    with pytest.raises(ValueError):
        bdt.select_dev_targets(frame, labels)
