Yeah — you _do_ have enough for a thesis. The trick is to stop thinking of it as “build a huge system” and start thinking of it as “run a clean benchmark on a fixed dataset.”

Your current outline already points in that direction: it frames cv extraction/QA as a benchmark problem, compares multiple pipeline styles, and lists experiments around accuracy, latency, retrieval, explainability, and model size. But as written, it’s too wide for the time you have.

Here’s what I think:

## What your thesis should become

Not:

“Let’s compare every open-source, commercial, layout-aware, and RAG model.”

Instead:

**“A benchmark study of cv question answering pipelines using a fixed human-annotated dataset.”**

That sounds academic, controlled, and finishable.

You already have the core asset:

- 100 cvs
- 30 questions per cv
- 5 categories
- human-curated ground truth answers

That is **3,000 QA instances**, which is actually enough for a solid empirical study.

## The strongest thesis angle

The best angle is not just open-source vs commercial.

That alone can become a shallow “leaderboard” paper.

A better and more thesis-like question is:

**How do model choice and context strategy affect cv QA performance under practical constraints like accuracy, latency, and cost?**

That gives you three dimensions:

1. **Model type**
   open-source vs commercial
2. **Context strategy**
   full cv vs retrieved section vs structured extraction
3. **Evaluation dimensions**
   accuracy, latency, cost, faithfulness/error type

That is much more defensible.

---

# What to keep and what to cut

Your uploaded plan includes 5 research questions and a lot of model families, including layout-aware systems and multiple RAG models. That is good as a brainstorming document, but too ambitious now.

## Cut these for now

Unless you already have them working:

- LayoutLMv3 / Donut / FormNet / LiLT
- too many RAG systems
- model size sweep across many models
- deep calibration study
- rationale correctness as a major standalone experiment

These will eat your time.

## Keep these

- 1-step full-context QA
- 2-step retrieval QA
- maybe one structured extraction pipeline
- open-source vs commercial comparison
- accuracy + latency + cost
- per-category analysis
- error analysis

That is enough for a real thesis.

---

# A concrete thesis design you can actually finish

## Proposed thesis title

**Benchmarking CV Question Answering Pipelines: Accuracy, Latency, and Cost Trade-offs Across Open-Source and Commercial LLMs**

A shorter version:
**Benchmarking CV QA Pipelines Using Open-Source and Commercial LLMs**

---

## Core research questions

I’d reduce your RQs to **3 main ones**:

### RQ1

**How does QA accuracy differ between open-source and commercial LLMs on cv-based question answering?**

### RQ2

**How do different context strategies affect performance: full-cv prompting, retrieval-based prompting, and structured-extraction-based prompting?**

### RQ3

**What trade-offs exist among accuracy, latency, and cost across models and pipelines?**

That’s tight, practical, and enough.

If you want one optional fourth:

### RQ4

**Which question categories are most difficult across pipelines, and what types of errors occur most often?**

That adds depth without much extra implementation.

---

# Best experimental setup

## Dataset unit

Each sample is:

- one cv
- one question
- one ground-truth answer
- one category label

Total: **3,000 samples**

## Recommended pipelines

Do **3 pipelines max**:

### Pipeline A: Full CV + Question

Give the model the whole extracted cv text and the question.

This is your baseline.

### Pipeline B: Retrieved Section + Question

Split the cv into chunks/sections, retrieve the most relevant chunk(s), then ask the model using only retrieved context.

This tests whether retrieval helps.

### Pipeline C: Structured Extraction → QA

First extract key cv fields into a structured JSON or template, then answer questions from that structured representation.

This is very thesis-friendly because it shows a different reasoning pathway.

If time gets bad, drop C and keep only A and B.

---

## Recommended models

Do not compare 10 models. That will hurt you.

Do something like:

### Commercial

- GPT-4.1 / GPT-4o / equivalent available model
- Claude or Gemini if accessible

### Open-source

- one smaller open-source model
- one stronger open-source model

Example structure:

- 2 commercial
- 2 open-source

That’s enough.

If time is _very_ tight:

- 1 commercial
- 2 open-source

Still acceptable.

---

# How to make the study feel comprehensive

This is the important part.

You do **not** need more data.
You need **more thoughtful analysis** on the data you already have.

## 1. Evaluate by question category

Since you already have 5 categories, report performance per category.

That instantly makes the study richer:

- education questions
- experience questions
- skills questions
- research/publications questions
- personal/contact/background questions
  or whatever your real categories are

This lets you say things like:

- commercial LLMs were strongest overall but not uniformly better across all categories
- retrieval helped most for experience-related questions
- structured extraction performed best on factual fields but worse on descriptive questions

That becomes real analysis.

## 2. Evaluate by answer type

You can label questions as:

- short factoid
- list extraction
- count/number
- date/time
- descriptive summary
- yes/no inference

Even if you manually label the 30 question templates once, that’s manageable.

This adds another layer of analysis.

## 3. Do error analysis

This is what makes a benchmark feel like a thesis.

Create 5 error classes:

- missing answer
- partially correct answer
- hallucinated answer
- wrong normalization/format
- wrong evidence selection

