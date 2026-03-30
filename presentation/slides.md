# Benchmarking Open-Source LLMs on CV Question Answering Pipelines Using a Fixed Human-Annotated Dataset

**Fahim Morshed**
Master's Thesis Defense

Supervised by **Dr. Rahat Ibn Rafiq**

<!-- Date: TBD -->

---

# Agenda

1. **Motivation & Problem Statement**
2. **Background & Related Work**
3. **Dataset Creation & Annotation**
4. **System Architecture & Pipeline Strategies**
5. **Experiment Design**
6. **Evaluation Framework**
7. **Results & Analysis**
8. **Application: Decision Support System**
9. **Limitations & Future Work**
10. **Conclusion**

---

# Motivation

- Organizations process **hundreds to thousands** of CVs for hiring decisions
- Manual CV screening is **time-consuming, inconsistent, and subjective**
- Open-source LLMs are rapidly improving but **lack standardized benchmarks** for CV understanding tasks
- Existing NLP benchmarks (SQuAD, TriviaQA) don't capture the **structured + unstructured nature of CVs**
- No publicly available **human-annotated CV QA dataset** exists for systematic evaluation

> **Gap:** How well can open-source LLMs extract and reason over information in real-world CVs — and which pipeline strategy works best?

---

# Research Questions

1. **How do different retrieval strategies** (full-context, keyword retrieval, semantic RAG) affect CV question-answering accuracy?

2. **How do open-source LLMs of varying sizes** (1.5B, 7B, 13B parameters) compare on CV QA tasks in terms of accuracy, reasoning quality, and efficiency?

3. **What types of questions and error patterns** emerge across different pipeline configurations?

4. **How well do model-generated confidence scores and rationales** correlate with actual answer correctness across models and strategies?

---

# Background: LLMs for Information Extraction

- **Large Language Models** have shown strong capabilities in reading comprehension and information extraction
- Open-source models (Mistral, LLaMA, Qwen) now approach proprietary model quality for many tasks
- Key challenge: **context window management** — CVs vary in length and structure
- Two paradigms:
  - **Full-context:** Feed entire document to the model
  - **Retrieval-Augmented Generation (RAG):** Retrieve relevant sections first, then generate

---

# Background: CV as a Document Type

- CVs are **semi-structured documents** — mix of free text, tables, lists, and formatting
- Information is distributed across sections: education, experience, skills, publications, etc.
- Questions fall into two types:
  - **Entity/Numeric:** "What is the applicant's GPA?" (precise extraction)
  - **Descriptive:** "Describe the applicant's research experience" (reasoning + synthesis)
- PDF extraction introduces **noise** — lost formatting, merged columns, OCR artifacts

---

# Related Work

| Area | Key Work | Gap |
|------|----------|-----|
| Reading Comprehension | SQuAD, TriviaQA | General QA, not CVs |
| Document QA | DocVQA, InfographicsVQA | Visual docs, not CV QA |
| Resume Parsing | Resume-NER, rule-based NER | Extraction, not QA |
| RAG Systems | REALM, Lewis et al. | General retrieval, not CV QA |
| LLM Benchmarks | MMLU, HumanEval | General reasoning, not document QA |

**Our contribution:** A human-annotated benchmark on real CV PDFs for end-to-end CV QA.

---

# Dataset Creation: Overview

<!-- This is the pipeline for building the dataset -->

```
100 Real CVs Collected
        │
        ▼
30 Questions Designed (across categories & answer types)
        │
        ▼
ChatGPT generates initial answers (CV + questions → structured output)
        │
        ▼
Human Evaluation & Annotation (verify/correct every answer)
        │
        ▼
3,000 Human-Annotated QA Pairs (100 CVs × 30 questions)
        │
        ▼
Subset of 50 CVs (1,500 records) used for experiments
```

---

# Dataset Creation: CV Collection

- **Sources:**
  - Publicly available CVs from personal websites
  - Voluntarily shared by peers, classmates, and colleagues
- **100 CVs** collected in total
- Diverse backgrounds: academia, industry, varying experience levels
- All CVs in **PDF format** — real-world documents, not synthetic
- No standardized template — reflects real-world variability in formatting and structure

---

# Dataset Creation: Question Design

**30 questions** spanning multiple dimensions:

