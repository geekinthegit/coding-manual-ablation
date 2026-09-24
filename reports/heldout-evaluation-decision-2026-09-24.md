# Held-out evaluation decision (2026-09-24)

## Original plan
decisions/02-2-development-and-held-out-sets.md §2.2.3, lines 26–28 (settled 2026-08-29): "Held-out evaluation set: Used once, for final evaluation, applying the rules developed on the development set without modification. Not touched before that point."

## Use of the held-out set to date
One structural check on 2026-09-15 (`scripts/check_population_counts.py --file heldout`; `reports/heldout-structure-check-2026-09-15.txt`, commit 32d0b8d). No model calls and no agreement calculations were made on the held-out set. No script used in the main experiment (`scripts/build_frame.py`, `scripts/build_inputs.py`, `scripts/run_experiment.py`) opens `test_data_63.xlsx`.

## Decision
Held-out evaluation will be omitted.

## Timing
Main-run data collection (`run_id` `main-2026-09-24`, execution commit beb3ef984f1b8bd0ec73f7c9f96171f80cddf1eb) was complete when this decision was recorded: pass 1 and pass 2 finished, and the runner reported that pass 3 was not needed. No scorer had been run on the main run.

## Nature of the decision
This decision departs from the plan in 02-2 §2.2.3 (line 26), which stated that the held-out set would be used once for final evaluation. The frozen decision documents do not state held-out evaluation as optional. Section 5.7.3 does not specify a procedure for changes to Section 2.2. This decision is therefore recorded separately as a post-freeze deviation from the held-out evaluation plan. The decision was made after completion of main-run data collection and before any main-study κ, Δκ or bootstrap result was computed or examined; it was not based on main-study agreement results. The held-out set has had one structural check (2026-09-15) and no model calls or agreement calculations.

## Consequences
The study's results refer to the development-set eligible target population defined in 2.1.2 and 2.3; no held-out result will be reported. decisions/02-2 is not edited by this record; a dated Revision note pointing to this record will be added to 02-2 in a later documentation clean-up.
