from typing import Dict, Any
from transformers import pipeline
from src.llm.base import BaseLLM
import time

class HuggingFaceLLM(BaseLLM):
    """
    A concrete implementation of BaseLLM using local Hugging Face pipelines.
    """
    def __init__(self, model_name: str, **kwargs):
        self._model_name = model_name
        self.pipe = pipeline("text-generation", model=model_name, **kwargs)
        
    @property
    def model_name(self) -> str:
        return self._model_name

    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        start_time = time.time()
        
        # Merge default config with specific call kwargs
        gen_kwargs = {
            "max_new_tokens": 128,
            "return_full_text": False,
            "do_sample": False,
        }
        if "llama" in self.model_name.lower():
            gen_kwargs["max_new_tokens"] = 256
            gen_kwargs["repetition_penalty"] = 1.15
            gen_kwargs["do_sample"] = True
            gen_kwargs["temperature"] = 0.6
            gen_kwargs["top_p"] = 0.9
        gen_kwargs.update(kwargs)
        
        # Generate text
        outputs = self.pipe(prompt, **gen_kwargs)
        
        # Pipeline output shape parsing
        if isinstance(outputs, list) and len(outputs) > 0:
            generated_text = outputs[0].get("generated_text", "")
        else:
            generated_text = str(outputs)
            
        latency = time.time() - start_time
        
        # Calculate tokens using the pipeline's tokenizer
        input_tokens = 0
        output_tokens = 0
        if hasattr(self.pipe, "tokenizer") and self.pipe.tokenizer:
            # We use add_special_tokens=False to avoid double counting for outputs
            try:
                input_tokens = len(self.pipe.tokenizer.encode(prompt))
                output_tokens = len(self.pipe.tokenizer.encode(generated_text))
            except Exception:
                pass # fallback to 0 if tokenizer fails for some reason
        
        return {
            "text": generated_text.strip(),
            "latency": latency,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost": 0.0 # Open source local models cost 0 in API fees
        }