| Category | Example Questions |
|----------|------------------|
| **Personal Information** | Full name, contact details |
| **Education** | Institutions attended, GPA, degrees |
| **Professional Experience** | Current employer, years of experience |
| **Skills** | Programming languages, technical skills |
| **Research & Publications** | Publication count, research areas |
| **Achievements** | Awards, certifications |

**Answer Types:** Entity/Numeric, Descriptive

---

# Dataset Creation: Annotation Process

1. **Initial Generation:** Each CV + 30 questions fed to ChatGPT UI
   - Output: structured array of answers
   - Scripted into CSV format using Python utility

2. **Human Evaluation & Annotation:**
   - Every generated answer manually verified against the source CV
   - Corrections made where ChatGPT hallucinated or missed information
   - Ensures **ground truth quality** for benchmark evaluation

3. **Final Dataset:**
   - 100 CVs × 30 questions = **3,000 annotated QA pairs**
   - Experiment subset: **50 CVs × 30 questions = 1,500 records**

---

# Dataset Statistics

| Metric | Value |
|--------|-------|
| Total CVs | 100 |
| Questions per CV | 30 |
| Total QA pairs | 3,000 |
| Experiment subset (CVs) | 50 |
| Experiment subset (QA pairs) | 1,500 |
| Question categories | 6 |
| Answer types | Entity/Numeric, Descriptive |
| CV format | PDF (real-world, no standardized template) |

<!-- TODO: Add distribution charts — questions per category, answer type distribution -->

---

# System Architecture

```
                    ┌─────────────────────────────────────┐
                    │           Generate Phase             │
                    │                                     │
  Dataset ────────► │  Strategy ──► LLM ──► JSON Parse   │ ──► Results CSV
  (CV + QnA)       │  (S1/S2/S3)   │       │             │
                    │               │       ▼             │
                    │               │  predicted_answer   │
                    │               │  confidence_score   │
                    │               │  rationale          │
                    └───────────────│─────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │          Evaluate Phase              │
                    │                                     │
                    │  Phase 1: Automatic Metrics          │
                    │  (Exact Match, F1, Overlap)          │
                    │                                     │
                    │  Phase 2: LLM Judge (Gemini)         │
                    │  (Correct/Partial/Incorrect)         │
                    └─────────────────────────────────────┘
```

---

# Strategy 1: Full CV Context

```
┌──────────┐     ┌──────────────────────┐     ┌─────────┐
│  CV PDF  │────►│  Full Text Extraction │────►│   LLM   │──► Answer
└──────────┘     │  (pypdf)             │     │ Prompt: │
                 └──────────────────────┘     │ System + │
                                              │ Full CV  │
┌──────────┐                                  │ + Question│
│ Question │─────────────────────────────────►│          │
└──────────┘                                  └─────────┘
```

- **Approach:** Entire CV text injected into the prompt
- **Pros:** Maximum context, no information loss from retrieval
- **Cons:** Longer prompts, higher latency, may exceed context window for large CVs
- **Best for:** Questions requiring cross-section reasoning

---

# Strategy 2: Keyword-Based Retrieval

```
┌──────────┐     ┌─────────────┐     ┌──────────────┐     ┌─────────┐
│  CV PDF  │────►│  Chunk Text │────►│  Keyword     │────►│   LLM   │──► Answer
└──────────┘     │  (500 words)│     │  Overlap     │     │ Prompt: │
                 └─────────────┘     │  Scoring     │     │ System + │
                                     └──────────────┘     │ Chunk(s) │
┌──────────┐                              │               │ + Question│
│ Question │──────────────────────────────┘               │          │
└──────────┘                                              └─────────┘
```

- **Approach:** CV chunked into 500-word segments; rank by keyword overlap with question
- **Pros:** Reduced prompt size, focused context
- **Cons:** Keyword matching may miss semantically relevant sections
- **Retrieval:** Lexical (word overlap scoring)

---

# Strategy 3: Semantic RAG

```
┌──────────┐     ┌─────────────┐     ┌──────────────┐     ┌─────────┐
│  CV PDF  │────►│  Chunk Text │────►│  Sentence    │────►│   LLM   │──► Answer
└──────────┘     │  (500 words)│     │  Transformer │     │ Prompt: │
                 └─────────────┘     │  Embeddings  │     │ System + │
                                     │  (MiniLM)    │     │ Chunk(s) │
┌──────────┐     ┌─────────────┐     │              │     │ + Question│
│ Question │────►│  Embed      │────►│  Cosine Sim  │     │          │
└──────────┘     │  Question   │     └──────────────┘     └─────────┘
                 └─────────────┘
```

