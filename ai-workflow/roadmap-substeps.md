# Roadmap sub-steps

This file lists the sub-steps of each roadmap of the study. The tools used and their versions are described in [AI_WORKFLOW.md](../AI_WORKFLOW.md), Section 1.

## Division of work

The researcher made or approved all research and methodological decisions, finalized decision clauses, and made every commit and push. AI tools drafted, reviewed, implemented, executed, or audited work within the scope the researcher assigned. Sub-steps below are listed without names; the roles are as follows.

| Role | Carried out by |
|:---:|:---:|
| Research and methodological decisions, approval of decision clauses, commit and push | Researcher |
| Running the experimental API calls (pilot and main run) | Researcher |
| Decision drafting, methodological discussion, interpretation, and prompt preparation | Claude |
| Repository checks, read-only inspection, reporting, execution of checks, and drafting of code and documents | Claude Code |
| Independent audit of the scoring record | Claude Code |
| Implementation of API-facing code, the scorer, and the main scoring run | Codex |
| Independent audits before execution and before scoring | Codex |
| Prompt review, methodological cross-checking, and the statistical-analysis proposal | ChatGPT |

From Roadmap 17 onward, planning and repository file work were primarily delegated to coding agents (Codex or Claude Code). Chat-based tools were used mainly for logic checks, comprehension checks, interpretation review, and cross-review.

The model queried in the experiment, `gpt-5.5-2026-04-23`, is the object of the study, not one of the AI tools listed above.

## Phase 1. Initial design decisions

- 1.1 Settle the research question and the scope of claims
- 1.2 Select the dataset and identify the development and held-out sets
- 1.3 Define the manual components and their inventory
- 1.4 Specify the placeholder requirements

## Phase 2. Further design and setup before the roadmap

- 2.1 Write the names-only reference section
- 2.2 Write the context specification
- 2.3 Extend the model and API parameters
- 2.4 Write the first part of the role of the pilot
- 2.5 Set up a personal API key
- 2.6 Select the model snapshot and record the tokenizer
- 2.7 Write the tag-to-category mapping
- 2.8 Confirm that Not-coded utterances are in the analysis population
- 2.9 Fix the sampling rule and the sample size

## Phase 3. The 18-step research roadmap

### Roadmap 1. Confirm the current protocol checklist

- 1-1 Mark the current decisions as settled
- 1-2 List the remaining implementation choices
- 1-3 Separate tool validation, the procedural pilot, the main experiment, and held-out evaluation

### Roadmap 2. Verify the sampling frame and gold-label mapping

- 2-1 Reproduce the source-data frame and verify the label mapping
- 2-2 Separate model inputs from gold labels
- 2-3 Fix the missing-text handling rule
- 2-4 Define the target eligibility rule
- 2-5 Split the data decision document
- 2-6 Check the structure of the held-out file

### Roadmap 3. Fix the API request format

- 3-1 Confirm the fixed inputs
- 3-2 Decide the provisional request structure
- 3-3 Write the minimal technical test script
- 3-4 Run the technical test call
- 3-5 Fix the output-token limit
- 3-6 Record the API request specification and the test result

### Roadmap 4. Implement context construction, target marking, and input separation

- 4-1 Clarify target identification relative to the human coding condition
- 4-2 Build the ±7 context window over all rows within transcript boundaries
- 4-3 Define the target marker and text serialization (proposed)
- 4-4 Assemble the prompt for each condition, omitting the manual for names-only
- 4-5 Keep gold labels out of the input files
- 4-6 Check inputs at a normal position, a transcript boundary, and a window with missing text
- 4-7 Record the context specification and the input examples

### Roadmap 5. Fix replacement spans and verify exact token matching

- 5-1 Transcribe Chapter 1 of the manual and verify it against the component inventory
- 5-2 Build the replacement-site manifest
- 5-3 Probe candidate placeholder symbols and construction rules with the model tokenizer
- 5-4 Fix the placeholder symbol and construction rule
- 5-5 Build the replacement-condition manuals
- 5-6 Verify local token matching, preserved text, downstream token positions, and total length
- 5-7 Record the placeholder specification and the verification reports

### Roadmap 6. Fix repeated-call, label-aggregation, and failure-handling rules

Note: From Roadmap 6, where the rules began to govern actual API calls, repeated calls, and retries, ChatGPT was also used to explain and cross-check these execution concepts, including OpenAI API error codes.

- 6-1 Decide the number of repeats, the aggregation rule, and tie handling
- 6-2 Define parser normalization and the valid-label criterion, separating invalid responses from Not coded
- 6-3 Define retryable errors, the attempt limit, and handling after retries are exhausted
- 6-4 Define the repeated-call reliability indicators
- 6-5 Write the repetition and aggregation specification and the reliability indicators (proposed)
- 6-6 Review the draft and commit

