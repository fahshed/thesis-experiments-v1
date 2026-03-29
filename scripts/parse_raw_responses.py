#!/usr/bin/env python3
"""
Parse `raw_response` JSON in generated-answers CSVs and populate
the `predicted_answer`, `rationale`, and `confidence_score` columns.

Adds a `raw_response_parsable` column: True if all three fields were
successfully extracted, False otherwise.

Usage:
    # Process every generated_answers / merged CSV under results/
    python scripts/parse_raw_responses.py

    # Process specific file(s)
    python scripts/parse_raw_responses.py path/to/file.csv [another.csv ...]

    # Dry-run: print stats without writing
    python scripts/parse_raw_responses.py --dry-run
"""

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import pandas as pd

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"

KEY_ALIASES = {
    "predicted_answer": {"predicted_answer", "predict ed_answer", "predictied_answer", "predictanswer", "predictAnswer"},
    "rationale": {"rationale"},
    "confidence_score": {"confidence_score", "confidencescore", "confidenceScore", "confidence"},
}


def _strip_fences(text: str) -> str:
    """Remove markdown code fences wrapping the JSON."""
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if m:
        return m.group(1).strip()
    return text


def _extract_first_json_object(text: str) -> Optional[str]:
    """Return the first top-level { … } span from *text*, handling nesting."""
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_str = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if escape:
            escape = False
            continue
        if ch == "\\":
            escape = True
            continue
        if ch == '"' and not escape:
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return text[start:]


def _resolve_key(obj: dict, target: str) -> Any:
    """Look up *target* in *obj* using known aliases (case-insensitive)."""
    aliases = KEY_ALIASES.get(target, {target})
    lower_map = {k.lower().replace(" ", "").replace("_", ""): k for k in obj}
    for alias in aliases:
        norm = alias.lower().replace(" ", "").replace("_", "")
        if norm in lower_map:
            return obj[lower_map[norm]]
    return None


def _clean_json_string(s: str) -> str:
    """Best-effort fix of common JSON issues from LLM output."""
    s = s.replace("\t", " ")
    s = re.sub(r'(?<!\\)\n', '\\n', s)
    s = re.sub(r",\s*}", "}", s)
    s = re.sub(r",\s*]", "]", s)
    return s


def parse_raw_response(raw: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Try to extract predicted_answer, rationale, confidence_score from a
    raw_response string.

    Returns (parsable: bool, fields: dict with the three keys or empty vals).
    """
    empty = {"predicted_answer": "", "rationale": "", "confidence_score": ""}

    if not raw or not raw.strip():
        return False, empty

    text = raw.strip()
    if text.startswith("ERROR:"):
        return False, empty

    text = _strip_fences(text)
    snippet = _extract_first_json_object(text)
    if snippet is None:
        return False, empty

    obj: Optional[dict] = None
    for attempt_clean in (False, True):
        candidate = _clean_json_string(snippet) if attempt_clean else snippet
        try:
            obj = json.loads(candidate)
            break
        except json.JSONDecodeError:
            obj = None

    if not isinstance(obj, dict):
        return False, empty

    pa = _resolve_key(obj, "predicted_answer")
    rat = _resolve_key(obj, "rationale")
    cs = _resolve_key(obj, "confidence_score")

    if pa is None and rat is None and cs is None:
        return False, empty

    if not isinstance(pa, str):
        pa = json.dumps(pa) if pa is not None else ""
    if not isinstance(rat, str):
        rat = str(rat) if rat is not None else ""

    if cs is not None:
        try:
            cs = str(float(cs))
        except (ValueError, TypeError):
            cs = ""
    else:
        cs = ""

    parsable = pa != "" and rat != "" and cs != ""
    return parsable, {"predicted_answer": pa, "rationale": rat, "confidence_score": cs}


def process_file(path: Path, dry_run: bool = False) -> Dict[str, int]:
    read_kw = {"keep_default_na": False, "na_values": []}
    df = pd.read_csv(path, **read_kw)

    if "raw_response" not in df.columns:
        print(f"  SKIP (no raw_response column): {path}")
        return {}

    for col in ("predicted_answer", "rationale", "confidence_score"):
        if col not in df.columns:
            df[col] = ""

    parsable_flags = []
    stats = {"total": len(df), "parsable": 0, "partial": 0, "unparsable": 0}

    for idx, row in df.iterrows():
        raw = str(row.get("raw_response", ""))
        ok, fields = parse_raw_response(raw)
        df.at[idx, "predicted_answer"] = fields["predicted_answer"]
        df.at[idx, "rationale"] = fields["rationale"]
        df.at[idx, "confidence_score"] = fields["confidence_score"]

        if ok:
            parsable_flags.append(True)
            stats["parsable"] += 1
        else:
            parsable_flags.append(False)
            has_any = any(v != "" for v in fields.values())
            if has_any:
                stats["partial"] += 1
            else:
                stats["unparsable"] += 1

    df["raw_response_parsable"] = parsable_flags

    print(f"  {path.name}")
    print(f"    rows={stats['total']}  parsable={stats['parsable']}  partial={stats['partial']}  unparsable={stats['unparsable']}")

    if not dry_run:
        df.to_csv(path, index=False)
        print(f"    -> written back to {path}")

    return stats


def discover_csvs() -> list[Path]:
    paths = []
    for p in RESULTS_DIR.rglob("*.csv"):
        if "generated_answers" in p.name or p.name == "merged_generated_answers.csv":
            paths.append(p)
    return sorted(paths)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="*", type=Path, help="CSV file(s) to process (default: auto-discover under results/)")
    parser.add_argument("--dry-run", action="store_true", help="Print stats without modifying files")
    args = parser.parse_args()

    targets = [p.expanduser().resolve() for p in args.files] if args.files else discover_csvs()

    if not targets:
        print("No CSV files found.")
        return

    print(f"Processing {len(targets)} file(s){'  [DRY RUN]' if args.dry_run else ''}:\n")

    totals = {"total": 0, "parsable": 0, "partial": 0, "unparsable": 0}
    files_with_unparsable: list[tuple[Path, int]] = []
    for path in targets:
        stats = process_file(path, dry_run=args.dry_run)
        for k in totals:
            totals[k] += stats.get(k, 0)
        u = stats.get("unparsable", 0)
        if u > 0:
            files_with_unparsable.append((path, u))

    print(f"\nOverall: {totals['total']} rows — {totals['parsable']} parsable, {totals['partial']} partial, {totals['unparsable']} unparsable")

    if files_with_unparsable:
        print(f"\nFiles with unparsable rows ({len(files_with_unparsable)}):")
        for p, n in sorted(files_with_unparsable, key=lambda x: (-x[1], str(x[0]))):
            print(f"  {n:>5}  {p}")
    else:
        print("\nNo unparsable rows in any processed file.")


if __name__ == "__main__":
    main()