- **Approach:** Semantic embeddings (all-MiniLM-L6-v2) for chunks and questions
- **Cosine similarity** matching for retrieval
- **Pros:** Captures meaning beyond keyword overlap
- **Cons:** Embedding quality dependency, additional compute for embeddings
- **Caching:** Per-CV embedding cache for efficiency across questions

---

# Models Under Study

| Model | Parameters | Type | Key Characteristics |
|-------|-----------|------|---------------------|
| **Qwen2.5-1.5B** | 1.5B | Instruct | Smallest, fastest, resource-efficient |
| **Mistral-7B-Instruct-v0.3** | 7B | Instruct | Mid-size, strong instruction following |
| **LLaMA-2-13B-Chat** | 13B | Chat | Largest, most capable, highest cost |

**Why these models?**
- Represent a range of model sizes (1.5B → 7B → 13B)
- All open-source and locally deployable
- Cover different architecture families
- Enable analysis of **accuracy vs. efficiency tradeoffs**

---

# Experiment Design

**Primary Experiment: E2 — CV Question Answering Accuracy**

### Comparison 1: Strategy Comparison (fixed model: Mistral-7B)

| Run | Strategy | Model | Records |
|-----|----------|-------|---------|
| S1-E2-Mistral | Full CV | Mistral-7B | 1,500 |
| S2-E2-Mistral | Keyword Retrieval | Mistral-7B | 1,500 |
| S3-E2-Mistral | Semantic RAG | Mistral-7B | 1,500 |

### Comparison 2: Model Comparison (fixed strategy: S1 Full CV)

| Run | Strategy | Model | Records |
|-----|----------|-------|---------|
| S1-E2-Qwen | Full CV | Qwen-1.5B | 1,500 |
| S1-E2-Mistral | Full CV | Mistral-7B | 1,500 |
| S1-E2-LLaMA | Full CV | LLaMA-13B | 1,500 |

---

# Experiment Environment

### Hardware

| Component | Specification |
|-----------|--------------|
| **CPU** | <!-- TODO: Add CPU model --> |
| **GPU** | <!-- TODO: Add GPU model --> |
| **RAM** | <!-- TODO: Add RAM --> |
| **CUDA Version** | <!-- TODO: Add CUDA version --> |
| **OS** | <!-- TODO: Add OS --> |

### Controlled Conditions

- All experiments ran on the **same machine** in the **same state**
- **No parallel runs** — each experiment ran sequentially to ensure accurate latency measurements
- Models loaded with `torch.float16` precision on `cuda:0`
- **LLaMA-13B** pushed hardware to its limits — GPU utilization reached **99%** during inference, leading to occasional incoherent outputs due to memory pressure

---

# Evaluation Framework

### Phase 1: Automatic Metrics

| Metric | Description |
|--------|-------------|
| **Parseability** | % of responses with valid JSON output |
| **Exact Match** | Normalized string equality (0 or 1) |
| **F1 Score** | Token-level precision/recall |
| **Overlap** | Word overlap fraction with ground truth |

### Phase 2: LLM Judge (Gemini API)

| Judgment | Credit | Description |
|----------|--------|-------------|
| **Correct** | 1.0 | Answer matches ground truth |
| **Partial** | 0.5 | Partially correct or missing details |
| **Incorrect** | 0.0 | Wrong or unrelated answer |

- Also evaluates **rationale quality** (correct/partial/incorrect)
- Classifies **error types** (11 categories)

---

# Evaluation: Error Taxonomy

The Gemini judge classifies errors into **11 categories:**

| Error Type | Description |
|------------|-------------|
| `none` | No error — answer is correct |
| `not_answered` | Model failed to provide an answer |
| `format_issue` | Response format was incorrect |
| `wrong_entity` | Extracted wrong entity from CV |
| `wrong_numeric_value` | Incorrect numeric extraction |
| `wrong_boolean` | Incorrect yes/no answer |
| `missing_detail` | Correct direction but incomplete |
| `extra_unsupported_detail` | Added information not in CV |
| `contradiction_to_ground_truth` | Directly contradicts source |
| `invented_value_for_missing_ground_truth` | Hallucinated for N/A questions |
| `other` | Uncategorized errors |

---

# Results: Strategy Comparison — Summary Table

<!-- TODO: Fill with actual values after Gemini judge results -->

