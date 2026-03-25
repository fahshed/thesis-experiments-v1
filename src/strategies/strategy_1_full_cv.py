import time
from typing import Dict, Any
from src.strategies.base import BaseStrategy

class Strategy1FullCV(BaseStrategy):
    """
    Strategy 1: Full CV + LLM
    Injects the entire CV and question into a single prompt 
    demanding a JSON response.
    """
    
    @property
    def strategy_name(self) -> str:
        return "S1_Full_CV"

    def _build_prompt(self, cv_text: str, question: str) -> str:
        return f"""You are an expert HR assistant. Your task is to extract information from the following CV.
        
CV TEXT:
{cv_text}

QUESTION:
{question}

Please answer the question accurately using ONLY the information from the CV. 
Respond ONLY in valid JSON format with the following keys:
- "predicted_answer": A concise and factual answer to the question.
- "rationale": A brief explanation of why this answer is correct based on the CV.
- "confidence_score": A float between 0.0 and 1.0 representing your confidence.

JSON Response:
"""

    def run(self, cv_text: str, question: str, **kwargs) -> Dict[str, Any]:
        print(f"  -> [{self.strategy_name}] Q: {question[:80]}...")
        start_time = time.time()
        
        prompt = self._build_prompt(cv_text, question)
        
        try:
            llm_output = self.llm.generate(prompt)
            raw_response = llm_output.get("text", "")
            input_tokens = llm_output.get("input_tokens", 0)
            output_tokens = llm_output.get("output_tokens", 0)
            estimated_cost = llm_output.get("estimated_cost", 0.0)
        except Exception as e:
            print(f"  -> [ERROR] LLM Generation failed: {e}")
            raw_response = f"ERROR: {str(e)}"
            input_tokens = 0
            output_tokens = 0
            estimated_cost = 0.0
            
        latency = time.time() - start_time
        
        return {
            "raw_response": raw_response,
            "latency": latency,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost": estimated_cost,
            "context_used": "Full CV"
        }
