from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class QARecord(BaseModel):
    """Represents a single input row from the dataset (e.g., Aaron2.csv)"""
    cv_id: str
    question_id: str
    question_category: str
    question_text: str
    ground_truth_answer: str

class RunResult(BaseModel):
    """Represents a single evaluated output row matching the master template."""
    # Input Echoes
    cv_id: str
    question_id: str
    question_category: str
    question_text: str
    ground_truth_answer: str
    
    # Run Info
    strategy: str
    model_name: str
    
    # Model Outputs
    predicted_answer: str
    confidence_score: Optional[float] = None
    rationale: Optional[str] = None
    
    # Performance & Cost
    latency: float = 0.0
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    estimated_cost: float = 0.0
    
    # Evaluation Metrics
    normalized_answer: Optional[str] = None
    score_exact_match: Optional[float] = None
    score_f1: Optional[float] = None
    overlap: Optional[float] = None
    semantic_score: Optional[float] = None
    human_eval_score: Optional[float] = None
    error_type: Optional[str] = None
    
    # Experiment-Specific Extended Fields (e.g., retrieval hits, field extraction)
    experiment_metadata: Dict[str, Any] = Field(default_factory=dict)
