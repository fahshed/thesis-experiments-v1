#!/usr/bin/env python3
"""
Concatenate two generated-answers CSVs: top file rows first, then bottom file rows.
Uses pandas so multiline quoted fields (e.g. raw_response JSON) round-trip correctly.

Unless you pass --output, the merged CSV is written in the same directory as top_csv
as merged_generated_answers.csv (typically the same folder as both inputs).
"""

import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "top_csv",
        type=Path,
        help="CSV whose rows appear first in the output",
    )
    parser.add_argument(
        "bottom_csv",
        type=Path,
        help="CSV whose rows are appended after top_csv",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output path (default: same directory as top_csv → merged_generated_answers.csv)",
    )
    args = parser.parse_args()

    top_path = args.top_csv.expanduser().resolve()
    bottom_path = args.bottom_csv.expanduser().resolve()
    if not top_path.is_file():
        raise SystemExit(f"Not a file: {top_path}")
    if not bottom_path.is_file():
        raise SystemExit(f"Not a file: {bottom_path}")

    out = args.output
    if out is None:
        out = top_path.parent / "merged_generated_answers.csv"
    else:
        out = out.expanduser().resolve()

    # Avoid treating literal "nan" in CSV cells as float NaN (common in ground_truth_answer).
    read_kw = {"keep_default_na": False, "na_values": []}
    df_top = pd.read_csv(top_path, **read_kw)
    df_bottom = pd.read_csv(bottom_path, **read_kw)

    if list(df_top.columns) != list(df_bottom.columns):
        raise SystemExit(
            "Column mismatch:\n"
            f"  top:    {list(df_top.columns)}\n"
            f"  bottom: {list(df_bottom.columns)}"
        )

    merged = pd.concat([df_top, df_bottom], ignore_index=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(out, index=False)

    print(f"Wrote {len(merged)} rows ({len(df_top)} + {len(df_bottom)}) to {out}")


if __name__ == "__main__":
    main()
