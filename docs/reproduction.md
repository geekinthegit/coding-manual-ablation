# Reproduction

This document describes how to re-run the data preparation and analysis using the preserved outputs. The main-experiment API calls are not rerun; reproduction begins from the model outputs preserved in the repository and proceeds through scoring and analysis. The reasons behind the study design are not repeated here; they are documented in [`DECISIONS.md`](../DECISIONS.md) and the files under [`decisions/`](../decisions/).

## 1. Environment

- Python 3.13.9. The study was run in the conda `base` environment.
- Install the dependencies:

      pip install -r requirements.txt

## 2. Source data

- Repository: SumnerLab/TalkMoves
- File: `data/train_data_504.xlsx` in that repository
- Size: 8,872,011 bytes
- SHA-256: c8fab1795d81c80e6815e355f7b1ba9948118b1bd67b7f402aeb0baf60148253
- Upstream commit: 869b9406de268ebab0f1b9a3bccde0b416b97290
- Verified on 2026-10-06 against the local clone at upstream commit 869b940.
- The source-workbook checksum was not recorded at the time of the main experiment.
- The derived analysis frame used for the main experiment was separately sealed by SHA-256 in the protocol-freeze record.
- The clone location is given by the environment variable `TALKMOVES_DIR`. See the Data section of [`README.md`](../README.md).

## 3. Prepare derived data

One script builds the sampling frame and the human-reference labels from the source workbook:

    python scripts/build_frame.py

- Input: `$TALKMOVES_DIR/data/train_data_504.xlsx`, resolved by `scripts/paths.py`. The workbook is read only.
- Output, all under `data/` and git-ignored:
  - `data/frame.csv`: teacher rows with the `eligible` flag; no label column.
  - `data/scoring_labels.csv`: the human-reference labels (`Tag`) per teacher row, joined to the frame by `source_id`.
  - `data/rows_all.csv`: every source row, all speakers, no labels; used for context windows.
- The script also writes `reports/frame-summary-<date>.txt`. The committed summaries are `reports/frame-summary-2026-09-14.txt` and `reports/frame-summary-2026-09-15.txt`.

The human-reference labels are not stored in the repository. They are regenerated from the workbook by this script.

Check the generated files:

    python scripts/check_frame_outputs.py

Compare the SHA-256 of `data/frame.csv` and `data/scoring_labels.csv` with the values in `reports/protocol-freeze-record-2026-09-24.md`, section 4 "Frozen files", table of git-ignored files.

## 4. Use preserved model outputs

The main run is preserved under `runs/main-2026-09-24/`. Seven files are tracked in Git:

- `prompts.jsonl`: one line per (utterance_id, condition) with the full prompt text and its sha256.
- `manifest_pass1.json`: the ordered call list of pass 1, seed, request parameters, settings, input hashes and environment.
- `attempts_pass1.jsonl`: the raw API responses of pass 1, one record per attempt, append-only.
- `manifest_pass2.json`: the call list of the tie-break pass (repeat 4).
- `attempts_pass2.jsonl`: the raw API responses of the tie-break pass.
- `labels.csv`: one row per attempt, written by `scripts/parse_attempts.py`.
- `final_labels.csv`: one row per (utterance_id, condition), the aggregated label written by `scripts/parse_attempts.py`.

The scorer reads `final_labels.csv` as the model-side analysis input and `data/scoring_labels.csv` as the human side.
It reads `manifest_pass1.json` and the `attempts_pass*.jsonl` files to check that every call terminated and that `final_labels.csv` equals a fresh aggregation of the attempts.
It reads `labels.csv` for the repeated-call diagnostics.
`prompts.jsonl` is provenance and is not a scoring input.

Verbatim snapshots of `labels.csv` and `final_labels.csv` are also kept under `analysis-inputs/main-2026-09-24/`. The scorer reads `runs/main-2026-09-24/`, not the snapshots.

## 5. Reproduce scoring

    python scripts/score_run.py --run-id main-2026-09-24

- Input: `runs/main-2026-09-24/` and `data/scoring_labels.csv` from section 3. The options `--scoring-labels` and `--runs-dir` change these paths.
- Output: `runs/main-2026-09-24/score_report.txt` and `runs/main-2026-09-24/score_summary.json`. Both are git-ignored and are overwritten if present.
- The script makes no API call.

Compare the standalone κ, the paired Δκ and their 95% intervals with `reports/main-scoring-record-2026-09-24.md`, sections 8 and 9.
The report header records the generation time, the repository commit and the local run directory, so the file hashes of the two outputs differ from the values in section 6 of that record. The statistics are the values to compare.

## 6. Run tests

    pytest -q
