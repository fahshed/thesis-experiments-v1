from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.core.schemas import QARecord, RunResult
from src.strategies.base import BaseStrategy

class BaseExperiment(ABC):
    """
    Interface defining how an experiment runs a dataset through a strategy.
    """
    def __init__(self, strategy: BaseStrategy):
        self.strategy = strategy
    
    @abstractmethod
    def run(self, dataset: List[QARecord], cv_texts: Dict[str, str], logger: Any = None) -> List[RunResult]:
        """
        Runs the experiment on the given dataset.
        cv_texts maps cv_id to raw text.
        If logger is provided, it writes results incrementally.
        """
        pass
    
    @property
    @abstractmethod
    def experiment_name(self) -> str:
        """Name of the experiment (e.g. 'E1_Extraction')"""
        pass