Then analyze a subset of wrong predictions.

This gives you interpretability without building a fancy explainability pipeline.

## 4. Add efficiency analysis

Measure:

- average latency per question
- token usage
- estimated cost per 1000 questions

That makes the work practical and stronger than just “who got best score.”

## 5. Statistical testing

Even a simple paired comparison helps:

- McNemar test for paired accuracy differences
- bootstrap confidence intervals
- paired t-test or Wilcoxon for latency

You do not need advanced stats. Just enough to support claims.

---

# Metrics you should use

Avoid only one metric.

## Main metrics

- **Exact Match** for strict factual answers
- **Token-level F1** for partial overlap
- **Semantic similarity / LLM-as-judge only as secondary**
- **Latency**
- **Estimated cost**
- **Hallucination rate** or unsupported answer rate

## For extraction-style questions

If some questions map to known fields:

- precision
- recall
- F1

## For lists

Use set-based precision/recall/F1.

This will make your evaluation much more robust.

---

# Best thesis narrative

Here’s the story your thesis can tell:

CVs are semi-structured documents. Different QA pipelines may work differently depending on whether the question needs simple lookup, multi-line aggregation, or interpretation. Using a human-annotated dataset of 3,000 cv-question pairs, the thesis benchmarks open-source and commercial LLM pipelines under different context strategies and evaluates not only answer correctness but also latency, cost, and error behavior.

That sounds complete.

---

# A very practical thesis structure

## Chapter 1: Introduction

- motivation: cv QA matters for admissions/recruitment
- challenge: cvs are semi-structured and variable
- gap: unclear trade-off between open-source and commercial LLMs, especially under different context strategies
- contributions

## Chapter 2: Related Work

Keep it short.
Cover:

- information extraction from cvs
- document QA
- LLM-based QA
- retrieval-augmented QA
- open-source vs commercial evaluation

## Chapter 3: Dataset and Task Formulation

- 100 cvs
- 30 questions each
- 5 categories
- human-curated answers
- total 3,000 QA pairs
- answer types
- any preprocessing

## Chapter 4: Methods

- pipeline A
- pipeline B
- pipeline C if included
- models used
- prompting strategy
- retrieval method
- evaluation protocol

## Chapter 5: Results

- overall accuracy
- per-category results
- per-answer-type results
- latency
- cost
- error analysis

## Chapter 6: Discussion

- what worked and why
- where retrieval helps
- where commercial models justify cost
- where open-source models are sufficient
- limitations

## Chapter 7: Conclusion

- summary
- future work

---

# The most realistic final scope

If I were optimizing for **finishability + thesis quality**, I would choose this exact version:

## Final recommended scope

### Models

- 2 open-source
- 1 or 2 commercial

### Pipelines

- Full cv prompting
- Retrieval-based prompting

### Experiments

1. overall accuracy comparison
2. per-category comparison
3. latency and cost comparison
4. error analysis on failed cases

That’s it.

This is the safest thesis.

---

# What I would not do now

I would not spend time on:

- training your own model
- fine-tuning unless already almost done
- many layout-aware models
- too many commercial APIs
- complicated RAG frameworks
- large-scale calibration study
- rationale faithfulness unless you can do it cheaply

Those are “nice if you had 4 more months” ideas.

---

# A sharper thesis contribution statement

You need claims that sound stronger than “we compared some models.”

Use something like this:

1. We created a controlled benchmark for cv QA using 3,000 human-annotated question-answer pairs derived from 100 cvs.
2. We compared open-source and commercial LLMs under different context strategies.
3. We evaluated practical trade-offs across accuracy, latency, and cost.
4. We analyzed category-specific performance and common failure modes.

That is clean and publishable-sounding.

---

# One even better angle if you want originality

Instead of only “best model,” frame it as:

**When is a cheaper pipeline good enough?**

That is a strong practical thesis question.

Example:

- Commercial model is most accurate
- But retrieval + smaller open-source model may achieve near-competitive performance at much lower cost
- Therefore model choice should depend on deployment needs

That’s a useful contribution.

---

# My honest recommendation

Your best thesis is **not** “compare every possible system.”

Your best thesis is:

**A focused benchmark of cv QA pipelines using your existing annotated dataset, emphasizing accuracy, latency, cost, and category-wise error analysis.**

That is doable, defensible, and can still look comprehensive.

---

# If you want the cleanest thesis proposal right now

Use this:

## Thesis topic

**Benchmarking Open-Source and Commercial LLM Pipelines for CV Question Answering**

## Research questions

- How do open-source and commercial LLMs compare on cv QA accuracy?
- How does context strategy affect performance?
- What are the trade-offs among accuracy, latency, and cost?
- Which question categories remain challenging?

## Experiments

- Full-context QA
- Retrieval-based QA
- Optional structured extraction pipeline
- Per-category and per-error-type analysis

## Metrics

- exact match
- F1
- latency
- cost
- hallucination/error rate

That’s enough.

If you want, I can turn this into a **proper thesis proposal draft** with title, abstract, research questions, methodology, experiments, and expected contributions.
