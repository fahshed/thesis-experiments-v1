import argparse
import os
import pandas as pd
from typing import List

from src.core.schemas import QARecord
from src.llm.huggingface import HuggingFaceLLM
from src.strategies.strategy_1_full_cv import Strategy1FullCV
from src.strategies.strategy_2_retrieve_section import Strategy2RetrieveSection
from src.experiments.experiment_1 import Experiment1Extraction
from src.experiments.experiment_2 import Experiment2QA
from src.utils.logger import CSVLogger

def mock_dataset() -> List[QARecord]:
    return [
        QARecord(
            cv_id="CV_001",
            question_id="Q_01",
            question_category="GPA",
            question_text="What is the GPA of the candidate?",
            ground_truth_answer="3.9"
        ),
        QARecord(
            cv_id="CV_001",
            question_id="Q_02",
            question_category="Skills",
            question_text="Does the candidate know Python?",
            ground_truth_answer="Yes"
        )
    ]

def mock_cv_texts() -> dict:
    return {
        "CV_001": "John Doe. Education: BSc in Computer Science, GPA: 3.9 out of 4.0. Skills: Python, Java, C++."
    }

def main():
    parser = argparse.ArgumentParser(description="Run CV QA Strategy Pipeline")
    parser.add_argument("--model", type=str, default="gpt2", help="HuggingFace model ID (default gpt2 for quick dry-run)")
    parser.add_argument("--strategy", type=int, choices=[1, 2], default=1, help="Which strategy to run")
    parser.add_argument("--experiment", type=int, choices=[1, 2], default=2, help="Which experiment to run")
    parser.add_argument("--output", type=str, default="results/dry_run_results.csv", help="Output CSV path")
    parser.add_argument("--dry-run", action="store_true", help="Run with mock data to verify pipeline")
    
    args = parser.parse_args()

    print(f"Initializing LLM: {args.model}")
    llm = HuggingFaceLLM(model_name=args.model, device="cpu")
    
    print(f"Initializing Strategy {args.strategy}")
    if args.strategy == 1:
        strategy = Strategy1FullCV(llm)
    else:
        strategy = Strategy2RetrieveSection(llm)
        
    print(f"Initializing Experiment {args.experiment}")
    if args.experiment == 1:
        experiment = Experiment1Extraction(strategy)
    else:
        experiment = Experiment2QA(strategy)
        
    print(f"Starting Logger targeting: {args.output}")
    logger = CSVLogger(args.output)
    
    if args.dry_run:
        print("Running DRY RUN with mock dataset.")
        dataset = mock_dataset()
        cv_texts = mock_cv_texts()
    else:
        print("To run with real data, implement your standard dataset loading here.")
        # E.g. dataset = load_aaron_csv("dataset/Aaron2.csv")
        # cv_texts = load_cv_texts("dataset/cvs/")
        return
        
    results = experiment.run(dataset, cv_texts)
    logger.log_batch(results)
    print(f"Pipeline complete! Logged {len(results)} results to {args.output}")

if __name__ == "__main__":
    main()
