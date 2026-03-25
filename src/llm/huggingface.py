from typing import Dict, Any
from transformers import pipeline
from src.llm.base import BaseLLM
import time

class HuggingFaceLLM(BaseLLM):
    """
    A concrete implementation of BaseLLM using local Hugging Face pipelines.
    """
    def __init__(self, model_name: str, device: str = "cpu", **kwargs):
        self._model_name = model_name
        # Using a very simple pipeline setup for demonstration.
        # In practice, device_map='auto', load_in_4bit, etc., can be passed in kwargs.
        self.pipe = pipeline(
            "text-generation", 
            model=model_name, 
            device=device,
            **kwargs
        )
        
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
        gen_kwargs.update(kwargs)
        
        # Generate text
        outputs = self.pipe(prompt, **gen_kwargs)
        
        # Pipeline output shape parsing
        if isinstance(outputs, list) and len(outputs) > 0:
            generated_text = outputs[0].get("generated_text", "")
        else:
            generated_text = str(outputs)
            
        latency = time.time() - start_time
        
        # NOTE: token counts would usually come from tokenizer explicit usage if needed,
        # but sticking to a simpler return structure for now.
        return {
            "text": generated_text.strip(),
            "latency": latency,
            "input_tokens": 0,   # Stub
            "output_tokens": 0,  # Stub
            "estimated_cost": 0.0 # Open source local models cost 0 in API fees
        }
