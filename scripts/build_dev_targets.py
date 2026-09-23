"""Select the development targets D for tool validation and the procedural pilot (Roadmap 9, 10).

D is a small, fixed set of eligible teacher utterances used to exercise the
tools and the procedure before the main experiment. Its members are excluded
as targets from the 300-utterance main sample (2.3, revision to be added).
This is a sampling script: it builds no API input and sends nothing.

Inputs (derived CSVs from build_frame.py, read with keep_default_na=False,
na_values=[""] like the other scripts):
* data/frame.csv          source_id, source_row_id, Transcript, Speaker, Sentence, eligible
* data/scoring_labels.csv source_id, source_row_id, Tag

Selection rule:
(a) frame rows with eligible == True, joined to scoring_labels on source_id;
(b) for each Tag 0-6 in ascending order, 2 rows drawn without replacement by
    numpy.random.default_rng(SEED) from that Tag's source_ids sorted
    ascending (rng.choice(ids, size=2, replace=False)); the order of the
    draws is fixed so the set is reproducible;
(c) the boundary cases source_id 0, 7 and 23541 are added; each must be
    eligible, otherwise the script stops with an error;
(d) a row drawn in (b) that is also a boundary case appears once, with the
    boundary reason; the final size is at most 17.

Outputs:
* samples/dev_targets.csv                 columns source_id, selection_reason; source_id ascending
* reports/dev-targets-<YYYY-MM-DD>.txt    script commit, seed, eligible counts per Tag,
                                          the selected rows with their Tag and reason,
                                          final size and whether an overlap occurred

Usage (repository root, conda base):
    python scripts/build_dev_targets.py
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from build_inputs import git_commit_hash
from paths import DEV_TARGETS_FILE, FRAME_FILE, REPORTS_DIR, SAMPLES_DIR, SCORING_LABELS_FILE
from tags import TAG_TO_CATEGORY

SEED = 20260923
N_PER_TAG = 2
# Boundary cases (2.3; input construction 5.1): the first row of the file,
# the first row with a full context window on both sides, and a row whose
# window contains an empty utterance.
BOUNDARY_REASONS: dict[int, str] = {
    0: "boundary_first_row",
    7: "boundary_full_window",
    23541: "boundary_empty_text_in_window",
}
RANDOM_REASON = "category_random"
OUTPUT_COLUMNS = ["source_id", "selection_reason"]


@dataclass(frozen=True)
class Selection:
    """Result of select_dev_targets.

    rows: DataFrame with source_id, Tag, selection_reason, sorted by
    source_id ascending. n_eligible and tag_counts describe the eligible
    labelled population the draw was made from. overlap lists the boundary
    source_ids that were also drawn in the per-Tag random step (d).
    """
    rows: pd.DataFrame
    seed: int
    n_eligible: int
    tag_counts: dict[int, int]
    overlap: list[int]


def read_tables(frame_path: Path = FRAME_FILE, labels_path: Path = SCORING_LABELS_FILE) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Read frame.csv and scoring_labels.csv as the other scripts do (only "" is missing)."""
    frame = pd.read_csv(frame_path, keep_default_na=False, na_values=[""])
    labels = pd.read_csv(labels_path, keep_default_na=False, na_values=[""])
    return frame, labels


def is_true(series: pd.Series) -> pd.Series:
    """Boolean view of the eligible column whether it was parsed as bool or left as text."""
    return series.map(lambda v: v is True or str(v) == "True")


def eligible_labelled(frame: pd.DataFrame, labels: pd.DataFrame) -> pd.DataFrame:
    """Step (a): eligible frame rows joined to their Tag on source_id (2.1.2 eligibility).

    Returns a DataFrame with integer source_id and Tag, sorted by source_id.
    Raises ValueError when source_id is duplicated in either table, when an
    eligible row has no label, or when a Tag is not a key of TAG_TO_CATEGORY.
    """
    for name, df in (("frame.csv", frame), ("scoring_labels.csv", labels)):
        if df["source_id"].duplicated().any():
            raise ValueError(f"{name}: duplicated source_id")
    elig = frame.loc[is_true(frame["eligible"]), ["source_id"]].copy()
    elig["source_id"] = elig["source_id"].astype(int)
    lab = labels[["source_id", "Tag"]].copy()
    lab["source_id"] = lab["source_id"].astype(int)
    joined = elig.merge(lab, on="source_id", how="left")
    if joined["Tag"].isna().any():
        missing = joined.loc[joined["Tag"].isna(), "source_id"].tolist()
        raise ValueError(f"eligible rows without a label in scoring_labels.csv: {missing[:5]} ({len(missing)} total)")
    joined["Tag"] = joined["Tag"].astype(int)
    bad = sorted(set(joined["Tag"]) - set(TAG_TO_CATEGORY))
    if bad:
        raise ValueError(f"Tag values not in tags.TAG_TO_CATEGORY: {bad}")
    return joined.sort_values("source_id").reset_index(drop=True)


