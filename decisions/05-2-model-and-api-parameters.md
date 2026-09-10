## 5.2 Model and API parameters

### 5.2.1 Model selection and version control

[decided 2026-09-09; originally proposed 2026-09-08]

The model must satisfy two requirements.

1. Token-sequence-level verification  
   Section 3.2.3 requires verification that the first unchanged content following each replacement span begins at the same token index as in the baseline prompt. The selected model must therefore allow the model-specific token-ID sequence of the complete prompt to be reproduced and inspected locally.

2. Fixed model version  
   The model version must remain stable throughout data collection. Provider-side model updates can alter model behavior and threaten replicability; the exact model version, API parameters, endpoint, and collection dates must therefore be fixed or recorded (Lin, 2025).

Two model classes satisfy these requirements:

- a pinned open-weight model with its tokenizer;
- an OpenAI dated snapshot with a compatible `tiktoken` encoding.

An OpenAI dated snapshot is used for the present project. A pinned open-weight model also satisfies the methodological requirements but requires additional management of the model checkpoint, inference engine, quantization settings, hardware environment, and software configuration.

The selected model is:

- Model snapshot: `gpt-5.5-2026-04-23`
- Tokenizer encoding: `o200k_base`

Compatibility was verified locally on 2026-09-09 using `tiktoken 0.14.0`. The call

`encoding_for_model("gpt-5.5-2026-04-23")`

returned `o200k_base`, and the tokenizer successfully returned a token-ID sequence for test text. This satisfies the token-sequence access requirement in Section 3.2.3.

Alternatives not adopted:

| Option | Reason |
| --- | --- |
| Moving API model alias | The underlying model version may change during data collection. |
| Web interface | Exact model version and generation parameters may be unavailable or insufficiently controllable. |
| API model without token-sequence-level access | Cannot implement the token-position checks required by Section 3.2.3. |
| Pinned open-weight model | Meets the requirements but adds inference-environment and documentation burden relative to the project timeline. |

The same snapshot will be used for tool validation, the pilot, and the main experiment. Model selection will not be changed on the basis of agreement results.


### 5.2.2 Generation parameters

[decided 2026-09-09]

Temperature is fixed at `0` for all experimental conditions. Temperature is treated as a technical variable rather than an experimental factor: the research question concerns the effect of manual-component replacement on human–LLM agreement, so variation in sampling temperature would introduce an unnecessary source of response variation.

The following configuration was successfully tested with the selected snapshot on 2026-09-09:

- `temperature = 0`
- `reasoning_effort = "none"`

The test API call returned a valid response from `gpt-5.5-2026-04-23`, with `reasoning_tokens = 0`.

`reasoning_effort = "none"` is used because the task is constrained classification rather than open-ended reasoning. The setting is held constant across all conditions.

Other generation parameters used in the final calling script will be fixed before the pilot and applied identically across baseline, replacement conditions, the negative control, and the names-only diagnostic.

The final API endpoint and output-format method remain to be fixed. [unresolved]


### 5.2.3 Environment record

[decided 2026-09-09]

The computational environment will be recorded so that the API configuration and token-index verification can be reconstructed.

The record will include:

- provider;
- exact model snapshot;
- API endpoint;
- API/SDK version;
- generation parameters;
- Python version;
- `openai` package version;
- `tiktoken` version;
- tokenizer encoding;
- data-collection dates.

Current verified values:

| Item | Value |
| --- | --- |
| Provider | OpenAI |
| Model snapshot | `gpt-5.5-2026-04-23` |
| Tokenizer encoding | `o200k_base` |
| `tiktoken` version | `0.14.0` |
| Temperature | `0` |
| Reasoning effort | `none` |
| Python version | `3.13.9` |
| `openai` SDK version | `3.8.0` |

[decided 2026-09-10] The experiment is run in the conda base environment (Anaconda). The `openai` and `tiktoken` packages are not upgraded until data collection is complete.

API keys are not stored in the repository. The project API key is accessed through a local environment variable.


Sources:

- Lin, Z. (2025). A validity-guided workflow for robust large language model research in psychology.
- OpenAI. (2026). tiktoken: A fast BPE tokenizer for use with OpenAI's models. GitHub.