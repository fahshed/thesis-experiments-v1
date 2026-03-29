import argparse
import os
import pandas as pd
from src.utils.evaluation import compute_exact_match, compute_f1, compute_overlap

def main():
    parser = argparse.ArgumentParser(description="Phase 2: Run Evaluation on Generated Answers")
    parser.add_argument("--input", type=str, default="results/generated_answers.csv", help="Input CSV path (from generation phase)")
    parser.add_argument("--output", type=str, default="results/evaluated_answers.csv", help="Output CSV path with evaluation metrics")
    
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} does not exist.")
        return

    print(f"Loading generated data from {args.input}...")
    df = pd.read_csv(args.input)

    # Initialize score columns
    for col in ["score_exact_match", "score_f1", "overlap", "semantic_score"]:
        if col not in df.columns:
            df[col] = None

    print(f"Running evaluation metrics on {len(df)} records...")
    for idx, row in df.iterrows():
        pred = str(row.get("predicted_answer", ""))
        truth = str(row.get("ground_truth_answer", ""))
        exp_name = str(row.get("experiment_name", ""))

        # We don't evaluate if there's no ground truth
        if pd.isna(row.get("ground_truth_answer")) or truth.lower() == "nan":
            continue

        ex_match = compute_exact_match(pred, truth)
        f1_score = compute_f1(pred, truth)

        df.at[idx, "score_exact_match"] = ex_match
        df.at[idx, "score_f1"] = f1_score

        if exp_name == "E2_QA_Accuracy":
            overlap = compute_overlap(pred, truth)
            df.at[idx, "overlap"] = overlap
            df.at[idx, "semantic_score"] = f1_score  # Dummy semantic score

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"Phase 2 complete! Logged evaluated results to {args.output}")

if __name__ == "__main__":
    main()