### S1 (Full CV) vs S2 (Keyword Retrieval) vs S3 (Semantic RAG)
*Model: Mistral-7B | Experiment: E2 QA Accuracy*

| Metric | S1 Full CV | S2 Keyword | S3 RAG |
|--------|-----------|------------|--------|
| Parseability | — | — | — |
| Strict Accuracy | — | — | — |
| Soft Accuracy | — | — | — |
| Avg F1 | — | — | — |
| Avg Overlap | — | — | — |
| Avg Latency (s) | — | — | — |

> **Finding:** <!-- TODO: 1-2 sentence takeaway on which strategy performed best and why -->

---

# Results: Strategy Comparison — Charts

<!-- TODO: Replace with actual charts -->

### Chart 1: Grouped Bar Chart — Accuracy Metrics by Strategy
<!-- CHART: X-axis = Strategy (S1, S2, S3), Y-axis = Score, Bars = Strict Accuracy, Soft Accuracy, F1 -->
<!-- PURPOSE: Visually compare which strategy yields the best answer quality -->

### Chart 2: Per-Category Accuracy by Strategy
<!-- CHART: Grouped bar or heatmap — X-axis = Question Category (6 categories), Groups = S1/S2/S3, Y-axis = Soft Accuracy -->
<!-- PURPOSE: Identify which categories benefit most from full context vs retrieval -->

### Chart 3: Error Type Distribution by Strategy
<!-- CHART: Stacked bar — X-axis = Strategy, Y-axis = Count, Stacks = Error types (not_answered, wrong_entity, missing_detail, etc.) -->
<!-- PURPOSE: Show whether retrieval strategies produce different failure modes -->

---

# Results: Model Comparison — Summary Table

<!-- TODO: Fill with actual values after Gemini judge results -->

### Qwen-1.5B vs Mistral-7B vs LLaMA-13B
*Strategy: S1 Full CV | Experiment: E2 QA Accuracy*

| Metric | Qwen (1.5B) | Mistral (7B) | LLaMA (13B) |
|--------|------------|-------------|-------------|
| Parseability | — | — | — |
| Strict Accuracy | — | — | — |
| Soft Accuracy | — | — | — |
| Avg F1 | — | — | — |
| Avg Overlap | — | — | — |
| Avg Latency (s) | — | — | — |
| Avg Input Tokens | — | — | — |
| Avg Output Tokens | — | — | — |

> **Finding:** <!-- TODO: 1-2 sentence takeaway on model size vs accuracy tradeoff -->

---

# Results: Model Comparison — Charts

<!-- TODO: Replace with actual charts -->

### Chart 4: Grouped Bar Chart — Accuracy Metrics by Model
<!-- CHART: X-axis = Model (Qwen, Mistral, LLaMA), Y-axis = Score, Bars = Strict Accuracy, Soft Accuracy, F1 -->
<!-- PURPOSE: Direct visual comparison of model capabilities -->

### Chart 5: Accuracy vs Model Size
<!-- CHART: Line/scatter plot — X-axis = Parameter count (1.5B, 7B, 13B), Y-axis = Soft Accuracy -->
<!-- PURPOSE: Show scaling behavior — is bigger always better? Note LLaMA's GPU memory pressure -->

### Chart 6: Per-Category Accuracy by Model
<!-- CHART: Heatmap — Rows = 6 question categories, Columns = 3 models, Cells = Soft Accuracy (color-coded) -->
<!-- PURPOSE: Reveal which categories each model excels at or struggles with -->

---

# Results: Per-Category Deep Dive

<!-- TODO: Fill with actual values -->

### Accuracy by Question Category (Best Configuration)

| Category | Best Strategy | Best Model | Soft Accuracy | Common Error |
|----------|--------------|------------|---------------|-------------|
| Personal Information | — | — | — | — |
| Education | — | — | — | — |
| Professional Experience | — | — | — | — |
| Skills | — | — | — | — |
| Research & Publications | — | — | — | — |
| Awards & Extracurricular | — | — | — | — |

### Chart 7: Radar Chart — Per-Category Accuracy
<!-- CHART: Radar/spider chart — 6 axes (one per category), Lines = S1/S2/S3 or Qwen/Mistral/LLaMA -->
<!-- PURPOSE: Show each configuration's strengths and weaknesses at a glance -->

---

# Results: Entity/Numeric vs Descriptive

<!-- TODO: Fill with actual values -->

### Accuracy by Answer Type

