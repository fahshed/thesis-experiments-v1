#!/usr/bin/env python3
"""
Judge generated CV-QA result CSV rows with the Gemini API.

For each row, the script sends:
- question_text
- ground_truth_answer
- predicted_answer
- rationale

Gemini returns structured JSON with:
- judge_answer_judgment
- judge_rationale_judgment
- judge_error_type

The script persists progress after every API attempt by writing the CSV back to disk
atomically. By default, any row that already has a non-empty judge response recorded
is skipped so charged rows are not re-run accidentally.

Usage:
    # First set GEMINI_API_KEY below in this script.

    # Test on a few rows first
    python3 scripts/judge_results_with_gemini.py results/my_file.csv --limit 5

    # Process one file fully
    python3 scripts/judge_results_with_gemini.py results/my_file.csv

    # Process multiple files
    python3 scripts/judge_results_with_gemini.py results/file1.csv results/file2.csv

    # Re-run rows even if a judge response already exists
    python3 scripts/judge_results_with_gemini.py results/my_file.csv --force
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Iterable, Literal, Optional, Tuple

import pandas as pd
from pydantic import BaseModel, Field

try:
    from google import genai
    from google.genai import types
except ImportError:  # pragma: no cover - import is environment-dependent
    genai = None
    types = None


DEFAULT_MODEL = "gemini-3-flash-preview"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEFAULT_PROMPT_VERSION = "judge_v1"
DEFAULT_MAX_RETRIES = 5
DEFAULT_RETRY_BASE_SLEEP = 2.0

JUDGE_COLUMNS = [
    "judge_model",
    "judge_prompt_version",
    "judge_raw_response",
    "judge_raw_response_parsable",
    "judge_answer_judgment",
    "judge_answer_credit",
    "judge_rationale_judgment",
    "judge_rationale_credit",
    "judge_error_type",
]


class JudgeResponse(BaseModel):
    judge_answer_judgment: Literal["correct", "partial", "incorrect"] = Field(
        description="Judgment of the predicted answer compared to the ground truth answer."
    )
    judge_rationale_judgment: Literal["correct", "partial", "incorrect"] = Field(
        description="Judgment of whether the rationale appropriately supports the predicted answer relative to the ground truth."
    )
    judge_error_type: Literal[
        "none",
        "not_answered",
        "format_issue",
        "wrong_entity",
        "wrong_numeric_value",
        "wrong_boolean",
        "missing_detail",
        "extra_unsupported_detail",
        "contradiction_to_ground_truth",
        "invented_value_for_missing_ground_truth",
        "other",
    ] = Field(
        description="Single best answer-error label. Use 'none' when judge_answer_judgment is correct. This field is for answer errors, not rationale-only issues."
    )


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, float) and pd.isna(value):
        return False
    return str(value).strip() != ""


def _is_missing_ground_truth(value: Any) -> bool:
    if not _has_value(value):
        return True
    normalized = str(value).strip().lower()
    return normalized in {"nan", "none", "null", "n/a", "na"}


def _display_text(value: Any, *, missing_label: str) -> str:
    if _is_missing_ground_truth(value):
        return missing_label
    if not _has_value(value):
        return "(empty)"
    return str(value).strip()


def _safe_write_csv(df: pd.DataFrame, path: Path) -> None:
    tmp_path = path.with_name(f".{path.name}.tmp")
    df.to_csv(tmp_path, index=False)
    tmp_path.replace(path)


def _derive_credit(judgment: str) -> float:
    return {"correct": 1.0, "partial": 0.5, "incorrect": 0.0}[judgment]


def _build_prompt(
    *,
    question_text: str,
    ground_truth_answer: str,
    predicted_answer: str,
    rationale: str,
) -> str:
    ground_truth_missing = _is_missing_ground_truth(ground_truth_answer)

    return f"""
You are judging a single row from a CV question-answering benchmark.

Judging rubric:
1. `judge_answer_judgment = correct`
   Use when the predicted answer semantically matches the ground truth.
2. `judge_answer_judgment = partial`
   Use when the predicted answer is partly right but incomplete, too broad, too narrow, or mixes correct and incorrect details.
3. `judge_answer_judgment = incorrect`
   Use when the predicted answer is wrong, blank, irrelevant, contradicts the ground truth, or invents unsupported information.
4. If the ground truth is missing, blank, or marked as NaN, interpret that as: the source CV does not provide an answer.
   In that case, a correct prediction should explicitly say the information is missing, not provided, or not mentioned.
   If the prediction invents a value anyway, use `invented_value_for_missing_ground_truth`.
