# Protocol freeze record (Roadmap 11)

This record fixes the documents and files that define the experimental procedure before the main sample is drawn (Roadmap 12). It follows the change rules of 5.7.3 and the freeze statement in 5.6.10. All values and hashes below were read from the repository at the freeze commit; the sha256 of every tracked file was computed from the committed blob (`git show ed13ec2:<path> | shasum -a 256`), and the sha256 of every git-ignored file from the working tree at the time of the freeze. No human label was read for this record.

## 1. Purpose and scope

The protocol freeze closes Roadmap 11. From this point the procedure is executed as written; Roadmaps 12 (sampling), 13 (input verification) and 14 (main run) apply it and do not reopen design choices.

Freeze point:

| Item | Value |
| --- | --- |
| Freeze commit | `ed13ec2` (`ed13ec29a889fddfc53226e948aa3390bdcc9c9f`), 2026-09-24, "Protocol freeze (Roadmap 11): promote all [proposed] sections to [decided 2026-09-24]" |
| Parent commit | `775695a` (`775695a16de9a31ac919dd74b17b771ad3bd485d`), 2026-09-24, "Procedural pilot (Roadmap 10): fix operational settings in 5.6.4, add pilot record" |
| Working tree at freeze | clean; 160 tests passed |

This record is committed after `ed13ec2` and therefore does not contain its own commit hash; the hash of the commit that adds it is recorded in the git history only.

## 2. Changes made at the freeze

Commit `ed13ec2` changed nine files under `decisions/` (37 insertions, 37 deletions). No research decision was changed: every edit either promoted an existing [proposed] tag to [decided 2026-09-24] or rewrote a sentence that referred to tool validation or the procedural pilot as future work, using the results recorded in `reports/tool-validation-record-2026-09-23.md` and `reports/procedural-pilot-record-2026-09-24.md`.

Tag promotions (18):

| File:line | New tag |
| --- | --- |
| 03-1:77 (3.1.5), 03-1:102 (3.1.6), 03-1:160 (3.1.8) | [decided 2026-09-24; proposed 2026-09-04] |
| 03-2:4 (3.2.1) | [decided 2026-09-24; proposed 2026-09-07] |
| 03-2:95 (3.2.3) | [decided 2026-09-24; proposed 2026-09-08; scope clarified 2026-09-11] |
| 03-2:124 (3.2.4) | [decided 2026-09-24; proposed 2026-09-08] |
| 04-2:3 (4.2 file head) | [decided 2026-09-24; proposed 2026-09-17; the reporting additions in 4.2.5 were decided 2026-09-19] |
| 05-1:3 (5.1 file head) | [decided 2026-09-24; proposed 2026-09-10] |
| 05-2:110 (5.2.4) | [decided 2026-09-24; proposed 2026-09-11] |
| 05-3:112 (5.3.10) | [decided 2026-09-24; proposed 2026-09-15] |
| 05-4:3 (5.4 file head) | [decided 2026-09-24; proposed 2026-09-17] |
| 05-6:3 (5.6 file head), 05-6:17, 29, 39, 45, 62, 72, 94, 118, 137, 158 (5.6.1–5.6.10) | [decided 2026-09-24; proposed 2026-09-18] |

Forward-looking sentences synchronised with completed work (7):

| File:line | Change |
| --- | --- |
| 03-2:109 | "will therefore be held identical" → endpoint, message structure and output-format configuration are fixed in 5.3 and applied identically across conditions |
| 05-1:28 | "is a pilot check item" → in the tool validation run and the procedural pilot run (306 calls each) no answer fell outside the canonical label set; every `labels.csv` row is valid |
| 05-2 §5.2.2 (59, 61) | 59: generation parameters "will be fixed before the pilot" → are fixed in 5.3; 61: "remain to be fixed. [unresolved]" → "are fixed in 5.3. [decided 2026-09-24; previously unresolved, undated]" |
| 05-2 §5.2.4 (112, 114, 118, 120) | request-level settings are fixed in 5.3; verification was performed on the 17 development targets during tool validation (`check_inputs.py` 102 checks passed, `check_token_matching.py` 1,530 site checks with 0 mismatches) and is repeated on the 300 main-sample inputs before the first main-run call; the scripts and their results are in the repository; Status line rewritten accordingly |
| 05-4:17 | observed repeat-to-repeat variation in the pilot recorded (94 identical, 8 with a 2/1 split, out of 102); "remain proposed and unchanged" → decided 2026-09-24 without change to the procedure |
| 05-6 §5.6.10 (160) | "Promotion to [decided] happens at the roadmap 11 protocol freeze … changes are made only when a test reveals …" → all subsections decided at the freeze; any later change is handled only under 5.7.3 |
| 05-6:3 | file-head tag promotion only (counted above) |

