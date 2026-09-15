"""Structure check for a TalkMoves data file (development or held-out).

Reproduces the teacher-population and category counts recorded in
Decision Log 2.1.3 for the development file, and runs the same structural
checks on the held-out file without expected-value comparison.

Checks
------
* Teacher rows (Speaker == "T"): N and the seven tag counts.
* Source-ID field (`Unnamed: 0`): missing, duplicate, monotonic, gaps.
* Transcript counts before and after the teacher mask.
* Gold-label mapping through tags.TAG_TO_CATEGORY.
* Missing utterance text (Sentence): counts for teacher and student rows,
  and the tag distribution of text-less teacher rows.
* Speaker == "S" rows that carry a value in the teacher Tag column.

Missing text
------------
The provider files store absent text as the literal string "nan". The file
is read with ``keep_default_na=False`` so that only "nan" is treated as
missing in Sentence, Tag, and StudentTag (the genuine utterance "None" is
preserved). This matches scripts/build_frame.py.

Usage
-----
    python check_population_counts.py                 # development file
    python check_population_counts.py --file heldout  # held-out file
    python check_population_counts.py --file heldout --out ../reports/heldout-structure-check-2026-09-15.txt

With --out, the same text printed to stdout is also written to that path.
Expected-value comparison (Decision Log 2.1.3) runs only for the
development file; the held-out file has no recorded expected values.
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

from paths import TEST_FILE, TRAIN_FILE
from tags import TAG_TO_CATEGORY

NA_RULE = {"keep_default_na": False, "na_values": {"Sentence": ["nan"], "Tag": ["nan"], "StudentTag": ["nan"]}}
PROVIDER_ID_COL = "Unnamed: 0"

# Counts recorded in Decision Log 2.1.3 on 2026-09-11 (development file only)
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

FILES = {"dev": TRAIN_FILE, "heldout": TEST_FILE}


def run(file_key: str) -> list[str]:
    """Run all checks on the selected file and return the report lines."""
    path = FILES[file_key]
    compare = file_key == "dev"
    out: list[str] = []
    say = out.append

    df = pd.read_excel(path, **NA_RULE)

    say(f"Structure check: {file_key} file")
    say(f"Source file: {path}")
    say(f"Rows (all speakers): {len(df):,}")
    say("")

    # Apply the prespecified teacher mask without additional exclusions.
    is_teacher = df["Speaker"] == "T"
    teacher_df = df[is_teacher]

    say(f"Teacher rows: {len(teacher_df):,}")
    if compare:
        say(f"Expected:     {EXPECTED_TOTAL:,}")
    say("")

    actual_counts = teacher_df["Tag"].astype(float).value_counts().sort_index()
    for tag, category in TAG_TO_CATEGORY.items():
        actual = int(actual_counts.get(tag, 0))
        if compare:
            expected = EXPECTED_COUNTS[tag]
            result = "PASS" if actual == expected else "FAIL"
            say(f"Tag {tag} | {category} | actual={actual:,} | expected={expected:,} | {result}")
        else:
            say(f"Tag {tag} | {category} | {actual:,}")
    say(f"Sum of tag counts: {int(actual_counts.sum()):,}")

    say("")
    say("Source identity checks")
    source_ids = df[PROVIDER_ID_COL]
    say(f"Missing source IDs: {int(source_ids.isna().sum())}")
    say(f"Duplicate source IDs: {int(source_ids.duplicated().sum())}")
    say(f"Source IDs are increasing: {source_ids.is_monotonic_increasing}")
    n_gaps = int(source_ids.max() + 1 - len(df))
    mismatch = source_ids != df.index
    first_gap = int(mismatch.idxmax()) if mismatch.any() else None
    say(f"Provider-ID gaps (max ID + 1 - rows): {n_gaps}; first gap at row position: {first_gap}")

    all_transcripts = set(df["Transcript"].dropna().unique())
    teacher_transcripts = set(teacher_df["Transcript"].dropna().unique())
    without_teacher = sorted(all_transcripts - teacher_transcripts, key=str)
    say(f"All transcripts: {len(all_transcripts)}")
    say(f"Teacher transcripts: {len(teacher_transcripts)}")
    say(f"Transcripts without teacher rows: {without_teacher}")
    say(f"First source row position: {df.index.min()}")
    say(f"Last source row position: {df.index.max()}")

    say("")
    say("Gold-label mapping checks")
    teacher_tags = teacher_df["Tag"]
    valid_tags = set(TAG_TO_CATEGORY)
    missing_labels = int(teacher_tags.isna().sum())
    observed_tags = set(teacher_tags.dropna().astype(int))
    unmapped_tags = sorted(observed_tags - valid_tags)
    mapped_rows = int(teacher_tags.dropna().astype(int).isin(valid_tags).sum())
    say(f"Missing teacher labels: {missing_labels}")
    say(f"Unmapped tag values: {unmapped_tags}")
    say(f"Mapped teacher rows: {mapped_rows:,} / {len(teacher_df):,}")
    say(f"Seven unique mapped categories: {len(TAG_TO_CATEGORY) == 7 and len(set(TAG_TO_CATEGORY.values())) == 7}")

    say("")
    say("Missing utterance text (Sentence == 'nan' in source)")
    missing_text = df["Sentence"].isna()
    t_missing = teacher_df["Sentence"].isna()
    say(f"Teacher rows with missing Sentence: {int(t_missing.sum()):,}")
    say(f"Student rows with missing Sentence: {int((missing_text & (df['Speaker'] == 'S')).sum()):,}")
    t_missing_tags = teacher_df.loc[t_missing, "Tag"].astype(float).value_counts().sort_index()
    for tag, category in TAG_TO_CATEGORY.items():
        n = int(t_missing_tags.get(tag, 0))
        if n:
            say(f"  Tag {tag} | {category} | {n:,}")
    say(f"Genuine utterance 'None' preserved (rows): {int((df['Sentence'] == 'None').sum())}")

    say("")
    say("Speaker == 'S' rows with a teacher Tag value")
    s_tagged = df[(df["Speaker"] == "S") & df["Tag"].notna()]
    say(f"Count: {len(s_tagged)}")
    if len(s_tagged):
        s_dist = s_tagged["Tag"].astype(float).value_counts().sort_index()
        say(f"Tag distribution: {{{', '.join(f'{int(k)}: {int(v)}' for k, v in s_dist.items())}}}")

    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--file", choices=FILES, default="dev", help="which file to check (default: dev)")
    parser.add_argument("--out", type=Path, default=None, help="also write the report to this path")
    args = parser.parse_args()

    lines = run(args.file)
    text = "\n".join(lines) + "\n"
    sys.stdout.write(text)
    if args.out is not None:
        args.out.parent.mkdir(exist_ok=True)
        args.out.write_text(text)
        sys.stdout.write(f"\nWrote {args.out}\n")


if __name__ == "__main__":
    main()
