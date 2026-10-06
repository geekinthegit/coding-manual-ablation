"""Build the API-input frame and the separate scoring table from TalkMoves.

Purpose
-------
Split the raw training file into derived outputs so that prompt
assembly code never reads a data structure that contains human labels:

* data/frame.csv          -- teacher rows, fields allowed as API input only
* data/scoring_labels.csv -- gold labels, joined to the frame by source_id
* data/rows_all.csv       -- every source row (all speakers), no labels;
                             used only to build context windows

Canonical row order
-------------------
``source_id`` is the 0-based row position in the raw DataFrame as returned
by ``pandas.read_excel(TRAIN_FILE)``. This position defines adjacency for
the +/-7 context window (Decision Log 5.1) and is the canonical row order
for every later stage.

``source_row_id`` is the provider-assigned ID in column ``Unnamed: 0``.
In the current file it is increasing but not contiguous (49 missing values;
first gap at 2286), so it is kept for traceability to the source data only
and must not be used to define adjacency.

Missing text
------------
The provider file stores absent utterance text as the literal string "nan".
The file is read with ``keep_default_na=False`` so that only "nan" is treated
as missing in Sentence, Tag, and StudentTag; the genuine utterance "None"
(e.g., an answer to a how-many question) is preserved as text.

Target eligibility
------------------
``eligible`` (bool) marks whether a row can be sampled as a target utterance
[decided 2026-09-15]. A teacher row whose ``Sentence`` is missing in the
source file is ineligible: there is no utterance to present to the model,
so a human-LLM comparison unit does not exist for that row. Ineligible rows
are kept in ``frame.csv`` so that row adjacency for the context window is
unchanged; only the sampling script filters on this flag.

Scope
-----
frame.csv and scoring_labels.csv contain every teacher row
(``Speaker == "T"``) with no additional exclusions. rows_all.csv contains
every source row in canonical order [decided 2026-09-23; proposed 2026-09-15];
the context window
is not materialised here but constructed later from rows_all.csv. The raw
file is read only.

The CSV outputs are derivatives of TalkMoves (CC BY-NC-SA) and are
git-ignored. Only ``reports/frame-summary-<date>.txt`` is committed.
"""

import subprocess
from datetime import datetime
from pathlib import Path

import pandas as pd

from paths import TRAIN_FILE
from tags import TAG_TO_CATEGORY

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
REPORTS_DIR = REPO_ROOT / "reports"

FRAME_FILE = DATA_DIR / "frame.csv"
LABELS_FILE = DATA_DIR / "scoring_labels.csv"
ROWS_ALL_FILE = DATA_DIR / "rows_all.csv"

PROVIDER_ID_COL = "Unnamed: 0"
LABEL_COLS_IN_SOURCE = ["Tag", "StudentTag"]

FRAME_COLUMNS = ["source_id", "source_row_id", "Transcript", "Speaker", "Sentence", "eligible"]
LABEL_COLUMNS = ["source_id", "source_row_id", "Tag"]
ROWS_ALL_COLUMNS = ["source_id", "source_row_id", "Transcript", "Speaker", "Sentence"]


def git_commit_hash() -> str:
    """Return HEAD hash; append '-dirty' if the working tree has uncommitted changes."""
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    ).stdout
    return head + ("-dirty" if status.strip() else "")