Descriptive use of "proposed" for the now-decided procedure:

| Handling | Locations |
| --- | --- |
| Word removed | 05-3:75 ("the proposed schema" → "the schema of 5.3"); 05-4:17 ("the proposed R = 3 plus adaptive tie-resolution procedure" → "the R = 3 …"); 05-4:87 ("the proposed aggregation rules" → "the aggregation rules"); 06-analysis:67 ("the proposed R = 3 procedure" → "the R = 3 procedure") |
| Dated decision text kept, promotion note appended | 04-2:27 and 06-analysis:3, both [decided 2026-09-19], with " (status at 2026-09-19; promoted to [decided] 2026-09-24 at the protocol freeze)" |

The tag at 05-2:61 reads "[decided 2026-09-24; previously unresolved, undated]" because the original "[unresolved]" carried no date; 5.2.2 itself is tagged [decided 2026-09-09].

## 3. Frozen values

| Item | Value | Source |
| --- | --- | --- |
| Model snapshot | `gpt-5.5-2026-04-23` | 5.2.1, 5.3.5 |
| Tokenizer encoding | `o200k_base` | 5.2.1, 5.3.5 |
| Endpoint | Chat Completions | 5.3.1 |
| Generation parameters | `temperature = 0`; `reasoning_effort = "none"`; `max_completion_tokens = 64` | 5.2.2, 5.3.5 |
| Structured output | one required field `category`, enum of the seven category names of `scripts/tags.py`; `additionalProperties: false`; `strict: true`; identical schema in all six conditions | 5.3.4 |
| Operational settings | concurrency 4; timeout 60 s; backoff_initial 2 s; backoff_max 60 s; consecutive-failure threshold 10; `max_retries = 0` | 5.6.4 |
| Call-order seeds | pass 1 = 20260918; pass 2 = 20260919; pass 3 = 20260920 | 5.6.1 |
| Conditions (identifiers in code) | `baseline`, `definition_replacement`, `example_replacement`, `exclusion_rule_replacement`, `negative_control`, `names_only` | 3.1.7, 3.3, 5.1.4 |
| Repeats | R = 3 independent calls per item-condition; final label = plurality over valid repeats | 5.4.1, 5.4.2 |
| Tie rules | one additional call per tie round, at most two rounds (at most 5 repeats); a tie after the second additional call gives no final label (`unresolved tie`) | 5.4.3 |
| Attempts and validity | at most 3 attempts per repeat; aggregation only with at least 2 valid repeats | 5.4.7, 5.4.8 |
| Development targets D | 17 utterances, `samples/dev_targets.csv`, sha256 `13893677cf2073624331a0068cb2b224120d1c929ad46fbaa0213475dfd00d21`; excluded from main-experiment target selection | 5.7.2, 2.3 |
| Sampling rule | simple random sampling without replacement, n = 300, from the eligible target population minus D: 150,644 − 17 = 150,627 | 2.3.2 and its revision note of 2026-09-23 |
| Sampling seed | to be fixed before sampling in Roadmap 12 | 2.3.2 revision note |
| Scorer and bootstrap rules | as specified in 6.1–6.6 (κ, paired Δκ, 10,000 replicates, seed 20260919, undefined and degenerate handling) | 6 |

## 4. Frozen files

Tracked files, size and sha256 of the blob at `ed13ec2` (recompute with `git show ed13ec2:<path> | shasum -a 256`):

