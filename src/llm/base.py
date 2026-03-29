from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseLLM(ABC):
    """
    Interface for LLMs ensuring consistent behavior across local and API models.
    """
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Takes a prompt and returns a dict with 'text', 'input_tokens', 'output_tokens' etc.
        """
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Returns the identifier of the underlying model"""
        pass
