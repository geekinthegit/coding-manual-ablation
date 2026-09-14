"""Verify the outputs of build_frame.py against the recorded population counts.

Checks
------
1. frame.csv contains exactly the allowed API-input columns and no label column.
2. scoring_labels.csv contains exactly source_id, source_row_id, Tag.
3. source_id and source_row_id agree row by row across the two files.
4. Row counts and per-tag counts match the values recorded in Decision Log
   2.1.3 and reproduced by check_population_counts.py (commit 8f92138).

This script reads the derived CSVs only; it does not touch the raw file.
"""

from pathlib import Path

import pandas as pd

from tags import TAG_TO_CATEGORY

REPO_ROOT = Path(__file__).resolve().parent.parent
FRAME_FILE = REPO_ROOT / "data" / "frame.csv"
LABELS_FILE = REPO_ROOT / "data" / "scoring_labels.csv"

FRAME_COLUMNS = ["source_id", "source_row_id", "Transcript", "Speaker", "Sentence"]
LABEL_COLUMNS = ["source_id", "source_row_id", "Tag"]
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


def main() -> None:
    frame = pd.read_csv(FRAME_FILE)
    labels = pd.read_csv(LABELS_FILE)

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

    print(f"\nRows: {len(frame):,} (expected {EXPECTED_TOTAL:,})")
    print("frame.csv columns:", list(frame.columns))
    print("scoring_labels.csv columns:", list(labels.columns))
    print("All checks passed.")


if __name__ == "__main__":
    main()
