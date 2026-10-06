"""Verify the outputs of build_frame.py against the recorded population counts.

Checks
------
1. frame.csv contains exactly the allowed API-input columns and no label column.
2. scoring_labels.csv contains exactly source_id, source_row_id, Tag.
3. source_id and source_row_id agree row by row across the two files.
4. Row counts and per-tag counts match the values recorded in Decision Log
   2.1.3 and reproduced by check_population_counts.py (commit 8f92138).
5. The eligible flag is True exactly where Sentence is present, and the
   eligible population and per-tag eligible counts match Decision Log 2.1.2
   [decided 2026-09-15].
6. rows_all.csv has no label column, one row per source row (203,601), row
   position equal to source_id, exactly the teacher count of "T" rows, each
   Transcript in one contiguous block, and its teacher rows agree with
   frame.csv field by field [decided 2026-09-23; proposed 2026-09-15].

This script reads the derived CSVs only; it does not touch the raw file.
"""

from pathlib import Path

import pandas as pd

from tags import TAG_TO_CATEGORY

REPO_ROOT = Path(__file__).resolve().parent.parent
FRAME_FILE = REPO_ROOT / "data" / "frame.csv"
LABELS_FILE = REPO_ROOT / "data" / "scoring_labels.csv"
ROWS_ALL_FILE = REPO_ROOT / "data" / "rows_all.csv"

FRAME_COLUMNS = ["source_id", "source_row_id", "Transcript", "Speaker", "Sentence", "eligible"]
LABEL_COLUMNS = ["source_id", "source_row_id", "Tag"]
ROWS_ALL_COLUMNS = ["source_id", "source_row_id", "Transcript", "Speaker", "Sentence"]
FORBIDDEN_IN_FRAME = {"Tag", "StudentTag"}

# Counts recorded in Decision Log 2.1.3 (2026-09-11), verified at commit 8f92138.
EXPECTED_TOTAL = 150_918
EXPECTED_COUNTS = {
    0: 101_309,
    1: 19_704,
    2: 2_556,
    3: 2_305,
    4: 3_436,
    5: 19_849,
    6: 1_759,
}

# Eligible target population recorded in Decision Log 2.1.2 [decided 2026-09-15]:
# teacher rows with Sentence present (274 rows have missing text in the source).
EXPECTED_ELIGIBLE_TOTAL = 150_644
EXPECTED_INELIGIBLE = 274
EXPECTED_ELIGIBLE_COUNTS = {
    0: 101_201,
    1: 19_704,
    2: 2_556,
    3: 2_145,
    4: 3_431,
    5: 19_848,
    6: 1_759,
}

# Source rows, all speakers, recorded in reports/frame-summary (2026-09-15).
EXPECTED_SOURCE_ROWS = 203_601


