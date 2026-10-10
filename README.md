# coding-manual-ablation

How does replacing specific components of a dialogue coding manual with placeholders change an LLM's agreement with human dialogue coding?

This repository contains an independent methodological study (August–September 2026) that answers that question on the TalkMoves classroom dialogue corpus. Chapter 1 of the TalkMoves coding manual was given to GPT-5.5 (gpt-5.5-2026-04-23) in six conditions: the full manual, four conditions in which one component type was replaced by token-matched placeholders (definitions, examples, exclusion rules, and a negative control of background text), and a names-only reference with no manual text. Agreement with the human labels was measured by unweighted Cohen's κ on 300 randomly sampled teacher utterances. The protocol and analysis plan were frozen before the sample was drawn. The full report is [reports/final-research-report-2026-09-25.md](reports/final-research-report-2026-09-25.md).

## Results

Baseline κ = 0.6085 (95% interval 0.5266 to 0.6846), exact agreement P_o = 0.7867 (236 of 300), n = 300.

| Condition | Δκ | 95% interval |
| --- | --- | --- |
| Definition replacement | −0.0018 | [−0.0384, 0.0360] |
| Example replacement | −0.0611 | [−0.1047, −0.0191] |
| Exclusion-rule replacement | −0.1062 | [−0.1576, −0.0556] |
| Negative control | −0.0232 | [−0.0581, 0.0118] |

Names-only reference: κ = 0.2727 (0.1971 to 0.3475), reported descriptively and excluded from the Δκ comparisons.

Agreement was lower than baseline under example replacement and exclusion-rule replacement, where the interval excluded zero. For definition replacement and the negative control the interval included zero; this is not read as evidence of no effect or of equivalence. Intervals are pointwise paired-bootstrap percentile intervals (10,000 replicates) and are not adjusted for multiple comparisons. Full numbers, confusion matrices, and claim boundaries are in [reports/main-scoring-record-2026-09-24.md](reports/main-scoring-record-2026-09-24.md).

## Getting started

The quickest way to see what the study does is the walkthrough notebook, [examples/walkthrough_one_utterance.ipynb](examples/walkthrough_one_utterance.ipynb). It takes one teacher utterance from the preserved main-run outputs, shows the prompt it received under each of the six conditions, the model's three responses per condition, the category the repository parser derives from each response, and the aggregated final label per condition. It does not show the human label or compute κ, because the human labels are derived from the source workbook and are not tracked in the repository. It reads only files in the repository (in Colab, a setup cell clones the repository first) and needs no API key or corpus download. Open it locally or in Google Colab.

To run the scripts and tests:

1. Install the environment: `pip install -r requirements.txt` ([requirements.txt](requirements.txt)). Package versions used in the study are recorded in [decisions/05-2-model-and-api-parameters.md](decisions/05-2-model-and-api-parameters.md) §5.2.3.
2. Clone the corpus and point the scripts to it:

       git clone https://github.com/SumnerLab/TalkMoves.git
       export TALKMOVES_DIR=/path/to/TalkMoves

   All scripts resolve data paths through [scripts/paths.py](scripts/paths.py), which reads this variable and stops with a message if it is not set.
3. Run the tests: `python -m pytest -q` (169 tests, no network).
4. Re-run scoring on the preserved model outputs without API calls, or rebuild the derived data from the corpus: see [docs/reproduction.md](docs/reproduction.md).

## Repository layout

| Folder | Contents |
| --- | --- |
| [decisions/](decisions/) | one file per design decision, with status tags and revision notes; [DECISIONS.md](DECISIONS.md) is the table of contents |
| [reports/](reports/) | protocol freeze record, sample manifest, tool validation and procedural pilot records, input verification, main run record, completeness report, scoring record, final report, held-out decision, errata, and the data and input validation outputs; [reports/README.md](reports/README.md) describes each file |
| [docs/](docs/) | reproduction guide, research workflow, roadmap and AI-assisted workflow, agent context |
| [scripts/](scripts/) | frame construction, sampling, condition building, token-matching check, API runner, parser, scorer; `check_tags.py` prints five teacher utterances per tag to verify the tag-to-category mapping against the manual, and `check_tag_context.py <tag>` prints the preceding context for rows with the given tag to verify Tags 3 and 4, whose definitions refer to the preceding student utterance |
| [tests/](tests/) | unit tests (169) |
| [examples/](examples/) | offline walkthrough notebook for one utterance; see Getting started |
| [analysis-inputs/](analysis-inputs/) | verbatim snapshots of `labels.csv` and `final_labels.csv` of the main run, with their hashes registered in the protocol freeze record; the scorer reads `runs/`, not these |
| [runs/](runs/) | run records; only [runs/README.md](runs/README.md) and [runs/main-2026-09-24/](runs/main-2026-09-24/) are tracked |
| [samples/](samples/) | `dev_targets.csv` (the 17 development targets used for tool validation and the pilot, with selection reasons) and `main_targets.csv` (the 300 source IDs of the main sample) |
| [manual/](manual/) | transcription of the coding manual chapter, its extraction corrections, and the four condition manuals |
| `data/` | derived data files; git-ignored |

## Data and licensing

The TalkMoves corpus is not included. Scripts read it from the directory named by the environment variable `TALKMOVES_DIR` (see [scripts/paths.py](scripts/paths.py)). The corpus and the coding manual are licensed CC BY-NC-SA 4.0; files in this repository derived from them ([runs/main-2026-09-24/](runs/main-2026-09-24/), [manual/](manual/)) are covered by [LICENSE-DATA](LICENSE-DATA) under the same terms. Code is under [LICENSE](LICENSE) (MIT). Human reference labels are not stored in the repository.

## Decisions and workflow

- [DECISIONS.md](DECISIONS.md) — index of all design decisions, linked to their sections
- [AI_WORKFLOW.md](AI_WORKFLOW.md) — AI tools used, division of work, and instructions given to coding agents
- [docs/ai-assisted-workflow.md](docs/ai-assisted-workflow.md) — the 18-step roadmap and its sub-steps
- [docs/research-workflow.md](docs/research-workflow.md) — mapping of this study to the validity-guided workflow (Lin, 2026)

## Status

The study is complete. No held-out evaluation was conducted ([reports/heldout-evaluation-decision-2026-09-24.md](reports/heldout-evaluation-decision-2026-09-24.md)). The final report has not had an independent audit. Post-scoring documentation changes are listed in [reports/documentation-errata-post-scoring-2026-09-25.md](reports/documentation-errata-post-scoring-2026-09-25.md).