| Answer Type | S1 | S2 | S3 | Qwen | Mistral | LLaMA |
|-------------|----|----|-----|------|---------|-------|
| Entity/Numeric | — | — | — | — | — | — |
| Descriptive | — | — | — | — | — | — |

### Chart 8: Grouped Bar — Accuracy by Answer Type × Strategy
<!-- CHART: X-axis = Answer Type, Groups = S1/S2/S3, Y-axis = Soft Accuracy -->
<!-- PURPOSE: Show if retrieval strategies impact factual extraction vs reasoning differently -->

### Chart 9: Grouped Bar — Accuracy by Answer Type × Model
<!-- CHART: X-axis = Answer Type, Groups = Qwen/Mistral/LLaMA, Y-axis = Soft Accuracy -->
<!-- PURPOSE: Show if larger models help more with descriptive reasoning or entity extraction -->

---

# Results: Error Analysis

<!-- TODO: Fill with actual error distribution data -->

### Chart 10: Stacked Bar — Error Types by Strategy
<!-- CHART: X-axis = Strategy (S1, S2, S3), Y-axis = Count, Stacks = error types -->
<!-- PURPOSE: Identify strategy-specific failure modes (e.g., more "not_answered" in retrieval strategies?) -->

### Chart 11: Stacked Bar — Error Types by Model
<!-- CHART: X-axis = Model (Qwen, Mistral, LLaMA), Y-axis = Count, Stacks = error types -->
<!-- PURPOSE: Identify model-specific failure patterns (e.g., more hallucination in smaller models?) -->

### Chart 12: Horizontal Bar — Top Error Types Overall
<!-- CHART: Horizontal bar — Y-axis = Error type, X-axis = Count, sorted descending -->
<!-- PURPOSE: Quick overview of most common failure modes across all experiments -->

---

# Results: Confidence Score Analysis

<!-- TODO: Fill with actual data -->

### How well do models calibrate their confidence?

### Chart 13: Box Plot — Confidence Score Distribution by Model
<!-- CHART: Box plot — X-axis = Model, Y-axis = Confidence Score (0-1) -->
<!-- PURPOSE: Show if models are overconfident — do they report high confidence regardless of correctness? -->

### Chart 14: Confidence vs Correctness
<!-- CHART: Grouped bar — X-axis = Confidence bins (0-0.5, 0.5-0.7, 0.7-0.9, 0.9-1.0), Y-axis = Actual accuracy within bin -->
<!-- PURPOSE: Calibration analysis — does higher confidence actually mean higher accuracy? -->

### Chart 15: Confidence Distribution by Judgment
<!-- CHART: Overlapping histogram or violin plot — X-axis = Confidence, Groups = Correct/Partial/Incorrect -->
<!-- PURPOSE: Visualize separation between confidence of correct vs incorrect answers -->

---

# Results: Rationale Quality

<!-- TODO: Fill with actual data -->

### Does the model explain its answers well?

| Rationale Judgment | S1 | S2 | S3 | Qwen | Mistral | LLaMA |
|-------------------|----|----|-----|------|---------|-------|
| Correct | — | — | — | — | — | — |
| Partial | — | — | — | — | — | — |
| Incorrect | — | — | — | — | — | — |

### Chart 16: Stacked Bar — Rationale Quality by Model
<!-- CHART: X-axis = Model, Y-axis = %, Stacks = Correct/Partial/Incorrect rationale -->
<!-- PURPOSE: Show which models provide better explanations alongside their answers -->

### Chart 17: Answer Correctness vs Rationale Correctness
<!-- CHART: Confusion-style heatmap — Rows = Answer judgment, Columns = Rationale judgment, Cells = count -->
<!-- PURPOSE: Can a model get the right answer with wrong reasoning, or vice versa? -->

---

# Results: Latency & Efficiency

<!-- TODO: Fill with actual data -->

### Computational Cost Comparison

| Configuration | Avg Latency (s) | Avg Input Tokens | Avg Output Tokens | Total Runtime |
|--------------|-----------------|------------------|-------------------|---------------|
| S1 + Mistral | — | — | — | — |
| S2 + Mistral | — | — | — | — |
| S3 + Mistral | — | — | — | — |
| S1 + Qwen | — | — | — | — |
| S1 + LLaMA | — | — | — | — |

