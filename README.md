# coding-manual-ablation

How does replacing specific components of a coding manual with
placeholders change an LLM's agreement with human dialogue coding?

Design decisions and their rationale are recorded in
[DECISIONS.md](DECISIONS.md), which links to per-section files under
`decisions/`.

## Data

This repository does not include the corpus. It reads from a local
clone of [SumnerLab/TalkMoves](https://github.com/SumnerLab/TalkMoves)
(CC BY-NC-SA 4.0).

1. Clone the corpus:

       git clone https://github.com/SumnerLab/TalkMoves.git

2. Point `TALKMOVES_DIR` at the clone:

       export TALKMOVES_DIR=/path/to/TalkMoves

All scripts resolve data paths through `scripts/paths.py`, which reads
this variable and stops with a message if it is not set.

## Scripts

- `scripts/check_tags.py` — prints five teacher utterances per tag,
  used to verify the tag-to-category mapping against the manual.
- `scripts/check_tag_context.py <tag>` — prints the preceding
  context for rows with the given tag, used to verify Tags 3 and 4,
  whose definitions refer to the preceding student utterance.