| File | Size | sha256 at ed13ec2 |
| --- | --- | --- |
| DECISIONS.md | 2,325 B | `7016fcc278e710cd6a2d4b4b19fd32ddf08fc66d47b3bb048a92797ceb7eb427` |
| decisions/01-research-question.md | 6,352 B | `887fdcd138ead4ae910ce8f6d6c72f14772ada854eaed2af12227e1570007822` |
| decisions/02-1-dataset-selection-and-scope.md | 8,965 B | `edc2414b4cfb503b509643b11c5ad23753b8248a1b08da46d370e67762b3db61` |
| decisions/02-2-development-and-held-out-sets.md | 2,777 B | `bdd79cd7cc819f4f99b4ff5a233821514a647f7feb5d5055e582d87d74001887` |
| decisions/02-3-sampling-design.md | 7,509 B | `cd15692fb5b0a47c4aea13130d2519f447dcacdddaa146520b3c7c67b6cef24a` |
| decisions/03-1-manual-component-definition.md | 20,200 B | `057a4209764d3d802d30d8435b264a83e9e42b9cac7ae54415248b207e0b5d82` |
| decisions/03-2-placeholder-specification.md | 18,649 B | `8ab2fd82cdbf670996b1231e98f9b9efb6cda9d7357028299b274cd9110031cb` |
| decisions/03-3-names-only-diagnostic.md | 1,482 B | `e8e4d097d6167fff5a989896621ee9c515c569dd1cf485603a401dccf8455d98` |
| decisions/04-2-repeated-call-reliability.md | 4,030 B | `5217ea81f16b87eac09c01db2da9bc084fc855dba2d6f1681aff4d38f60df3cb` |
| decisions/05-1-context-specification.md | 8,559 B | `f59a2b7e9be540b74b00389d14563070cd55ce6b5dfac2e0cebe5aecc8571af6` |
| decisions/05-2-model-and-api-parameters.md | 8,410 B | `926938eec8bab2f28c919241bc9eb64c1a90bc547a7db7610b1368c47ad235f4` |
| decisions/05-3-call-unit-and-api-request.md | 7,295 B | `2eebc856561c46a4e91cd77f638d3bc4c0461d56fe41a5a3d42b5a3665034248` |
| decisions/05-4-repetition-and-label-aggregation.md | 9,036 B | `5f44a7a9809c2101f4c596dead19699f99e0946fb722050ac15e699b5c62cdf6` |
| decisions/05-5-role-of-the-pilot.md | 288 B | `56a2838d4aefabbd2699184ea31136211e4e441394994bd5466bb114cf40dce9` |
| decisions/05-6-execution-order-and-run-records.md | 19,790 B | `5e3ba20e1bbd745c57127106a2c68d3b0065bd8b377f82c9ac57ff6328ef9ca9` |
| decisions/05-7-tool-validation.md | 7,396 B | `370bf39ffcf02e5452b4a77033f2868008001de2a49c748c8655f45bdabc13bc` |
| decisions/06-analysis.md | 15,230 B | `16dd9a31c4b0aa149f6f283a1560b54ab1ca9966a4015d24759ce8e9f1c24ea1` |
| scripts/run_experiment.py | 50,150 B | `a70914fd71045dbe4c5189567c27be0bba3f20667bd835bd4df1133ba720083f` |
| scripts/parse_attempts.py | 14,400 B | `c9a3ba9d99a038a11b4d16355377fdbf65d081f3de53a3895d0a8db8a9c18047` |
| scripts/score_run.py | 13,197 B | `d9c71c3a1880acfaa9ee9717b8ab4181133fbad1aae9ae9f9ce7566beca177c9` |
| scripts/check_inputs.py | 6,560 B | `cf371bc935066007f4ec8623d42a3b56d5cae1e129d3027e0970b4f95d424b2b` |
| scripts/check_token_matching.py | 5,536 B | `10b55a36bdfd7078ecf8b98aef1e383cfff8782ee0d74a4930b186f9c52f10a8` |
| scripts/build_inputs.py | 11,522 B | `f08a32df9c2db15aea05ddea1adc6f5ded6b580933ab1010a700697fb02a08b0` |
| scripts/manual_sites.py | 15,757 B | `7ae63477951970efd503df237199909cbeb66d4f5d6329289569d664febf0998` |
| scripts/tags.py | 902 B | `f14a6f6c98c375df612d9374d9842f1970d7b056eddfd5771ec3030881248851` |
| scripts/validation.py | 8,639 B | `f3029b84f7a8bbd6d835586daf31b32dc75332dcf18231c9db24a595841e8ed1` |
| scripts/test_api_request.py | 5,990 B | `536c803adec59ff8196cbf46a87a85c489f40460c3fe61b360eb2a5a40665e00` |
| scripts/scorer.py | 32,514 B | `15a955d575b024ac0b269f0a46efbc304035cea0852b43bea67f8ef53468f482` |
| scripts/paths.py | 876 B | `01e47fa90f3b04e6e9ec9e6984d0c301948e52906e66777f1afa38b9f85dff1a` |
| scripts/build_conditions.py | 4,654 B | `7911c074ded49e81fcd4a8cc2c8a4489450dd460bd0db6852f87593ecc26720e` |
| scripts/build_dev_targets.py | 9,065 B | `471c390bdfccffe89d62649923fc1198f2763ef80a446eb3615b22d976770d4e` |
| scripts/build_frame.py | 8,735 B | `213b5d8e45b95d867e676f778fbe9dd56fcddb929a13ce9b8e49c4d8c0a49efa` |
| samples/dev_targets.csv | 420 B | `13893677cf2073624331a0068cb2b224120d1c929ad46fbaa0213475dfd00d21` |
| pytest.ini | 27 B | `c809c969ec7e11b9ff37784e9c6fcc0b7c5148d168e18b05aed797e03fbd6ead` |