### Chart 18: Box Plot — Latency Distribution by Configuration
<!-- CHART: Box plot — X-axis = Configuration, Y-axis = Latency (seconds) -->
<!-- PURPOSE: Show latency spread, outliers (especially LLaMA's GPU-constrained runs) -->

### Chart 19: Scatter Plot — Soft Accuracy vs Avg Latency
<!-- CHART: Scatter — X-axis = Avg Latency, Y-axis = Soft Accuracy, Points = each configuration labeled -->
<!-- PURPOSE: Visualize the accuracy-efficiency tradeoff — find the "sweet spot" -->

---

# Application: Decision Support System

This research builds upon a **real-world application** developed during the Graduate Assistantship:

- **Admission Assistant**
  - Full-stack platform: Next.js + Python + FastAPI
  - Processes CVs and Statements of Purpose
  - Uses open-source models (Mistral, LLaMA) via Hugging Face
  - Ranking logic translates qualitative criteria into structured AI prompts
  - Interactive dashboard for exploring applicant qualifications

- **Connection to thesis:**
  - Application motivated the need for systematic benchmarking
  - Thesis findings inform which models and strategies to deploy
  - Benchmark dataset enables ongoing evaluation of system improvements

---

# Discussion: Key Findings

<!-- TODO: Update with actual findings after results analysis -->

1. **Strategy impact:** How much does retrieval strategy matter compared to model choice?

2. **Model size vs accuracy:** Is bigger always better? Where does the sweet spot lie? How did LLaMA's GPU memory pressure affect results?

3. **Error patterns:** Are certain question types systematically harder? Do models fail differently?

4. **RAG effectiveness:** Does semantic retrieval outperform simpler approaches for CV QA?

5. **Confidence calibration:** Do models know when they're wrong? How useful are self-reported confidence scores?

6. **Rationale quality:** Do correct answers come with correct reasoning? When do models get answers right for wrong reasons?

7. **Practical implications:** Which configuration offers the best accuracy-efficiency tradeoff for real-world deployment?

---

# Limitations

- **Hardware constraints:** LLaMA-13B pushed GPU to 99% utilization, causing occasional incoherent outputs due to memory pressure — results may improve on higher-end hardware
- **Dataset scope:** 100 CVs (50 in experiments) — limited diversity in domains and formats
- **Model selection:** Three models from a rapidly evolving landscape — findings may not generalize to newer architectures
- **PDF extraction:** pypdf-based extraction loses formatting information that visual models could leverage
- **Single-language:** English-only CVs and questions
- **Judge reliability:** Gemini-based evaluation itself may have biases or errors (mitigated by spot-checking)
- **Question design:** 30 fixed questions may not cover all real-world CV querying needs
- **No fine-tuning:** All models used in zero-shot setting — fine-tuned models may perform differently

---

# Future Work

- **Expand dataset:** More CVs, more question types, multi-language support
- **Visual document understanding:** Incorporate layout-aware models (e.g., LayoutLM) that can use formatting cues
- **Fine-tuning experiments:** Domain-specific fine-tuning on CV QA task
- **Newer models:** Evaluate emerging models (Mistral v0.4+, LLaMA 3, Qwen 2.5+, Phi-3)
- **Hybrid strategies:** Combine keyword and semantic retrieval
- **Human evaluation study:** Systematic inter-annotator agreement on judge quality
- **Production deployment:** Integrate findings into the decision support system
- **Cost analysis:** Detailed compute cost comparison for deployment planning

---

# Conclusion

- **Created** a novel human-annotated benchmark dataset of **3,000 CV QA pairs** (100 CVs × 30 questions)
- **Designed and implemented** a modular evaluation framework with **3 pipeline strategies** and **3 model sizes**
- **Evaluated** 1,500 records per configuration using both **automatic metrics** and **LLM-based judging**
- **Showed** that full-CV context is the strongest strategy for CV QA, while retrieval-heavy pipelines lose critical detail
- **Established** Mistral-7B as the best balance of accuracy and efficiency across tested configurations
- **Analyzed** the main failure patterns, especially missing detail, weak confidence calibration, and category-level difficulty differences
- **Demonstrated** practical applicability through connection to a real-world decision support system

> This work moves CV QA from trial-and-error toward evidence-based system design, creating a strong path to more reliable and scalable decision support.

---

<!-- _class: lead -->
<!-- _paginate: false -->

# Thank You

## Questions?

**Fahim Morshed**
Supervised by **Dr. Rahat Ibn Rafiq**

<!-- Contact info here if desired -->
