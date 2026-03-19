## Strategies

**Strategy 1: Full CV + LLM**
Give the whole cv and the question to the model, and let it answer directly.

**Strategy 2: Retrieve Section, then LLM**
First find the most relevant part of the cv, then give that part plus the question to the model.

**Strategy 3: RAG System**
Use retrieval-augmented generation to pull relevant cv content while answering.

**Strategy 4: Layout-Aware Model**
Use a model that reads both the cv text and the visual page structure.

**Strategy 5: Structured JSON Pipeline**
First convert the cv into structured JSON fields, then answer questions from that structured representation.

## Experiments

**Experiment 1: Structured Field Extraction**
Test how well each strategy can extract specific cv fields such as GPA, skills, publications, education, or work history.

**Experiment 2: CV QA Accuracy**
Test how accurately each strategy can answer the predefined questions about each cv.

**Experiment 3: Retrieval Strategy Impact**
Compare direct answering, retrieve-then-answer, and RAG to see whether retrieval improves answer quality and efficiency.

**Experiment 4: Explainability and Calibration**
Test whether the model can justify its answers with valid evidence and whether its confidence matches how often it is actually correct.

**Experiment 5: Model Size vs Performance**
Compare smaller and larger models to see whether increased model size leads to better results worth the added time or cost.

**Experiment 6: Context Ablation**
Test how performance changes when the model is given different amounts of cv context, such as the full cv, top 1 chunk, or top 3 chunks.

## Experiment matrix

| Exp    | Plain English                                                       | Use these strategies                                                      | Main metrics                                           |
| ------ | ------------------------------------------------------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------ |
| **E1** | Extract fields like GPA, skills, publications                       | **S1, S2, S3, S4, S5**                                                    | Precision, Recall, **F1**, field fill rate             |
| **E2** | Answer the 30 cv questions                                      | **S1, S2, S3, S4, S5**                                                    | **Exact Match**, F1, semantic match, latency, cost     |
| **E3** | Check whether retrieval helps                                       | **S1, S2, S3**                                                            | Accuracy, latency, cost                                |
| **E4** | Check whether answers are explainable and confidence is trustworthy | **S1, S2, S3, S5**                                                        | Rationale accuracy, faithfulness, **ECE**, Brier score |
| **E5** | Check whether bigger models are worth it                            | **Run inside one strategy at a time**: mainly **S3**, then maybe S1/S2/S5 | Accuracy, latency, cost                                |
| **E6** | Check how much context is actually needed                           | **S1, S2, S3, S5**                                                        | Accuracy vs context size, latency, token/cost          |

## Core data points (Output Schema) to generate for almost every run

For each **cv + question + strategy + model**, generate:

- **cv_id**
- **question_id**
- **question_category**
- **question_text**
- **ground_truth_answer**
- **strategy**
- **model_name**
- **predicted_answer**
- **confidence_score**
- **rationale**
- **latency**
- **input_tokens**
- **output_tokens**
- **estimated_cost**
- **normalized_answer**
- **score_exact_match**
- **score_f1 / overlap**
- **semantic_score**
- **human_eval_score** _(for a subset if full manual grading is too much)_
- **error_type**

That becomes your master results table.

## Then what changes by experiment

### Experiment 1: Structured Field Extraction

Extra data points:

- **field_name**
- **predicted_field_value**
- **ground_truth_field_value**
- **field_match**
- **field_precision / recall / f1**

This is more field-level than question-level.

### Experiment 2: CV QA Accuracy

Main data points:

- question
- answer
- confidence
- rationale
- latency
- accuracy scores

This is your most standard setup.

### Experiment 3: Retrieval Strategy Impact

Add retrieval-specific columns:

- **retrieved_chunk_ids**
- **retrieved_text**
- **num_chunks_used**
- **retrieval_score**
- **retrieval_hit** _(did retrieved chunk actually contain the answer?)_

This lets you analyze whether failure came from bad retrieval or bad answering.

### Experiment 4: Explainability and Calibration

This is where **rationale** really matters.

Add:

- **rationale_supported_by_cv**
- **rationale_quality_score**
- **confidence_bin**
- **correct_or_not**
- **calibration_error contribution**

So yes, here the model should definitely output:

- **answer**
- **confidence**
- **rationale**

### Experiment 5: Model Size vs Performance

Mostly same columns, but compare across:

- **model_size**
- **parameter_count** or size label
- **latency**
- **cost**
- **accuracy**

This one is more about aggregation than new row fields.

### Experiment 6: Context Ablation

Add:

- **context_type** _(full cv, top 1 chunk, top 3 chunks, etc.)_
- **context_length**
- **tokens_in_context**

This lets you plot accuracy vs context amount.

## So yes, your intuition is right

Most experiments will reuse the **same base outputs**:

- answer
- confidence
- rationale
- time
- scores

Then each experiment adds a few special columns.

## Best practical design

Think in **two layers**:

### Base output schema

Used for all runs:

- answer
- confidence
- rationale
- latency
- cost
- scores

### Experiment-specific schema

Used only when needed:

- retrieval columns for E3
- field columns for E1
- calibration columns for E4
- context columns for E6

## Clean final view

For every run, the model should ideally output:

- **answer**
- **confidence**
- **rationale**

Then your evaluation pipeline adds:

- **accuracy scores**
- **semantic scores**
- **latency/cost**
- **experiment-specific metrics**

That is the right foundation.
