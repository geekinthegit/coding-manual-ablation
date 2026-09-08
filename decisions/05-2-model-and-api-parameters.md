## 5.2 Model and API parameters

### 5.2.1 Model selection and version control

[proposed 2026-09-08]

The model must satisfy two requirements.

1. Token-sequence-level verification  
   Section 3.2.3 requires local verification of the token count of each replacement span and the token positions of unchanged content following that span. The selected model must therefore allow the model-specific token-ID sequence to be reproduced and inspected locally.

2. Fixed model version  
   The model version must remain stable throughout data collection. Provider-side model updates can alter model behavior and threaten replicability; the exact model version, API parameters, endpoint, and collection dates must therefore be fixed or recorded (Lin, 2025).

Two model classes satisfy these requirements:

- a pinned open-weight model with its tokenizer;
- an OpenAI dated snapshot with a compatible `tiktoken` encoding.

OpenAI's `tiktoken` provides model-specific encodings through `encoding_for_model()` and returns token-ID sequences that can be inspected locally. The compatibility of the specific snapshot selected for the experiment will be verified before the pilot.

An OpenAI dated snapshot is preferred for the present project. A pinned open-weight model also satisfies the methodological requirements but requires additional management and documentation of the model checkpoint, inference engine, quantization settings, hardware environment, and software configuration. API execution reduces this implementation burden while retaining version pinning and local token-sequence verification.

Alternatives not adopted:

| Option | Reason |
|---|---|
| Moving API model alias | The underlying model version may change during data collection. |
| Web interface | Exact model version and generation parameters may be unavailable or insufficiently controllable. |
| API model without token-sequence-level access | Cannot implement the token-position checks required by Section 3.2.3. |
| Pinned open-weight model | Meets the requirements but adds inference-environment and documentation burden relative to the project timeline. |

The exact OpenAI dated snapshot and corresponding `tiktoken` encoding have not yet been selected. [unresolved]

The selected snapshot will be fixed before the pilot and used unchanged for the main experiment. Model selection will not be changed on the basis of pilot agreement results.

Sources:

- Lin, Z. (2025). A validity-guided workflow for robust large language model research in psychology.
- OpenAI. (2026). tiktoken: A fast BPE tokenizer for use with OpenAI's models. GitHub.