Git-ignored files (`.gitignore`: `manual/`, `data/`), size and sha256 of the working-tree file at the freeze; these are regenerated from the source data and the manual transcription by `build_frame.py`, `build_conditions.py` and `manual_sites.py`, and are not in the git history:

| File | Size | not tracked; sha256 at freeze |
| --- | --- | --- |
| manual/chapter1.txt | 8,220 B | `27940a360cab26ba3bf38c490143af563f536eefc8824a87abddedb21798d8c1` |
| manual/chapter1_definition_replacement.txt | 7,160 B | `0d485a551e54dd612067c00290c850e1004ade6dd9d60551e1a4a947d9c2ee58` |
| manual/chapter1_example_replacement.txt | 7,117 B | `2c388823b8a15e5f029df6e6d17d3a04226ac7fa9d75ed4a7e5780186e33f75d` |
| manual/chapter1_exclusion_rule_replacement.txt | 7,670 B | `a1bd7d21c25c57aa6b6de5d2ca92fe895ef0e8fc73e897d1f726db83cff3c727` |
| manual/chapter1_negative_control.txt | 7,960 B | `9114addaf6995235985607a076819486eeb4996ca79daefd3a1050eef7618d6c` |
| data/frame.csv | 14,897,803 B | `39506e9cb60fe4786057e8993f713127d8f89ca5ffbd8f9344ffed1aea333154` |
| data/rows_all.csv | 18,353,538 B | `71fc760091277c33cae03eafbb9f3f7a5ebe1a9f5dd0a4fe64faa3c021ff23c0` |
| data/scoring_labels.csv | 2,269,412 B | `44e95948c340184e204856bda7d7c56cc17b1b7e7ba9ae8eb3f9f6b583340e58` |
| data/placeholder_plan.csv | 3,183 B | `e4d510a8082a5593c492b83c3c2c3889904790fbd219de3a48aeb7e1b8a9b3a5` |
| data/replacement_manifest.csv | 9,323 B | `6d52b70231fd956a7e9dbe094d53e9fe25608ed5261247fb13e3774a03ab65bb` |

The `data/scoring_labels.csv` hash equals the value recorded in the validation score report header (`reports/tool-validation-record-2026-09-23.md` §6), and the `manual/` hashes correspond to the condition files whose token matching was verified on D (`reports/token-matching-check-2026-09-23.txt`).

## 5. Procedure after the freeze

Roadmaps 12–14 execute the frozen protocol rather than reopen design choices; any exception requires the change procedure in §5.7.3.

Post-freeze changes under §5.7.3 are appended to this record as dated revision notes with the new hashes. The original freeze record is never edited; revision notes are append-only.

The following later artifacts are compared against the hashes in section 4: the Roadmap 12 sample manifest (source data version and the sampling script), the Roadmap 13 input-verification report on the 300 sampled inputs (`check_inputs.py`, `check_token_matching.py`, the `manual/` and `data/` files used), and the Roadmap 14 main-run `manifest_pass1.json` (`git_commit`, `input_file.sha256`, `prompts_sha256`).
