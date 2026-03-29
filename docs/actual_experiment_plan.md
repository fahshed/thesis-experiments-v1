# Actual Experiment Plan

Based on the latest updates to the experiment design, this document is the source of truth for the completed generation runs and the evaluation plan.

## Core Evaluation Plan

The primary goals for the actual experiment runs are two main comparisons:

1. **Strategy Comparison**: Compare `S1` vs `S2` vs `S3` on Experiment 2 (QA Accuracy) using the default `Mistral` model.
2. **Model Comparison**: Compare `Qwen` vs `Mistral` vs `LLaMA` on Strategy 1 + Experiment 2 (QA Accuracy).

## Phase 1: Generation Runs

All actual runs are based on **Experiment 2 (QA Accuracy)**.

### Completed

- `**s1e2 (Mistral GPU)`**: Strategy 1 (Full CV) + Experiment 2 (QA Accuracy) using `mistralai/Mistral-7B-Instruct-v0.3`
- `**s2e2 (Mistral)**`: Strategy 2 (Retrieve Section) + Experiment 2 (QA Accuracy) using `mistralai/Mistral-7B-Instruct-v0.3`
- `**s3e2 (Mistral)**`: Strategy 3 (RAG) + Experiment 2 (QA Accuracy) using `mistralai/Mistral-7B-Instruct-v0.3`
- `**s1e2 (Qwen)**`: Strategy 1 (Full CV) + Experiment 2 (QA Accuracy) using `Qwen`
- `**s1e2 (LLaMA)**`: Strategy 1 (Full CV) + Experiment 2 (QA Accuracy) using `LLaMA`

## Phase 2: Evaluation & Analysis

Once generation is complete, evaluation will combine three pieces:

1. **Automatic metrics** computed from generation outputs
2. **Gemini-as-judge evaluation** for answer quality and rationale quality
3. **Grouped analysis** by strategy, model, question category, and question type

Human review is not the main evaluation source. The main evaluator is the Gemini API, and a small subset of rows will be spot-checked manually for sanity.

### Judge-Based Evaluation Fields

These are evaluation-time fields added by the Gemini judge:

- `judge_model`
- `judge_prompt_version`
- `judge_raw_response`
- `judge_raw_response_parsable`
- `judge_answer_judgment`: `correct | partial | incorrect`
- `judge_answer_credit`: `1.0 | 0.5 | 0.0`
- `judge_rationale_judgment`: `correct | partial | incorrect`
- `judge_rationale_credit`: `1.0 | 0.5 | 0.0`
- `judge_error_type`

### Spot-Check Fields

These are optional fields for the small manually reviewed subset:

- `spotcheck_status`: `not_checked | confirmed | disagreed`
- `spotcheck_notes`

### Core Evaluation Outputs and Fields Used


| Evaluation output                               | Fields used                                                                                                    |
| ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| **Parseability rate**                           | `raw_response_parsable`                                                                                        |
| **Strict accuracy** (`% correct`)               | `judge_answer_judgment`                                                                                        |
| **Soft accuracy** (`% correct + 0.5 * partial`) | `judge_answer_judgment` or `judge_answer_credit`                                                               |
| **EM / F1 / overlap**                           | computed from `predicted_answer` + `ground_truth_answer`; stored in `score_exact_match`, `score_f1`, `overlap` |
| **Latency and token usage**                     | `latency`, `input_tokens`, `output_tokens`                                                                     |
| **Per-category breakdown**                      | `question_category` + whichever metric field is being summarized                                               |
| **Per-type breakdown**                          | `question_type` + whichever metric field is being summarized                                                   |
| **Confidence vs correctness**                   | `confidence_score` + `judge_answer_judgment` or `judge_answer_credit`                                          |
| **Error type distribution**                     | `judge_error_type`, usually filtered to rows where `judge_answer_judgment != correct`                          |
| **Rationale quality rate**                      | `judge_rationale_judgment` or `judge_rationale_credit`                                                         |


### Planned Reporting Slices

The final evaluation tables and charts should be reported:

- **Overall**
- **By strategy**
- **By model**
- **By question category**
- **By question type**
- **By confidence bands**

## Columns Required for Evaluation

These are the columns that must either already exist, be joined in, or be derived in order to power the evaluation pipeline.

### 1. Base identifiers

- `cv_id`
- `question_id`
- `strategy`
- `model_name`

### 2. Dataset metadata

- `question_category`
- `question_type`
- `question_text`
- `ground_truth_answer`

### 3. Generation outputs

- `raw_response`
- `raw_response_parsable`
- `predicted_answer`
- `confidence_score`
- `rationale`

### 4. Runtime and efficiency fields

- `latency`
- `lookup_latency`
- `llm_generation_latency`
- `input_tokens`
- `output_tokens`
- `estimated_cost`

### 5. Retrieval-specific fields

Needed for `S2` and `S3` analysis when available:

- `retrieved_chunk_ids`
- `retrieved_text`
- `num_chunks_used`

### 6. Automatic evaluation fields

- `normalized_answer`
- `score_exact_match`
- `score_f1`
- `overlap`

### 7. Gemini judge output fields

- `judge_model`
- `judge_prompt_version`
- `judge_raw_response`
- `judge_raw_response_parsable`
- `judge_answer_judgment`
- `judge_answer_credit`
- `judge_rationale_judgment`
- `judge_rationale_credit`
- `judge_error_type`

### 8. Optional spot-check fields

- `spotcheck_status`
- `spotcheck_notes`

### 9. Helpful derived helper fields

These do not all need to be permanently stored, but the evaluation code will likely operate on them:

- `confidence_bin`
- `is_answerable`
- `is_missing_ground_truth`
- `total_tokens`

## Required Data Schema

### Phase 1: Generation Outputs

Generated directly during experiment execution:

- **Identification**: `cv_id`, `question_id`, `question_category`, `question_text`, `ground_truth_answer`
- **Run metadata**: `strategy`, `model_name`
- **Model outputs**: `raw_response`, `predicted_answer`, `confidence_score`, `rationale`
- **Performance logs**: `latency`, `lookup_latency`, `llm_generation_latency`, `input_tokens`, `output_tokens`, `estimated_cost`
- **Generation quality check**: `raw_response_parsable`
- **Retrieval fields for `S2` / `S3` when available**: `retrieved_chunk_ids`, `retrieved_text`, `num_chunks_used`

### Phase 2: Evaluation Fields

Computed or joined after generation is complete:

- **Joined metadata**: `question_type`
- **Automatic metrics**: `normalized_answer`, `score_exact_match`, `score_f1`, `overlap`
- **Judge-based answer evaluation**: `judge_answer_judgment`, `judge_answer_credit`
- **Judge-based rationale evaluation**: `judge_rationale_judgment`, `judge_rationale_credit`
- **Judge metadata**: `judge_model`, `judge_prompt_version`, `judge_raw_response`, `judge_raw_response_parsable`
- **Confidence analysis inputs**: `confidence_score`, `judge_answer_judgment`, `judge_answer_credit`
- **Qualitative analysis**: `judge_error_type`
- **Optional manual spot-checks**: `spotcheck_status`, `spotcheck_notes`