def main() -> None:
    # Only an empty cell is missing; the string "None" is a genuine utterance.
    frame = pd.read_csv(FRAME_FILE, keep_default_na=False, na_values=[""])
    labels = pd.read_csv(LABELS_FILE, keep_default_na=False, na_values=[""])

    assert list(frame.columns) == FRAME_COLUMNS, f"frame columns: {list(frame.columns)}"
    assert not FORBIDDEN_IN_FRAME & set(frame.columns), "label column present in frame.csv"
    assert list(labels.columns) == LABEL_COLUMNS, f"label columns: {list(labels.columns)}"

    assert len(frame) == len(labels) == EXPECTED_TOTAL, (
        f"rows: frame={len(frame):,}, labels={len(labels):,}, expected={EXPECTED_TOTAL:,}"
    )
    assert frame["source_id"].equals(labels["source_id"]), "source_id mismatch"
    assert frame["source_row_id"].equals(labels["source_row_id"]), "source_row_id mismatch"
    assert not frame["source_id"].duplicated().any()
    assert not frame["source_row_id"].duplicated().any()
    assert (frame["Speaker"] == "T").all(), "non-teacher row in frame.csv"
    assert frame["Transcript"].notna().all(), "missing Transcript in frame.csv"

    actual_counts = labels["Tag"].value_counts().sort_index()
    all_pass = True
    for tag, category in TAG_TO_CATEGORY.items():
        actual = int(actual_counts.get(tag, 0))
        expected = EXPECTED_COUNTS[tag]
        result = "PASS" if actual == expected else "FAIL"
        all_pass &= actual == expected
        print(f"Tag {tag} | {category} | actual={actual:,} | expected={expected:,} | {result}")
    assert all_pass, "per-tag counts differ from Decision Log 2.1.3"

    # Eligibility checks. read_csv keeps the boolean column as True/False.
    assert frame["eligible"].dtype == bool, f"eligible dtype: {frame['eligible'].dtype}"
    assert (frame["eligible"] == frame["Sentence"].notna()).all(), "eligible flag disagrees with Sentence presence"
    n_ineligible = int((~frame["eligible"]).sum())
    n_eligible = int(frame["eligible"].sum())
    assert n_ineligible == EXPECTED_INELIGIBLE, f"ineligible rows: {n_ineligible}"
    assert n_eligible == EXPECTED_ELIGIBLE_TOTAL, f"eligible rows: {n_eligible:,}"
    eligible_tags = labels.loc[frame["eligible"], "Tag"].value_counts().sort_index()
    print()
    eligible_pass = True
    for tag, category in TAG_TO_CATEGORY.items():
        actual = int(eligible_tags.get(tag, 0))
        expected = EXPECTED_ELIGIBLE_COUNTS[tag]
        result = "PASS" if actual == expected else "FAIL"
        eligible_pass &= actual == expected
        print(f"Tag {tag} | {category} | eligible={actual:,} | expected={expected:,} | {result}")
    assert eligible_pass, "eligible per-tag counts differ from Decision Log 2.1.2"
    print(f"Eligible rows: {n_eligible:,} (expected {EXPECTED_ELIGIBLE_TOTAL:,}); ineligible: {n_ineligible}")

    # rows_all.csv: full row table used for context windows
    # [decided 2026-09-23; proposed 2026-09-15].
    rows_all = pd.read_csv(ROWS_ALL_FILE, keep_default_na=False, na_values=[""])
    assert list(rows_all.columns) == ROWS_ALL_COLUMNS, f"rows_all columns: {list(rows_all.columns)}"
    assert not FORBIDDEN_IN_FRAME & set(rows_all.columns), "label column present in rows_all.csv"
    assert len(rows_all) == EXPECTED_SOURCE_ROWS, f"rows_all rows: {len(rows_all):,}"
    assert (rows_all["source_id"] == rows_all.index).all(), "rows_all row position != source_id"
    assert set(rows_all["Speaker"].unique()) == {"S", "T"}, rows_all["Speaker"].unique()
    assert int((rows_all["Speaker"] == "T").sum()) == EXPECTED_TOTAL, "teacher count in rows_all"
    # Each Transcript must occupy one contiguous block; the window walks over adjacent rows.
    starts = int((rows_all["Transcript"] != rows_all["Transcript"].shift()).sum())
    assert starts == rows_all["Transcript"].nunique(), "a Transcript appears in non-contiguous blocks"
    # Teacher rows agree with frame.csv at the same source_id.
    at_ids = rows_all.loc[frame["source_id"].to_numpy()]
    for col in ("source_row_id", "Transcript", "Speaker"):
        assert (at_ids[col].to_numpy() == frame[col].to_numpy()).all(), f"{col} mismatch vs frame.csv"
    assert (at_ids["Sentence"].isna().to_numpy() == frame["Sentence"].isna().to_numpy()).all(), "Sentence missingness mismatch"
    assert (at_ids["Sentence"].fillna("").to_numpy() == frame["Sentence"].fillna("").to_numpy()).all(), "Sentence text mismatch"
    print(f"rows_all.csv rows: {len(rows_all):,} (expected {EXPECTED_SOURCE_ROWS:,}); transcript blocks: {starts}")

    print(f"\nRows: {len(frame):,} (expected {EXPECTED_TOTAL:,})")
    print("frame.csv columns:", list(frame.columns))
    print("scoring_labels.csv columns:", list(labels.columns))
    print("rows_all.csv columns:", list(rows_all.columns))
    print("All checks passed.")


if __name__ == "__main__":
    main()
