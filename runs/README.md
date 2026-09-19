# runs/

Run records written by `scripts/run_experiment.py` (Decision Log 5.6). Everything
here except this README is git-ignored: the files contain prompt text (manual
transcription) and raw API responses.

```
runs/<run_id>/
  prompts.jsonl        one line per (utterance_id, condition): full prompt + sha256
  manifest_pass1.json  ordered call list, seed, request params, settings, hashes, env
  attempts_pass1.jsonl append-only: attempt_started / attempt_completed / run_stopped
  manifest_pass2.json  repeat-4 tie-break calls (only after pass 1 is fully terminated and ties remain)
  attempts_pass2.jsonl
  manifest_pass3.json  repeat-5 tie-break calls (only after pass 2 is fully terminated and ties remain)
  attempts_pass3.jsonl
  labels.csv           written by scripts/parse_attempts.py: one row per attempt
  final_labels.csv     written by scripts/parse_attempts.py: 5.4 aggregation per (utterance, condition)
  recovery_log.jsonl   only after a --repair
  run.lock             only while a runner process holds the run
```

After the last pass has terminated, run `python scripts/parse_attempts.py --run-id <run_id>`
once more so labels.csv and final_labels.csv reflect all passes. Analysis reads
final_labels.csv only after this step.

Records are never edited. The single exception is `--repair`, which removes an
incomplete final line after copying the file to `attempts_passN.jsonl.bak-<timestamp>`
and logging the removed bytes in `recovery_log.jsonl`.
