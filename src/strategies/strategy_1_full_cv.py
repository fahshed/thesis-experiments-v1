import time
import json
import re
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

    def _parse_response(self, text: str) -> Dict[str, Any]:
        result = {
            "predicted_answer": "",
            "rationale": "",
            "confidence_score": 0.0,
        }
        
        # Try to extract json blocks
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                result["predicted_answer"] = data.get("predicted_answer", str(data.get("answer", "")))
                result["rationale"] = data.get("rationale", "")
                result["confidence_score"] = float(data.get("confidence_score", 0.0))
            except (json.JSONDecodeError, ValueError):
                # Fallback if json parsing fails
                result["predicted_answer"] = text.strip()
        else:
            result["predicted_answer"] = text.strip()
            
        return result

    def run(self, cv_text: str, question: str, **kwargs) -> Dict[str, Any]:
        start_time = time.time()
        
        prompt = self._build_prompt(cv_text, question)
        llm_output = self.llm.generate(prompt)
        
        parsed = self._parse_response(llm_output["text"])
        
        latency = time.time() - start_time
        
        return {
            "predicted_answer": parsed.get("predicted_answer", ""),
            "confidence_score": parsed.get("confidence_score", 0.0),
            "rationale": parsed.get("rationale", ""),
            "latency": latency,
            "input_tokens": llm_output.get("input_tokens", 0),
            "output_tokens": llm_output.get("output_tokens", 0),
            "estimated_cost": llm_output.get("estimated_cost", 0.0),
            "context_used": "Full CV"
        }
