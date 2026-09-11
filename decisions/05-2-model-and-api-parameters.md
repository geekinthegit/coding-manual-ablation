## 5.2 Model and API parameters

### 5.2.1 Model selection and version control

[decided 2026-09-09; originally proposed 2026-09-08; token-verification scope clarified 2026-09-11]

The model must satisfy two requirements.

1. Token-level verification of controlled text input  
   Section 3.2.3 requires condition-to-condition verification of token counts and downstream positions within the researcher-constructed text input. The selected model must therefore have a compatible tokenizer that allows this text to be tokenized and its token-ID sequence inspected locally. This requirement does not assume that the provider's complete internal API serialization can be reconstructed locally. Compatibility was verified locally on 2026-09-09 using `tiktoken 0.14.0`. The call `encoding_for_model("gpt-5.5-2026-04-23")` returned `o200k_base`, and the tokenizer successfully returned a token-ID sequence for test text. This verifies access to a compatible tokenizer for the local checks specified in Section 3.2.3. It does not itself constitute verification of the final experimental inputs, which will be performed after the endpoint, message structure, output-format configuration, and placeholder instances are fixed.
   
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

The same snapshot is used for all study-related API calls, including tool validation, the pilot, the main experiment, and the names-only diagnostic.

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
- openai SDK version;
- generation parameters;
- Python version;
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

[decided 2026-09-10]
The experiment is run in the conda base environment (Anaconda). Python, `openai`, and `tiktoken` are not upgraded or otherwise changed until data collection is complete.

API keys are not stored in the repository. The project API key is accessed through a local environment variable.

Package versions are re-verified immediately before data collection, and the calling script records the openai and tiktoken versions with every run log.

### 5.2.4 Final input construction and token verification

[proposed 2026-09-11]

Before experimental data collection, the API endpoint, message structure, output-format configuration, and all other request-level settings will be fixed and applied identically across conditions.

Verification will then be performed on the actual researcher-constructed text inputs used for the baseline and replacement conditions. For every replacement instance, the verification script will confirm the replacement token count, the token index of the first retained content following the replacement, and the total token count of the constructed text input relative to baseline.

The verification concerns the text representation under direct control of the study. Provider-internal serialization tokens that are not exposed through the local tokenizer are not treated as directly observed. Request structure outside the manipulated text is instead controlled by holding the endpoint, message arrangement, output-format configuration, and other fixed API settings constant across conditions.

The verification script and per-instance results will be retained in the repository.

Status: final verification pending completion of the unresolved endpoint, output-format, and placeholder specifications.


Sources:

- Lin, Z. (2025). A validity-guided workflow for robust large language model research in psychology.
- OpenAI. (2026). tiktoken: A fast BPE tokenizer for use with OpenAI's models. GitHub.