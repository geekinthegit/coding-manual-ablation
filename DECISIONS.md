# Decision Log

Structure overview. Each section links to its own file under `decisions/`.

## [1. Research Question](decisions/01-research-question.md)
- 1.1 RQ wording
- 1.2 Scope of claims

## 2. Data
- [2.1 Dataset selection and scope](decisions/02-1-dataset-selection-and-scope.md)
- [2.2 Development and held-out evaluation sets](decisions/02-2-development-and-held-out-sets.md)
- [2.3 Sampling design](decisions/02-3-sampling-design.md)

## 3. Experimental Design
- [3.1 Manual-component definition](decisions/03-1-manual-component-definition.md)
- [3.2 Placeholder specification](decisions/03-2-placeholder-specification.md)
- [3.3 Names-only diagnostic](https://github.com/geekinthegit/coding-manual-ablation/blob/main/decisions/03-3-names-only-diagnostic.md)

## [4. Measurement](decisions/04-measurement.md)
- 4.1 Human–LLM agreement
- [4.2 Repeated-call reliability](decisions/04-2-repeated-call-reliability.md)
- 4.3 Primary contrast / Δκ

## [5. Procedure](decisions/05-procedure.md)
- [5.1 Context specification](https://github.com/geekinthegit/coding-manual-ablation/blob/main/decisions/05-1-context-specification.md)
- [5.2 Model and API parameters](decisions/05-2-model-and-api-parameters.md)
* [5.3 Call unit and API request](https://github.com/geekinthegit/coding-manual-ablation/blob/main/decisions/05-3-call-unit-and-api-request.md)
- [5.4 Repetition and label aggregation](decisions/05-4-repetition-and-label-aggregation.md)
- [5.5 Role of the pilot](https://github.com/geekinthegit/coding-manual-ablation/blob/main/decisions/05-5-role-of-the-pilot.md)
## [6. Analysis](decisions/06-analysis.md)
- 6.1 Estimation of condition-specific κ
- 6.2 Estimation and uncertainty of Δκ
- 6.3 Non-independence
- 6.4 Robustness checks

## [7. Interpretive Boundaries](decisions/07-interpretive-boundaries.md)
- 7.1 Underdetermined causes of near-zero Δκ
- 7.2 Direction of development-set bias
- 7.3 Remaining threats / unresolved alternatives

## [8. Repository](decisions/08-repository.md)
- 8.1 Repository name and local structure
- 8.2 Data exclusion and licensing