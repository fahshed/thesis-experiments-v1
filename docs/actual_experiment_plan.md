# Actual Experiment Plan

Based on the latest updates to the experiment design, here is the clear source of truth for the strategies, experiments, and the specific runs.

## Core Evaluation Plan

The primary goals for the actual experiment runs evaluate two main comparisons:

1. **Strategy Comparison**: Comparing `S1` vs `S2` vs `S3` on Experiment 2 (QA Accuracy) using the default `Mistral` model.
2. **Model Comparison**: Comparing `Qwen` vs `Mistral` vs `LLaMA` on Strategy 1 + Experiment 2 (QA Accuracy) to understand model performance dynamics (E5 analysis).

## Phase 1: Generation Runs

The immediate goal is to generate the data for the following 5 runs. All runs are based on **Experiment 2 (QA Accuracy)**.

### ✅ Completed

- **`s3e2`**: Strategy 3 (RAG) + Experiment 2 (QA Accuracy) — _[Default Model: `mistralai/Mistral-7B-Instruct-v0.3`]_
- **`s2e2`**: Strategy 2 (Retrieve Section) + Experiment 2 (QA Accuracy) — _[Default Model: `mistralai/Mistral-7B-Instruct-v0.3`]_
- **`s1e2 (CPU)`**: Strategy 1 (Full CV) + Experiment 2 (QA Accuracy) — _[Default Model: `mistralai/Mistral-7B-Instruct-v0.3`]_ (CPU run)

### 📋 Pending

- **`s1e2 (GPU)`**: Strategy 1 (Full CV) + Experiment 2 (QA Accuracy) — _[Default Model: `mistralai/Mistral-7B-Instruct-v0.3`]_ (GPU run)
- **`s1e2 (Qwen)`**: Strategy 1 (Full CV) + Experiment 2 (QA Accuracy) — using the **Qwen** model (run for E5 Model Size vs Performance analysis).
- **`s1e2 (LLaMA)`**: Strategy 1 (Full CV) + Experiment 2 (QA Accuracy) — using the **LLaMA** model (run for E5 Model Size vs Performance analysis).

---

## Phase 2: Evaluation & Analysis

Once the generations are complete, we will run evaluations on the generated data. Because all actual runs effectively use the E2 (QA Accuracy) framework, the evaluation pipeline will utilize a standard Base Output Schema.

### REQUIRED DATA SCHEMA

#### Phase 1: Generation Outputs

Generated directly during the execution of the experiments:

- **Identification:** `cv_id`, `question_id`, `question_category`, `question_text`, `ground_truth_answer`
- **Run Metadata:** `strategy`, `model_name`
- **Model Outputs:** `predicted_answer`, `confidence_score`, `rationale`
- **Performance Logs:** `latency`, `input_tokens`, `output_tokens`, `estimated_cost`
- _(For S3 / RAG only)_: `retrieved_chunk_ids`, `retrieved_text`, `num_chunks_used`

#### Phase 2: Evaluation Metrics

Computed strictly after Phase 1 is complete, by parsing the generation outputs:

- **Accuracy Scores:** `normalized_answer`, `score_exact_match`, `score_f1` (or overlap), `semantic_score`
- **Qualitative Analysis:** `human_eval_score` (optional, for a subset), `error_type` (categorized for incorrect answers)
