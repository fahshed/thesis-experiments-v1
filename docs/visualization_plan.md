# Thesis Visualization & Diagram Plan

All visualizations are mapped to the four research questions. Charts will be generated via Python scripts; diagrams via Mermaid.

## Data Sources


| Config         | Directory                            | Strategy             | Model         | Records | Status |
| -------------- | ------------------------------------ | -------------------- | ------------- | ------- | ------ |
| S1 Mistral GPU | `results/s1e2 mistral (1-50) (gpu)/` | S1 Full CV           | Mistral-7B    | 1,500   | Judged |
| S1 Mistral CPU | `results/s1e2 mistral (1~45) (cpu)/` | S1 Full CV           | Mistral-7B    | 1,273   | Judged |
| S1 Qwen        | `results/s1e2 qwen (1-50)/`          | S1 Full CV           | Qwen-2.5-1.5B | 1,500   | Judged |
| S1 LLaMA i3    | `results/s1e2 llama (1-50) i3/`      | S1 Full CV           | LLaMA-2-13B   | 1,500   | Judged |
| S2 Mistral     | `results/s2e2 mistral (1-50)/`       | S2 Keyword Retrieval | Mistral-7B    | 1,500   | Judged |
| S3 Mistral     | `results/s3e2 mistral (1-50)/`       | S3 Semantic RAG      | Mistral-7B    | 1,500   | Judged |


**Notes:**

- Use LLaMA i3 run only (original run had generation issues)
- CPU run is a separate finding (hardware impact), not part of core model comparison

---

## RQ1: How do retrieval strategies affect accuracy?

*Comparison: S1 vs S2 vs S3, model fixed to Mistral-7B GPU*


| #   | Type        | Description                                                              |
| --- | ----------- | ------------------------------------------------------------------------ |
| 1   | Grouped bar | Soft accuracy, strict accuracy, parseability by strategy                 |
| 2   | Grouped bar | Per-category accuracy by strategy (6 categories)                         |
| 3   | Stacked bar | Error type distribution by strategy — shows *why* S2/S3 fail differently |
| 4   | Bar         | Latency + input tokens by strategy — the efficiency tradeoff             |


---

## RQ2: How do models of varying sizes compare?

*Comparison: Qwen 1.5B vs Mistral 7B vs LLaMA 13B, strategy fixed to S1 Full CV*


| #   | Type         | Description                                                 |
| --- | ------------ | ----------------------------------------------------------- |
| 5   | Grouped bar  | Soft accuracy, strict accuracy, parseability by model       |
| 6   | Scatter/line | Accuracy vs model size (1.5B, 7B, 13B) — "bigger != better" |
| 7   | Grouped bar  | Per-category accuracy by model                              |
| 8   | Stacked bar  | Error type distribution by model                            |
| 9   | Box/violin   | Latency distribution by model (shows LLaMA's long tail)     |
| 10  | Scatter      | Accuracy vs latency tradeoff (all 5 GPU configs as points)  |


---

## RQ3: What question types and error patterns emerge?

*Cross-cutting analysis across all configurations*


| #   | Type           | Description                                                              |
| --- | -------------- | ------------------------------------------------------------------------ |
| 11  | Heatmap        | Error type x config matrix (rows=error types, cols=configs)              |
| 12  | Grouped bar    | Accuracy by answer type (entity/numeric vs descriptive) x strategy       |
| 13  | Grouped bar    | Accuracy by answer type x model                                          |
| 14  | Radar/spider   | Per-category accuracy profile per config                                 |
| 15  | Horizontal bar | Top error types overall (sorted descending)                              |
| 16  | Boxplot        | Per-CV accuracy spread across configs — shows consistency, not just mean |


---

## RQ4: How well do confidence scores and rationales correlate with correctness?

*Cross-cutting analysis across all configurations*


| #   | Type                         | Description                                                            |
| --- | ---------------------------- | ---------------------------------------------------------------------- |
| 17  | Calibration plot             | Confidence bucket vs actual accuracy (diagonal = perfect calibration)  |
| 18  | Histogram                    | Confidence score distribution — the bimodal spike at 0.8-1.0           |
| 19  | Violin/overlapping histogram | Confidence distribution split by correct/partial/incorrect judgment    |
| 20  | Stacked bar                  | Rationale quality (correct/partial/incorrect) by model and strategy    |
| 21  | Heatmap (confusion-style)    | Answer judgment x rationale judgment — right answer with wrong reason? |


---

## Separate Finding: Hardware Impact (GPU vs CPU)

*Comparison: Mistral S1 on GPU vs CPU*

**Important:** The CPU run has 1,273 records (CVs 1–45) while the GPU run has 1,500 records (CVs 1–50). When comparing, clip the GPU dataset to only the matching CV/question pairs present in the CPU run so the comparison is apples-to-apples.

| #   | Type      | Description                                                                       |
| --- | --------- | --------------------------------------------------------------------------------- |
| 22  | Bar       | GPU vs CPU latency for Mistral S1 (2s vs 111s)                                    |
| 23  | Table/bar | Accuracy comparison GPU vs CPU (accuracy should be similar; latency is the story) |


---

## Diagrams (Mermaid)


| #   | Diagram                   | Purpose                                                           |
| --- | ------------------------- | ----------------------------------------------------------------- |
| D1  | System architecture       | Shows the 3 pipeline strategies as parallel flows                 |
| D2  | Evaluation pipeline       | Generate phase → JSON parse → Gemini judge → metrics aggregation  |
| D3  | Dataset creation pipeline | CV collection → ChatGPT generation → human annotation → benchmark |
| D4  | Experiment matrix         | Grid of model x strategy showing which combinations were run      |


---

## Summary Tables


| #   | Table                        | Purpose                                                                                                |
| --- | ---------------------------- | ------------------------------------------------------------------------------------------------------ |
| T1  | Master results               | One row per config: soft accuracy, strict accuracy, parseability, avg latency, avg input/output tokens |
| T2  | Per-category accuracy        | Rows = 6 question categories, columns = each config                                                    |
| T3  | Error taxonomy with examples | Definition + count for each of the 11 error types (methodology chapter)                                |


---

## Totals

- **23 charts** (Python/matplotlib)
- **4 diagrams** (Mermaid)
- **3 tables** (can be generated as CSV or LaTeX)