5. `judge_rationale_judgment = correct`
   Use when the rationale appropriately supports the predicted answer and is consistent with the ground truth.
6. `judge_rationale_judgment = partial`
   Use when the rationale is somewhat relevant but incomplete, vague, or only partly consistent with the ground truth.
7. `judge_rationale_judgment = incorrect`
   Use when the rationale is irrelevant, contradicts the ground truth, or tries to justify a wrong answer.
8. `judge_error_type` is for the answer error only, not the rationale error.
   If `judge_answer_judgment` is `correct`, set `judge_error_type = none`.
   Otherwise choose the single best label from the schema enum.

Input row:
- question_text: {json.dumps(question_text, ensure_ascii=False)}
- ground_truth_answer: {json.dumps(_display_text(ground_truth_answer, missing_label="(missing / not provided in source CV)"), ensure_ascii=False)}
- ground_truth_missing: {"true" if ground_truth_missing else "false"}
- predicted_answer: {json.dumps(_display_text(predicted_answer, missing_label="(empty)"), ensure_ascii=False)}
- rationale: {json.dumps(_display_text(rationale, missing_label="(empty)"), ensure_ascii=False)}
""".strip()


def _call_gemini(
    *,
    client: Any,
    model: str,
    prompt: str,
    max_retries: int,
    retry_base_sleep: float,
) -> Tuple[str, Optional[JudgeResponse], bool]:
    assert types is not None, "google-genai is not installed"
    config = types.GenerateContentConfig(
        temperature=0,
        response_mime_type="application/json",
        response_schema=JudgeResponse,
    )

    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )
            raw_text = getattr(response, "text", "") or ""
            parsed = getattr(response, "parsed", None)

            if isinstance(parsed, JudgeResponse):
                return raw_text, parsed, False
            if isinstance(parsed, dict):
                return raw_text, JudgeResponse.model_validate(parsed), False
            if raw_text:
                return raw_text, JudgeResponse.model_validate_json(raw_text), False

            return json.dumps({"empty_response": True}), None, False
        except Exception as exc:  # noqa: BLE001
            status_code = getattr(exc, "status_code", None)
            retryable = status_code in {429, 500, 502, 503, 504} or status_code is None
            if retryable and attempt < max_retries:
                sleep_s = retry_base_sleep * (2 ** (attempt - 1))
                print(
                    f"    retryable exception {type(exc).__name__}; sleeping {sleep_s:.1f}s before retry {attempt + 1}/{max_retries}",
                    flush=True,
                )
                time.sleep(sleep_s)
                continue
            return f"ERROR: {type(exc).__name__}: {exc}", None, True

    return "ERROR: unexpected retry exhaustion", None, True


def _ensure_columns(df: pd.DataFrame) -> None:
    for col in JUDGE_COLUMNS:
        if col not in df.columns:
            df[col] = ""


def _stringify_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "True" if value else "False"
    return str(value)


def _is_truthy_flag(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, float) and pd.isna(value):
        return False
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def _row_should_skip(row: pd.Series, *, force: bool) -> bool:
    if force:
        return False
    return _has_value(row.get("judge_raw_response")) or _has_value(row.get("judge_answer_judgment"))


def _validate_input_columns(df: pd.DataFrame, path: Path) -> None:
    required = ["question_text", "ground_truth_answer", "predicted_answer", "rationale"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise SystemExit(f"Missing required columns in {path}: {missing}")


def process_file(
    path: Path,
    *,
    client: Any,
    model: str,
    prompt_version: str,
    force: bool,
    limit: Optional[int],
    offset: int,
) -> None:
    read_kw = {"keep_default_na": False, "na_values": []}
    df = pd.read_csv(path, **read_kw)
    _validate_input_columns(df, path)
    _ensure_columns(df)

    start = max(offset, 0)
    stop = len(df) if limit is None else min(len(df), start + max(limit, 0))
    row_indices = list(df.index[start:stop])

    processed = 0
    skipped = 0
    skipped_unparsable = 0

    print(f"\nProcessing {path}")
    print(f"  rows in file: {len(df)}")
    print(f"  target slice: start={start}, stop={stop}, count={len(row_indices)}")

    for position, idx in enumerate(row_indices, start=1):
        row = df.loc[idx]
        if _row_should_skip(row, force=force):
            skipped += 1
            continue
        if "raw_response_parsable" in df.columns and not _is_truthy_flag(row.get("raw_response_parsable")):
            skipped_unparsable += 1
            continue

        question_text = str(row.get("question_text", ""))
        ground_truth_answer = str(row.get("ground_truth_answer", ""))
        predicted_answer = str(row.get("predicted_answer", ""))
        rationale = str(row.get("rationale", ""))
        question_id = str(row.get("question_id", idx))

        print(
            f"  [{position}/{len(row_indices)}] judging row_index={idx} question_id={question_id}",
            flush=True,
        )

        prompt = _build_prompt(
            question_text=question_text,
            ground_truth_answer=ground_truth_answer,
            predicted_answer=predicted_answer,
            rationale=rationale,
        )
        raw_response, parsed, had_transport_error = _call_gemini(
            client=client,
            model=model,
            prompt=prompt,
            max_retries=DEFAULT_MAX_RETRIES,
            retry_base_sleep=DEFAULT_RETRY_BASE_SLEEP,
        )
        parsable = parsed is not None

        df.at[idx, "judge_model"] = _stringify_cell(model)
        df.at[idx, "judge_prompt_version"] = _stringify_cell(prompt_version)
        df.at[idx, "judge_raw_response"] = _stringify_cell(raw_response)
        df.at[idx, "judge_raw_response_parsable"] = _stringify_cell(bool(parsable))

        if parsable:
            answer_judgment = parsed.judge_answer_judgment
            rationale_judgment = parsed.judge_rationale_judgment
            error_type = parsed.judge_error_type

            if answer_judgment == "correct" and error_type != "none":
                error_type = "none"
            elif answer_judgment != "correct" and error_type == "none":
                error_type = "other"

            df.at[idx, "judge_answer_judgment"] = _stringify_cell(answer_judgment)
            df.at[idx, "judge_answer_credit"] = _stringify_cell(_derive_credit(answer_judgment))
            df.at[idx, "judge_rationale_judgment"] = _stringify_cell(rationale_judgment)
            df.at[idx, "judge_rationale_credit"] = _stringify_cell(_derive_credit(rationale_judgment))
            df.at[idx, "judge_error_type"] = _stringify_cell(error_type)
            print(
                f"    saved answer={answer_judgment} rationale={rationale_judgment} error_type={error_type}",
                flush=True,
            )
        else:
            df.at[idx, "judge_answer_judgment"] = ""
            df.at[idx, "judge_answer_credit"] = ""
            df.at[idx, "judge_rationale_judgment"] = ""
            df.at[idx, "judge_rationale_credit"] = ""
            df.at[idx, "judge_error_type"] = ""
            state = "transport_error" if had_transport_error else "unparsable"
            print(f"    saved {state} judge response for later inspection", flush=True)

        _safe_write_csv(df, path)
        processed += 1

    print(
        "  complete: "
        f"processed={processed} skipped_existing={skipped} skipped_source_unparsable={skipped_unparsable} "
        f"untouched={len(row_indices) - processed - skipped - skipped_unparsable}"
    )


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "csv_paths",
        nargs="+",
        type=Path,
        help="One or more generated-results CSV files to judge in place.",
    )
    parser.add_argument(
        "--prompt-version",
        default=DEFAULT_PROMPT_VERSION,
        help=f"Version string recorded in judge_prompt_version (default: {DEFAULT_PROMPT_VERSION})",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of rows to process in each file.",
    )
    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Number of rows to skip from the start of each file.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-run rows even if a judge response is already recorded.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Optional[Iterable[str]] = None) -> None:
    args = parse_args(argv)
    if genai is None or types is None:
        raise SystemExit(
            "The google-genai package is not installed. Install it with: pip install google-genai"
        )

    api_key = (GEMINI_API_KEY or "").strip()
    if not api_key:
        raise SystemExit(
            "Set GEMINI_API_KEY in the script or export GEMINI_API_KEY in your shell before running."
        )

    with genai.Client(api_key=api_key) as client:
        for csv_path in args.csv_paths:
            path = csv_path.expanduser().resolve()
            if not path.is_file():
                raise SystemExit(f"Not a file: {path}")
            process_file(
                path,
                client=client,
                model=DEFAULT_MODEL,
                prompt_version=args.prompt_version,
                force=args.force,
                limit=args.limit,
                offset=args.offset,
            )

if __name__ == "__main__":
    main(sys.argv[1:])
