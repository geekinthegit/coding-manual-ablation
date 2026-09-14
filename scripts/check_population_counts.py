"""Reproduce the teacher-population and category counts in Decision Log 2.1.3."""

import pandas as pd

from paths import TRAIN_FILE
from tags import TAG_TO_CATEGORY


# Counts recorded in Decision Log 2.1.3 on 2026-09-11
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

df = pd.read_excel(TRAIN_FILE)

# Apply the prespecified teacher mask without additional exclusions.
teacher_df = df[df["Speaker"] == "T"]

print(f"Teacher rows: {len(teacher_df):,}")
print(f"Expected:     {EXPECTED_TOTAL:,}")
print()

actual_counts = teacher_df["Tag"].value_counts().sort_index()

for tag, category in TAG_TO_CATEGORY.items():
    actual = int(actual_counts.get(tag, 0))
    expected = EXPECTED_COUNTS[tag]
    result = "PASS" if actual == expected else "FAIL"

    print(
        f"Tag {tag} | {category} | "
        f"actual={actual:,} | expected={expected:,} | {result}"
    )

    print()
print("Source identity checks")

# Check whether the source-provided ID can uniquely identify every teacher row.
source_ids = teacher_df["Unnamed: 0"]

print("Missing source IDs:", source_ids.isna().sum())
print("Duplicate source IDs:", source_ids.duplicated().sum())
print("Source IDs are increasing:", source_ids.is_monotonic_increasing)

# Count transcripts before and after applying the teacher mask.
all_transcripts = set(df["Transcript"].dropna().unique())
teacher_transcripts = set(teacher_df["Transcript"].dropna().unique())
transcripts_without_teacher = sorted(
    all_transcripts - teacher_transcripts,
    key=str,
)

print("All transcripts:", len(all_transcripts))
print("Teacher transcripts:", len(teacher_transcripts))
print("Transcripts without teacher rows:", transcripts_without_teacher)

# The unfiltered DataFrame index preserves row position in the current Excel data.
print("First source row position:", df.index.min())
print("Last source row position:", df.index.max())

print()
print("Gold-label mapping checks")

# Verify that every teacher label can be mapped through tags.py.
teacher_tags = teacher_df["Tag"]
valid_tags = set(TAG_TO_CATEGORY)

missing_labels = int(teacher_tags.isna().sum())
mapped_rows = int(teacher_tags.isin(valid_tags).sum())
observed_tags = set(teacher_tags.dropna().astype(int))
unmapped_tags = sorted(observed_tags - valid_tags)

mapping_has_seven_unique_categories = (
    len(TAG_TO_CATEGORY) == 7
    and len(set(TAG_TO_CATEGORY.values())) == 7
)

print("Missing teacher labels:", missing_labels)
print("Unmapped tag values:", unmapped_tags)
print(f"Mapped teacher rows: {mapped_rows:,} / {len(teacher_df):,}")
print(
    "Seven unique mapped categories:",
    mapping_has_seven_unique_categories,
)