# Resume QA Strategy Pipeline Implementation Plan

This document outlines the architecture for a simple, modular, and versioned strategy pipeline for running Resume Q&A experiments, starting with Strategies 1 & 2 and Experiments 1 & 2, using Hugging Face models.

## Architecture Guidelines
- **Simplicity & Modularity**: Each component (Data Loading, LLM inference, Strategy logic, Evaluator, Logger) will be isolated in its own module.
- **Plug-and-Play**: Interfaces (`BaseStrategy`, `BaseExperiment`, `BaseLLM`) will enforce consistent inputs and outputs.
- **Versioning**: Each run should output directly to a CSV aligned with the `master_resume_qa_results_template.csv`.
- **Local Transformers**: The pipeline will use the `transformers` library locally to run HuggingFace open-source models.

## Proposed Component Structure

### 1. Data Models (`src/core/schemas.py`)
Use `pydantic` or standard `dataclasses` to enforce strict shapes:
- `QARecord`: Represents a single row from `Aaron2.csv`.
- `RunResult`: Represents a single evaluated output row matching the master template.

### 2. LLM Abstraction (`src/llm/`)
- `BaseLLM`: interface demanding a `.generate(prompt, **kwargs)` method.
- `HuggingFaceLLM`: implementation wrapping the chosen HF model using local `transformers`.

### 3. Strategies (`src/strategies/`)
- `BaseStrategy`: interface with a `.run(resume_text, question)` method returning `(predicted_answer, confidence, rationale, context_used)`.
- **Strategy 1 (`strategy_1_full_resume.py`)**: Concatenates the full resume text and the question into the prompt.
- **Strategy 2 (`strategy_2_retrieve_section.py`)**: Uses a basic chunking or keyword-retrieval step to find the best snippet of the resume before calling the LLM.

### 4. Experiments (`src/experiments/`)
- `BaseExperiment`: interface defining how to iterate over questions and calculate metrics.
- **Experiment 1 (Structured Extraction)**: Evaluates strict field extraction (GPA, skills, etc.). Calculates Exact Match, F1, and Precision/Recall based on field values.
- **Experiment 2 (QA Accuracy)**: Evaluates normal QA, producing standard Accuracy, exact match, latency, and tokens.

### 5. Evaluation & Logging (`src/utils/`)
- `evaluation.py`: functions for computing Overlap, F1, Exact Match, etc.
- `logger.py`: a robust CSV writer that maps `RunResult` to the `master_resume_qa_results_template.csv`.

### 6. Main Entry Point (`run.py`)
A simple CLI or configuration-driven script that wires the components together:
```python
# Pseudo-code for run.py
llm = HuggingFaceLLM(model_name="meta-llama/Llama-3-8b")
strategy = Strategy1FullResume(llm=llm)
experiment = Experiment2QA(strategy=strategy)

dataset = load_dataset("dataset/")
results = experiment.run(dataset)
save_results(results, "results/run_001.csv")
```

## Verification Plan
### Automated Tests
- Unit tests against the exact match and F1 scoring functions in `evaluation.py`.
- Mock LLM responses to verify `Strategy1` and `Strategy2` formatting.
### Manual Verification
- We will perform a dry-run using a small subset of the dataset saving the output to a CSV.
- The resulting CSV will be visually inspected against the `master_resume_qa_results_template.csv` to ensure perfect column matching.
