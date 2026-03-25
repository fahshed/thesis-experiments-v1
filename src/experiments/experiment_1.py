from typing import List, Dict
from src.core.schemas import QARecord, RunResult
from src.experiments.base import BaseExperiment
from src.utils.evaluation import compute_exact_match, compute_f1

class Experiment1Extraction(BaseExperiment):
    """
    Experiment 1: Structured Field Extraction
    Focuses on fields like GPA, Skills, etc. F1 and Exact Match are main scores.
    """
    
    @property
    def experiment_name(self) -> str:
        return "E1_Extraction"

    def run(self, dataset: List[QARecord], cv_texts: Dict[str, str]) -> List[RunResult]:
        results = []
        
        for record in dataset:
            cv_text = cv_texts.get(record.cv_id, "")
            if not cv_text:
                continue
                
            out = self.strategy.run(cv_text, record.question_text)
            
            pred = out.get("predicted_answer", "")
            truth = record.ground_truth_answer
            
            ex_match = compute_exact_match(pred, truth)
            f1_score = compute_f1(pred, truth)
            
            res = RunResult(
                cv_id=record.cv_id,
                question_id=record.question_id,
                question_category=record.question_category,
                question_text=record.question_text,
                ground_truth_answer=truth,
                strategy=self.strategy.strategy_name,
                model_name=self.strategy.llm.model_name,
                predicted_answer=pred,
                confidence_score=out.get("confidence_score"),
                rationale=out.get("rationale"),
                latency=out.get("latency", 0.0),
                input_tokens=out.get("input_tokens"),
                output_tokens=out.get("output_tokens"),
                estimated_cost=out.get("estimated_cost", 0.0),
                normalized_answer=pred.lower().strip(),
                score_exact_match=ex_match,
                score_f1=f1_score,
                experiment_metadata={
                    "experiment_name": self.experiment_name,
                    "target_field": record.question_category,
                    "field_f1": f1_score
                }
            )
            
            # Incorporate strategy-specific data (like retrieval metadata)
            res.experiment_metadata.update({k: v for k, v in out.items() if k not in res.dict()})
            
            results.append(res)
            
        return results
