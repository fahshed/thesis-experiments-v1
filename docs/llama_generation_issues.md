# Llama-2-13B Model Generation Issues

## Overview
During the execution of experiment `s1e2` using the `meta-llama/Llama-2-13b-chat-hf` model, the generated outputs exhibited severe hallucinations, primarily characterized by infinite text repetition (e.g., repeatedly outputting "the the the the the ends the ends the").

A second class of issue was also identified: ~50% of responses produced completely incoherent token streams (e.g., "erson", "astsodsumnLSDFerson", "LESodlaces theheursideodsule theossule") with no parseable content.

---

## Root Causes

### 1. Missing Chat Templates (`[INST]` tags)
The `Llama-2-13b-chat-hf` model is instruction-tuned and expects prompts to be formatted using specific conversation tags (`[INST]` and `<<SYS>>`). Without the appropriate chat template structure, the model fails to recognize the input as an instruction, often resulting in out-of-distribution behavior and generation loops.

### 2. Greedy Decoding & Missing Repetition Penalty
The generation pipeline employed greedy decoding (`do_sample=False`) without any repetition penalty (default 1.0). Llama models are particularly susceptible to getting stuck in localized token loops under greedy decoding unless a repetition penalty is applied.

### 3. Double BOS Token (primary cause of ~50% gibberish responses)
`_build_llama_prompt` manually prepended `<s>` to the prompt string. However, the HuggingFace `text-generation` pipeline tokenizes with `add_special_tokens=True` by default, which also prepends `<s>`. This caused the model to receive `<s><s>[INST]...` — a double BOS token — putting the model in an undefined attention state and producing completely incoherent output roughly half the time.

### 4. `max_new_tokens` Too Low for Llama
The default `max_new_tokens=128` was insufficient for Llama responses, which include a rationale field and tend to be more verbose. Hitting the generation limit mid-token can degrade output quality.

---

## Fixes Applied

| Issue | Fix |
|---|---|
| No `[INST]` formatting | Added `_build_llama_prompt` with `[INST] <<SYS>>...<</SYS>>...` structure |
| Repetition / greedy decoding | Set `repetition_penalty=1.15`, `do_sample=True`, `temperature=0.6`, `top_p=0.9` for Llama |
| Double BOS token | Removed manual `<s>` from `_build_llama_prompt` — pipeline adds it automatically |
| `max_new_tokens` too low | Set `max_new_tokens=256` in the Llama-specific block in `huggingface.py` |

**Files changed:**
- `src/strategies/strategy_1_full_cv.py` — removed `<s>` prefix from `_build_llama_prompt`
- `src/llm/huggingface.py` — added `max_new_tokens=256` to Llama-specific generation kwargs
