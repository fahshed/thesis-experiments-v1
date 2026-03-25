import argparse
import os
from datetime import datetime

from src.utils.dataset_loader import mock_dataset, mock_cv_texts, load_real_dataset
from src.llm.huggingface import HuggingFaceLLM
from src.strategies.strategy_1_full_cv import Strategy1FullCV
from src.strategies.strategy_2_retrieve_section import Strategy2RetrieveSection
from src.experiments.experiment_1 import Experiment1Extraction
from src.experiments.experiment_2 import Experiment2QA
from src.utils.logger import CSVLogger




def main():
    parser = argparse.ArgumentParser(
        description="Phase 1: Run Generation (No Evaluation)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="mistralai/Mistral-7B-Instruct-v0.3",
        help="HuggingFace model ID (default Mistral for real runs)",
    )
    parser.add_argument(
        "--strategy", type=int, choices=[1, 2], default=1, help="Which strategy to run"
    )
    parser.add_argument(
        "--experiment",
        type=int,
        choices=[1, 2],
        default=2,
        help="Which experiment to run",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/generated_answers.csv",
        help="Output CSV path for generations",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Run with mock data to verify pipeline"
    )

    args = parser.parse_args()

    print(f"=== Initializing LLM: {args.model}")
    print("=== Using GPU with device_map='auto'.")
    llm = HuggingFaceLLM(model_name=args.model, device=None, device_map="auto")

    print(f"=== Initializing Strategy {args.strategy}")
    if args.strategy == 1:
        strategy = Strategy1FullCV(llm)
    else:
        strategy = Strategy2RetrieveSection(llm)

    print(f"=== Initializing Experiment {args.experiment}")
    if args.experiment == 1:
        experiment = Experiment1Extraction(strategy)
    else:
        experiment = Experiment2QA(strategy)

    # Modify output path with timestamp and mock status
    base_dir = os.path.dirname(args.output) or "."
    file_name = os.path.basename(args.output)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = f"{timestamp}_mock_" if args.dry_run else f"{timestamp}_"
    args.output = os.path.join(base_dir, prefix + file_name)

    print(f"=== Starting Generation targeting: {args.output}")
    logger = CSVLogger(args.output)

    if args.dry_run:
        print("=== Running DRY RUN with mock dataset.")
        dataset = mock_dataset()
        cv_texts = mock_cv_texts()
    else:
        print("=== Loading REAL dataset (limited to 2 directories) ===")
        dataset, cv_texts = load_real_dataset(limit=2)
        if not dataset:
            print("No dataset loaded. Exiting.")
            return

    results = experiment.run(dataset, cv_texts)
    logger.log_batch(results)
    print(f"=== Phase 1 complete! Logged {len(results)} generations to {args.output}")


if __name__ == "__main__":
    main()
