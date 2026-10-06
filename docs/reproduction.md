# Reproduction

This document describes how to re-run the analysis from the preserved outputs.
The API calls of the main experiment are not part of the reproduction. They cost money and the model outputs are not deterministic.
The reproduction target is the path from the preserved model outputs to the scoring results.

## 1. Environment

- Python 3.13.9
- Install dependencies with `requirements.txt`.

## 2. Source data

- Repository: SumnerLab/TalkMoves
- File: `train_data_504.xlsx`
- Size: 8,872,011 bytes
- SHA-256: c8fab1795d81c80e6815e355f7b1ba9948118b1bd67b7f402aeb0baf60148253
- Upstream commit: 869b9406de268ebab0f1b9a3bccde0b416b97290
- Verified on 2026-10-06 against the local clone at that commit.
- The source-workbook checksum was not recorded at the time of the main experiment.
- The derived analysis frame used for the main experiment was separately sealed by SHA-256 in the protocol-freeze record.
- Clone location is set by `TALKMOVES_DIR`. See README.

## 3. Prepare derived data

- Build the frame.
- Compare the SHA-256 of the generated frame with the value in the protocol-freeze record.
- Build the human-reference labels.

## 4. Use preserved model outputs

- Location of the preserved prompts, raw responses and manifests.

## 5. Reproduce scoring

- Run the scoring script on the preserved outputs.
- Compare the results with the main-scoring record.

## 6. Run tests

- `pytest -q`