def select_dev_targets(frame: pd.DataFrame, labels: pd.DataFrame, seed: int = SEED,
                       boundary: dict[int, str] = BOUNDARY_REASONS) -> Selection:
    """Steps (a)-(e): the development target set and its selection reasons.

    Per Tag in ascending key order of TAG_TO_CATEGORY, N_PER_TAG source_ids
    are drawn by rng.choice over the Tag's source_ids sorted ascending, from
    one numpy.random.default_rng(seed) shared across Tags in that order (b).
    Boundary source_ids are then added (c); each must be eligible, otherwise
    ValueError. A source_id in both sets is kept once with its boundary
    reason (d, e). Raises ValueError when a Tag has fewer than N_PER_TAG
    eligible rows.
    """
    pop = eligible_labelled(frame, labels)
    tag_of = dict(zip(pop["source_id"], pop["Tag"]))
    tag_counts = {t: int((pop["Tag"] == t).sum()) for t in sorted(TAG_TO_CATEGORY)}

    rng = np.random.default_rng(seed)
    random_ids: list[int] = []
    for t in sorted(TAG_TO_CATEGORY):
        ids = sorted(int(s) for s in pop.loc[pop["Tag"] == t, "source_id"])
        if len(ids) < N_PER_TAG:
            raise ValueError(f"Tag {t} has {len(ids)} eligible rows, fewer than {N_PER_TAG}")
        random_ids.extend(int(s) for s in rng.choice(ids, size=N_PER_TAG, replace=False))

    not_eligible = [s for s in boundary if s not in tag_of]
    if not_eligible:
        raise ValueError(f"boundary source_ids not eligible or not present: {not_eligible}")

    overlap = sorted(s for s in boundary if s in random_ids)
    reason: dict[int, str] = {s: RANDOM_REASON for s in random_ids}
    reason.update(boundary)          # boundary reason wins on overlap (e)
    rows = pd.DataFrame({"source_id": sorted(reason)})
    rows["Tag"] = rows["source_id"].map(tag_of).astype(int)
    rows["selection_reason"] = rows["source_id"].map(reason)
    return Selection(rows=rows, seed=seed, n_eligible=len(pop), tag_counts=tag_counts, overlap=overlap)


def write_targets(selection: Selection, path: Path = DEV_TARGETS_FILE) -> None:
    """samples/dev_targets.csv with source_id and selection_reason only (no Tag)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    selection.rows[OUTPUT_COLUMNS].to_csv(path, index=False)


def report_lines(selection: Selection, now: datetime) -> list[str]:
    """Text of the report: commit, seed, population counts, the selected rows, size, overlap."""
    lines = [
        "Development targets (Roadmap 9 tool validation, Roadmap 10 procedural pilot)",
        f"Generated at: {now.isoformat(timespec='seconds')}",
        f"Script commit: {git_commit_hash()}",
        f"Seed: {selection.seed} (numpy.random.default_rng)",
        f"Rule: {N_PER_TAG} per Tag drawn from eligible rows, plus boundary cases {sorted(BOUNDARY_REASONS)}",
        "",
        f"Eligible labelled rows: {selection.n_eligible:,}",
    ]
    for t in sorted(selection.tag_counts):
        lines.append(f"Tag {t} | {TAG_TO_CATEGORY[t]} | eligible {selection.tag_counts[t]:,}")
    lines += ["", "Selected rows (source_id | Tag | selection_reason):"]
    for r in selection.rows.itertuples(index=False):
        lines.append(f"{r.source_id} | {r.Tag} | {r.selection_reason}")
    lines += [
        "",
        f"Final count: {len(selection.rows)}",
        f"Overlap between random draw and boundary cases: {'yes ' + str(selection.overlap) if selection.overlap else 'no'}",
    ]
    return lines


def write_report(selection: Selection, reports_dir: Path = REPORTS_DIR, now: datetime | None = None) -> Path:
    now = now or datetime.now().astimezone()
    reports_dir.mkdir(exist_ok=True)
    path = reports_dir / f"dev-targets-{now:%Y-%m-%d}.txt"
    path.write_text("\n".join(report_lines(selection, now)) + "\n", encoding="utf-8")
    return path


def main() -> None:
    frame, labels = read_tables()
    selection = select_dev_targets(frame, labels)
    SAMPLES_DIR.mkdir(exist_ok=True)
    write_targets(selection)
    report_path = write_report(selection)
    print(f"wrote {DEV_TARGETS_FILE}: {len(selection.rows)} rows")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