### Roadmap 7. Implement the execution order and run-record system

- 7-1 Fix the execution order and seeds
- 7-2 Fix concurrency and retry rules
- 7-3 Fix interruption and resume rules
- 7-4 Fix the storage format for prompts, attempts, manifests, and recovery
- 7-5 Classify HTTP 429 errors by error code
- 7-6 Implement the runner, response validation, and the parser
- 7-7 Separate tie-break passes and align the documents with the implementation
- 7-8 Add decision-clause references to docstrings
- 7-9 Add the rules for unexpected exceptions to the run-record specification
- 7-10 Record unexpected exceptions as fatal errors and stop the run

### Roadmap 8. Fix the analysis specification and verify the scorer

- 8-1 Audit the proposed statistical rules
  - a. Audit the proposal against the existing decisions
  - b. Re-audit against the original text of the proposal
- 8-2 Decide the analysis rules
  - a. Decide the analysis set for comparisons with missing final labels
  - b. Decide the interval level, interval method, number of replicates, and seed
  - c. Decide the handling of undefined κ and degenerate intervals
  - d. Decide the interpretation boundaries for the bootstrap and for R = 3
  - e. Decide the descriptive reporting items
- 8-3 Record the analysis specification
- 8-4 Design the scorer
- 8-5 Make the scorer refuse incomplete runs
  - a. Add the incomplete-run rule to the analysis specification
  - b. Implement the entry check in the scorer
- 8-6 Implement and verify the point estimates
  - a. Implement standalone κ, paired sets, paired-set baseline κ, and Δκ
  - b. Verify the point estimates with hand-computed synthetic data
- 8-7 Implement and verify the bootstrap
  - a. Fix the bootstrap reproducibility conditions
  - b. Record the row order and the bit generator for the draws
  - c. Implement the bootstrap
  - d. Verify the bootstrap exception handling
- 8-8 Implement and verify reporting
  - a. Clarify the denominators of the repeated-call diagnostics
  - b. Implement run reading and the repeated-call diagnostics
  - c. Verify the repeated-call diagnostics with hand-computed cases
  - d. Implement the text and JSON reports and the command-line entry point

### Roadmap 9. Complete tool/task validation

- 9-1 Prepare and run the independent audit
  - a. Compare the local instruction files
  - b. Confirm the base commit and a clean working tree
  - c. Record the test status
  - d. Write the audit prompt
  - e. Run the read-only audit
  - f. Receive the audit report and check it against the prompt
- 9-2 Adjudicate the audit findings and fix the scope of changes
  - a. Confirm the blocker judgement
  - b. Classify the non-blocking issues
  - c. Decide what to change and when
  - d. Assign the changes to each party
  - e. Fix the permitted scope of changes for Codex
  - f. List corrections to earlier records
- 9-3 Decide the validation design
  - a. Fix the changes permitted and prohibited after inspecting validation output
  - b. Fix the selection rule for the development targets
  - c. Fix the scope and use of the agreement calculation
  - d. Fix the location and format of the validation records
  - e. Fix the run identifiers and the provisional operational settings
- 9-4 Record the decisions and prepare the code
  - a. Check the existing records and code read-only
  - b. Write the development-target script and its tests
  - c. Write the tool-validation decision document and the related revisions
  - d. Update the local instruction files
  - e. Push and record the pre-validation commit
- 9-5 Run the static checks
  - a. Run the input and token-matching checks on all development targets
  - b. Generate the full prompts for two targets under all six conditions
  - c. Read the prompts
  - d. Commit the check reports and the prompt files
- 9-6 Run the validation calls and write the record
  - a. Run the dry run and the validation calls
  - b. Run the parser and check the raw responses
  - c. Run the scorer and inspect anomalies
  - d. Handle defects (none were found)
  - e. Write and commit the tool-validation record
  - f. Decide the promotion of proposed items

### Roadmap 10. Run and complete the procedural pilot

- 10-1 Fix the pilot completion criteria before running
  - a. Fix the items to check and the completion criterion
  - b. Decide how paths not triggered in the pilot are recorded
  - c. Fix the rule for confirming the operational settings
  - d. Fix the run identifiers and the record location
- 10-2 Run the pilot dry run
- 10-3 Run the pilot API calls
- 10-4 Process the responses and check the operational metrics
  - a. Run the parser twice and confirm identical outputs
  - b. Compile the operational metrics
  - c. Compare the results with the completion criteria
- 10-5 Confirm the operational settings and write the pilot record
  - a. Record the confirmed operational settings in the execution specification
  - b. Write the procedural pilot record
  - c. Decide the follow-up edits after review
- 10-6 Close the records and commit
  - a. Tidy the status tags, synchronize the tool-validation document, and trim the record
  - b. Run the tests and check for residual wording
  - c. Commit and push

