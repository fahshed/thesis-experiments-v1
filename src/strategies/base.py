from abc import ABC, abstractmethod
from typing import Dict, Any

from src.llm.base import BaseLLM

class BaseStrategy(ABC):
    """
    Interface for a strategy. Every strategy must hold an LLM 
    and define how it processes a single (cv_text, question) pair.
    """
    
    def __init__(self, llm: BaseLLM):
        self.llm = llm

    @abstractmethod
    def run(self, cv_text: str, question: str, **kwargs) -> Dict[str, Any]:
        """
        Takes the raw text and question and returns a dict containing:
        - cv_id/question_category may be supplied in kwargs for strategies that need per-CV context
        - predicted_answer: str
        - confidence_score: float
        - rationale: str
        - context_used: str/int/list depending on strategy tracking
        - latency: total time for logic + generation
        - token/cost info if applicable
        """
        pass
    
    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Returns string identifier e.g. 'S1_Full_CV'"""
        pass
