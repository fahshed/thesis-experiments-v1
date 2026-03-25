from typing import List, Dict
from src.core.schemas import QARecord, RunResult
from src.experiments.base import BaseExperiment

class Experiment2QA(BaseExperiment):
    """
    Experiment 2: CV QA Accuracy
    Standard CV QA over broader questions. Includes Overlap and Semantic dummy.
    """
    
    @property
    def experiment_name(self) -> str:
        return "E2_QA_Accuracy"

    def run(self, dataset: List[QARecord], cv_texts: Dict[str, str]) -> List[RunResult]:
        results = []
        total_records = len(dataset)
        
        for i, record in enumerate(dataset, 1):
            print(f"[{self.experiment_name}] Processing record {i}/{total_records} - CV ID: {record.cv_id}")
            cv_text = cv_texts.get(record.cv_id, "")
            if not cv_text:
                continue
                
            out = self.strategy.run(cv_text, record.question_text)
            
            pred = out.get("predicted_answer", "")
            truth = record.ground_truth_answer
            
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
                experiment_metadata={
                    "experiment_name": self.experiment_name
                }
            )
            
            # Incorporate ONLY retrieved_text if provided by strategy
            if "retrieved_text" in out:
                res.experiment_metadata["retrieved_text"] = out["retrieved_text"]

            results.append(res)
            
        return results