### Roadmap 11. Freeze the executable protocol

- 11-1 Read and classify the items to be frozen
  - a. List the remaining status tags and forward-looking sentences
  - b. Classify the sections into tag-only changes and tag-and-sentence changes
  - c. List the files to be frozen and the existing hash formats
- 11-2 Decide how each item is handled
  - a. Fix the freeze date and the tag format
  - b. Decide the wording for sentences that referred to future steps
  - c. Replace the separate change rule with the single post-freeze procedure
  - d. Separate the frozen sampling rule from the sampling seed
- 11-3 Promote the status tags and synchronize the sentences
- 11-4 Write the protocol freeze record
  - a. Fix the scope of the record
  - b. Write the record with the frozen files, hashes, and values
- 11-5 Verify and commit the record
  - a. Add the missing file to the hash table and confirm the cross-checks
  - b. Run the tests and commit

### Roadmap 12. Draw the 300-utterance main sample

- 12-1 Check the sampling inputs and the existing extraction code read-only
- 12-2 Decide the implementation details of the draw
  - a. Fix the random number generator, the frame ordering, and the draw call
  - b. Fix the output file, its columns and row order, and the manifest fields
  - c. Fix the defect criterion and the correction path for defects
  - d. Fix how the script is recorded after the freeze and how prompts_sha256 is compared in Roadmap 14
- 12-3 Write the draw script and its tests
- 12-4 Commit and push the script
- 12-5 Fix the seed before the draw
- 12-6 Run the draw and check the output
  - a. Run the first draw
  - b. Check the output read-only and recompute it independently
  - c. Decide to replace the absolute paths in the manifest before committing
  - d. Record repository-relative paths in the manifest and add a test
  - e. Commit the change and rerun the draw with the same seed
  - f. Confirm that the output is byte-identical to the first draw
- 12-7 Record the sample and commit
  - a. Add the seed revision note to the sampling decision and the post-freeze section to the freeze record
  - b. Commit and push

### Roadmap 13. Verify all main-experiment inputs

- 13-1 Check the verification tools read-only
- 13-2 Decide the verification scope and the record format
  - a. Fix the list of checks
  - b. Fix the run identifiers for the verification dry run, the pre-run dry run, and the main run
  - c. Fix the report name, language, and sections
  - d. Fix the files to be committed as the base commit for the main run
- 13-3 Run the checks without API calls
  - a. Run the input checks on all 300 targets under six conditions
  - b. Run the token-matching checks on the four replacement conditions
  - c. Run the verification dry run
  - d. Recompute the call plan and check the generated prompts
- 13-4 Judge the results
  - a. Explain the second [TARGET] occurrence as a difference in counting scope
  - b. Judge that all checks passed
- 13-5 Write and commit the input-verification report
  - a. Write the report
  - b. Commit and push

### Roadmap 14. Run the main experiment

Note: Steps in this roadmap are numbered from 14-0 to match the numbering used in the repository records.

- 14-0 Run the independent integrity audit before execution
  - a. Run the read-only audit
  - b. Judge the findings
  - c. Record the missing files in the freeze record and commit
  - d. Recheck the corrected sections
  - e. Judge the audit as ready for execution
- 14-1 Check the runner's stop, resume, and error paths read-only
- 14-2 Fix the execution plan
  - a. Fix the run identifiers and the commands
  - b. Fix the rule for abnormal termination and resumption
  - c. Fix the conditions for the tie-break passes
  - d. Fix the reporting items and the record format
- 14-3 Run the pre-run dry run and compare it with the expected values
- 14-4 Run pass 1
- 14-5 Aggregate pass 1 and parse the responses
  - a. Recheck the manifest and aggregate the attempts
  - b. Parse the responses and identify the remaining tie

  Note: A first Claude Code session ran the parser and stopped at a usage limit before reporting; the step was re-run in full in a new Claude Code session with a different model, and the parser outputs were byte-identical.
- 14-6 Run the tie-break passes
  - a. Run pass 2
  - b. Parse again and confirm that no ties remain
  - c. Confirm that pass 3 is not needed
- 14-7 Write and commit the main-run record
  - a. Write the record
  - b. Review the draft and correct it
  - c. Commit and push

### Roadmap 15. Verify the collected records and seal the final labels

- 15-1 Check the scorer inputs and the frozen completeness rules
  - a. Check the scorer inputs, the frozen rules, the parser outputs, and the stale documentation read-only
  - b. Decide the handling of the three findings outside the instructions
- 15-2 Fix the verification specification
  - a. Fix the list of completeness checks
  - b. Fix the canonical run files and the snapshot of the label files
  - c. Fix the report name, its content, and the direction of references
  - d. Fix the freeze-record entry and the files in the sealing commit
