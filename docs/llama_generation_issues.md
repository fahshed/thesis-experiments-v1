# Llama-2-13B Model Generation Issues

## Overview
During the execution of experiment `s1e2` using the `meta-llama/Llama-2-13b-chat-hf` model, the generated outputs exhibited severe hallucinations, primarily characterized by infinite text repetition (e.g., repeatedly outputting "the the the the the ends the ends the").

## Root Causes

1. **Missing Chat Templates (`[INST]` tags)**
   The `Llama-2-13b-chat-hf` model is instruction-tuned and expects prompts to be formatted using specific conversation tags (`[INST]` and `<<SYS>>`). In the current implementation (e.g., in `Strategy1FullCV`), prompts are passed as raw text. Without the appropriate chat template structure, the model fails to recognize the input as an instruction, often resulting in out-of-distribution behavior and generation loops.

2. **Greedy Decoding & Missing Repetition Penalty**
   The generation pipeline currently employs greedy decoding (`do_sample=False`) without any repetition penalty configuration (default is 1.0). Llama models are particularly susceptible to getting stuck in localized token loops when using greedy decoding unless a repetition penalty is applied.

## Recommended Solutions

* **Apply Chat Templates:** Format the prompt using the model's native `tokenizer.apply_chat_template` or manually structure the string to include the `[INST]` and `<<SYS>>` tags.
* **Adjust Generation Parameters:** Modify the `HuggingFaceLLM` configuration to include a `repetition_penalty` (typically between `1.1` and `1.2`) to actively penalize and break repetitive token loops.
