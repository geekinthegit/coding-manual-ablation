# AI Workflow

This document records how AI tools were used in the coding-manual-ablation study: which tools were used, how work was divided, what instructions the coding agents received, and how far the AI-assisted process can be reproduced.

Research decisions and their rationale are documented in [DECISIONS.md](DECISIONS.md). Model and API specifications are documented in [decisions/05-2-model-and-api-parameters.md](decisions/05-2-model-and-api-parameters.md) and [decisions/05-3-call-unit-and-api-request.md](decisions/05-3-call-unit-and-api-request.md). The execution of the main experiment is documented in [reports/main-run-record-2026-09-24.md](reports/main-run-record-2026-09-24.md).

## 1. Tools used

| Tool | Underlying model / version | Window | Main use |
|:---|:---|:---|:---|
| Claude | Claude Fable 5.1; Claude Opus 5.5 for part of the study | Main window, decision windows | Decision drafting, methodological discussion, prompt preparation, result review and cross-review |
| Claude Code | Claude Fable 5.1; Claude Opus 5.5 for part of the study | Work window | Repository-based code and document work, execution, source verification and audits |
| Codex | GPT-6 Astra | Work window | Independent audits, OpenAI-API-facing implementation, and main scoring execution and verification |
| ChatGPT | GPT-5.6 Sol; GPT-6 Astra only for the statistical-analysis proposal | Separate chat | Prompt review, methodological cross-checking, interpretation review and the statistical-analysis proposal |

The model queried in the experiment, `gpt-5.5-2026-04-23`, is the object of the study, not one of the AI tools listed above. The tools above were used to plan, implement, run, and check the study. They did not generate the experimental labels.

## 2. Division of work

The researcher made or approved all research and methodological decisions, finalized decision clauses, and made every commit and push. AI tools drafted, reviewed, implemented, executed, or audited work within the scope the researcher assigned. Coding agents were instructed not to change research decisions, expand the assigned scope, or commit repository changes. The researcher specified each unit of work and adjudicated audit findings.

| Role | Carried out by |
|:---|:---|
| Research and methodological decisions, approval of decision clauses, commit and push | Researcher |
| Running the experimental API calls (pilot and main run) | Researcher |
| Decision drafting, methodological discussion, interpretation, and prompt preparation | Claude |
| Repository checks, read-only inspection, reporting, execution of checks, and drafting of code and documents | Claude Code |
| Independent audit of the scoring record | Claude Code |
| Implementation of API-facing code, the scorer, and the main scoring run | Codex |
| Independent audits before execution and before scoring | Codex |
| Prompt review, methodological cross-checking, and the statistical-analysis proposal | ChatGPT |

From Roadmap 17 onward, planning and repository file work were primarily delegated to coding agents (Codex or Claude Code). Chat-based tools were used mainly for logic checks, comprehension checks, interpretation review, and cross-review.

## 3. Instructions provided to coding agents

Two local files, `CLAUDE.md` and `AGENTS.md`, were provided to Claude Code and Codex respectively at the start of each session. They are not committed to the repository. The original files are written in Korean. Personal information was removed from them, and the redacted text is reproduced in English translation in [docs/agent-context.md](docs/agent-context.md).

## 4. Roadmap sub-steps

The sub-steps of each roadmap are listed in [docs/ai-assisted-workflow.md](docs/ai-assisted-workflow.md).

## 5. Reproducibility and limits

```
The AI-assisted development process itself is not exactly reproducible. Model outputs are stochastic, and the models used by the AI assistants listed in Section 1. The model queried in the experiment, gpt-5.5-2026-04-23, was fixed throughout.
```

The reproducible basis of the reported study is the versioned repository: committed code and decision documents, sealed analysis inputs, and execution and scoring records. This document and the roadmap sub-step list describe how AI contributed to producing and checking those materials.