def main() -> None:
    # The provider file encodes absent values as the literal string "nan".
    # pandas' default NA list also treats the string "None" as missing, which
    # erased 12 genuine utterances ("None" as an answer). Only "nan" is missing.
    df = pd.read_excel(
        TRAIN_FILE,
        keep_default_na=False,
        na_values={"Sentence": ["nan"], "Tag": ["nan"], "StudentTag": ["nan"]},
    )

    # Provider-ID gap description for the full file (reported, not asserted).
    provider_ids = df[PROVIDER_ID_COL]
    n_gaps = int(provider_ids.max() + 1 - len(df))
    mismatch = provider_ids != df.index
    first_gap = int(mismatch.idxmax()) if mismatch.any() else None

    # Full row table, all speakers, no labels, for context-window construction
    # [decided 2026-09-23; proposed 2026-09-15]. Row position in df is source_id
    # (see docstring).
    assert set(df["Speaker"].unique()) == {"S", "T"}, df["Speaker"].unique()
    assert (df["Transcript"] != "nan").all(), "literal 'nan' Transcript in source rows"
    rows_all = pd.DataFrame({
        "source_id": df.index.astype(int),
        "source_row_id": df[PROVIDER_ID_COL].astype(int),
        "Transcript": df["Transcript"],
        "Speaker": df["Speaker"],
        "Sentence": df["Sentence"],
    })[ROWS_ALL_COLUMNS]
    assert not set(LABEL_COLS_IN_SOURCE) & set(rows_all.columns), "label column leaked into rows_all"

    # Single definition of the teacher mask; every count below derives from it.
    is_teacher = df["Speaker"] == "T"
    teacher = df.loc[is_teacher].copy()
    n_teacher = len(teacher)

    # Label integrity: no missing labels; every value maps through tags.py.
    assert teacher["Tag"].notna().all(), "missing Tag in teacher rows"
    teacher["Tag"] = teacher["Tag"].astype(int)
    observed = set(teacher["Tag"].unique())
    unmapped = sorted(observed - set(TAG_TO_CATEGORY))
    assert not unmapped, f"unmapped tag values: {unmapped}"

    counts = {tag: int((teacher["Tag"] == tag).sum()) for tag in TAG_TO_CATEGORY}
    assert sum(counts.values()) == n_teacher, "category counts do not sum to N"

    # Transcript must be present on every teacher row (needed for context windows later).
    assert teacher["Transcript"].notna().all(), "missing Transcript in teacher rows"
    # Sentence missingness is reported only; the handling rule is set at the context-window stage.
    n_missing_sentence = int(teacher["Sentence"].isna().sum())

    # Target eligibility flag (see module docstring). Rows are never dropped.
    teacher["eligible"] = teacher["Sentence"].notna()
    eligible = teacher[teacher["eligible"]]
    n_eligible = len(eligible)
    assert n_eligible == n_teacher - n_missing_sentence
    eligible_counts = {tag: int((eligible["Tag"] == tag).sum()) for tag in TAG_TO_CATEGORY}
    assert sum(eligible_counts.values()) == n_eligible

    # Row position in the raw DataFrame is the canonical order (see module docstring).
    teacher["source_id"] = teacher.index.astype(int)
    teacher["source_row_id"] = teacher[PROVIDER_ID_COL].astype(int)
    assert teacher["source_id"].is_monotonic_increasing
    assert not teacher["source_row_id"].duplicated().any(), "duplicate provider IDs"

    frame = teacher[FRAME_COLUMNS]
    labels = teacher[LABEL_COLUMNS]

    assert len(frame) == len(labels) == n_teacher
    assert not set(LABEL_COLS_IN_SOURCE) & set(frame.columns), "label column leaked into frame"

    DATA_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)
    frame.to_csv(FRAME_FILE, index=False)
    labels.to_csv(LABELS_FILE, index=False)
    rows_all.to_csv(ROWS_ALL_FILE, index=False)

    now = datetime.now().astimezone()
    summary_file = REPORTS_DIR / f"frame-summary-{now:%Y-%m-%d}.txt"
    lines = [
        "Frame and scoring-label build summary",
        f"Generated at: {now.isoformat(timespec='seconds')}",
        f"Script: scripts/{Path(__file__).name}",
        f"Script commit: {git_commit_hash()}",
        f"Source file: {TRAIN_FILE}",
        f"Source rows (all speakers): {len(df):,}",
        f"Provider-ID gaps in source file: {n_gaps} (first gap at row position {first_gap})",
        "",
        f"Teacher rows (N): {n_teacher:,}",
        f"Teacher rows with missing Sentence: {n_missing_sentence:,}",
    ]
    for tag, category in TAG_TO_CATEGORY.items():
        lines.append(f"Tag {tag} | {category} | {counts[tag]:,}")
    lines += [
        "",
        f"Eligible target rows (Sentence present): {n_eligible:,}",
        f"Ineligible rows (Sentence missing): {n_teacher - n_eligible:,}",
    ]
    for tag, category in TAG_TO_CATEGORY.items():
        lines.append(f"Tag {tag} | {category} | eligible {eligible_counts[tag]:,} of {counts[tag]:,}")
    lines += [
        "",
        f"frame.csv rows: {len(frame):,}; columns: {', '.join(frame.columns)}",
        f"scoring_labels.csv rows: {len(labels):,}; columns: {', '.join(labels.columns)}",
        f"rows_all.csv rows: {len(rows_all):,}; columns: {', '.join(rows_all.columns)}",
    ]
    summary_file.write_text("\n".join(lines) + "\n")

    print("\n".join(lines))
    print(f"\nWrote {FRAME_FILE}\nWrote {LABELS_FILE}\nWrote {ROWS_ALL_FILE}\nWrote {summary_file}")


if __name__ == "__main__":
    main()