- 15-3 Run the completeness verification
  - a. Re-run the parser and confirm identical outputs
  - b. Run the scorer's run-completeness check without reading the human labels
  - c. Run the completeness checks
  - d. Copy the label files to the snapshot directory
  - e. Write the completeness report
  - f. Decide the revisions to the report
  - g. Revise the report
- 15-4 Judge the verification as passed
- 15-5 Seal the analysis inputs
  - a. Register the new files in the freeze record
  - b. Commit and push
- 15-6 Decide the scope of the documentation cleanup
  - a. Decide to leave the frozen decision documents unchanged and record known issues in an errata file
  - b. Decide the revision note for the held-out decision and the fixes to the decision index
  - c. Decide the redaction of local paths and teacher names
  - d. Decide how the documentation updates are recorded in the freeze record
- 15-7 Clean up the documentation and commit separately
  - a. Check the files to be edited read-only
  - b. Edit the documents and write the errata
  - c. Commit and push

### Roadmap 16. Score the main experiment

Note: Steps in this roadmap are numbered from 16-0 to match the numbering used in the repository records.

- 16-0 Run the read-only preflight before scoring
  - a. Write the preflight scope and prompt
  - b. Run the preflight
- 16-1 Run the scorer once
- 16-2 Verify the integrity of the scoring outputs
- 16-3 Recompute the point estimates independently
  - a. Write the recomputation prompt with the tolerance, the stop rule, and the exclusion of the bootstrap intervals
  - b. Recompute the point estimates without importing the scorer
- 16-4 Report and judge the results
  - a. Report the results
  - b. Judge the results and write the interpretation statements
- 16-5 Check the interpretation statements against the frozen decision documents
  - a. Run the first boundary check against the research question, the analysis specification, and the held-out decision record
  - b. Decide the revisions to the interpretation statements
  - c. Run the supplementary boundary check against the delegated sections and extract the reporting checklist
  - d. Adopt the statement set, the prespecified boundary clauses, and the reporting checklist
  - e. Check the cited values and their sources against the repository
  - f. Decide how the pandas version and the bootstrap seed source are recorded
- 16-6 Write the scoring record
  - a. Decide the file name, the number of decimal places, the handling of the extraction and recomputation code, and the wording of the pending audit line
  - b. Write the scoring record
  - c. Add a sentence on the missing threshold for "very small" counts, then revert it as a duplicate
- 16-7 Audit the scoring record independently
  - a. Check the working directory and Python environment of a new session, then audit the record
  - b. Check the record text and the frozen versions of the cited decision documents
  - c. Decide the corrections
  - d. Apply the corrections
  - e. Verify the corrected record
  - f. Replace the pending audit line with the final audit sentence
  - g. Verify that only that line changed
- 16-8 Commit and push

### Roadmap 17. Close out the omission of the held-out evaluation

Note: Step 17-0 precedes the numbered steps of the working notes, so that their numbers are kept.

- 17-0 Record the omission of the held-out evaluation before scoring
  - a. Check how the held-out evaluation is planned and referenced in the repository read-only
  - b. Decide to omit the held-out evaluation and to record it as a post-freeze deviation
  - c. Write the decision record and add the deviation section to the freeze record
  - d. Commit and push
- 17-1 Collect the textual evidence for the omission read-only
  - a. Collect the decision record, the deviation section, the revision note, and the scoring dates
  - b. Report the full decision record and the commit that added the deviation section
- 17-2 Judge whether the existing records are sufficient
  - a. Judge the four closing criteria against the records
  - b. Decide to keep the existing records without adding a reason or the decision maker

### Roadmap 18. Write the final report and the reproducibility checklist

Note: Step 18-0 precedes the numbered steps of the working notes, so that their numbers are kept.

- 18-0 Record the two errata carried over from Roadmap 16
  - a. Check the repository conventions for errata and revision notes read-only
  - b. Decide the location and content of the errata
  - c. Write the errata file and add the post-scoring section to the freeze record
  - d. Revise the basis lines and update the size and hash in the freeze record
  - e. Commit and push
- 18-1 Plan the report and the checklist
  - a. Plan the report sections, the checklist items, and the mapping to the authority documents read-only
  - b. Review the plan
- 18-2 Decide the plan
  - a. Decide the format, location, sections, boundary wording, and the writing and auditing tools
  - b. Check the complete set of boundary statements in the scoring record read-only
  - c. Review the result of the check
- 18-3 Write the draft report
  - a. Write the drafting prompt
  - b. Write the draft report
- 18-4 Review and revise the report
  - a. Review the draft and list the candidate revisions
  - b. Decide to correct only the errors settled by the source text and to defer the open wording choices
  - c. Apply the corrections
  - d. Commit and push the first version