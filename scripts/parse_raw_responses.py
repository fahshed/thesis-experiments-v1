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

    # Random unparsable previews (10) + up to 2 full raw_response blobs
    python scripts/parse_raw_responses.py --dry-run --dump-unparsable-samples results/unparsable_sample_dump.txt
"""

import argparse
import json
import random
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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


def process_file(
    path: Path,
    dry_run: bool = False,
    unparsable_collector: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, int]:
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

    for row_i, (idx, row) in enumerate(df.iterrows()):
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
                if unparsable_collector is not None:
                    rec: Dict[str, Any] = {"path": path, "row_index": row_i, "raw": raw}
                    if "question_id" in df.columns:
                        rec["question_id"] = str(row.get("question_id", ""))
                    if "question_text" in df.columns:
                        rec["question_text"] = str(row.get("question_text", ""))
                    unparsable_collector.append(rec)

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


def write_unparsable_sample_dump(
    out_path: Path,
    records: List[Dict[str, Any]],
    *,
    preview_n: int = 10,
    full_raw_max: int = 2,
    preview_raw_chars: int = 600,
    question_preview_chars: int = 200,
    seed: Optional[int] = None,
) -> None:
    """
    Write *preview_n* random unparsable rows with truncated raw_response, plus up to
    *full_raw_max* full raw_response blobs (independent random draw).
    """
    rng = random.Random(seed)
    lines: list[str] = [
        "Unparsable row observation sample",
        f"Generated (UTC): {datetime.now(timezone.utc).isoformat()}",
        f"Total unparsable rows collected: {len(records)}",
        f"Random seed: {seed if seed is not None else '(system default)'}",
        "",
    ]

    if not records:
        lines.append("No unparsable rows found; nothing to sample.")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    n_prev = min(preview_n, len(records))
    preview = rng.sample(records, n_prev)

    lines.append(f"=== {n_prev} random unparsable row(s) — metadata + truncated raw_response ({preview_raw_chars} chars max) ===")
    lines.append("")
    for k, rec in enumerate(preview, start=1):
        p = rec["path"]
        lines.append(f"--- preview {k}/{n_prev} ---")
        lines.append(f"file: {p}")
        lines.append(f"row_index (0-based data row): {rec['row_index']}")
        if "question_id" in rec:
            lines.append(f"question_id: {rec['question_id']}")
        if "question_text" in rec:
            qt = rec["question_text"]
            if len(qt) > question_preview_chars:
                qt = qt[:question_preview_chars] + " …"
            lines.append(f"question_text (preview): {qt}")
        raw = rec["raw"]
        if len(raw) > preview_raw_chars:
            raw_show = raw[:preview_raw_chars] + "\n… [truncated]"
        else:
            raw_show = raw
        lines.append("raw_response (truncated):")
        lines.append(raw_show)
        lines.append("")

    n_full = min(full_raw_max, len(records))
    full_pick = rng.sample(records, n_full)
    lines.append(f"=== Up to {full_raw_max} full raw_response value(s) ({n_full} drawn) ===")
    lines.append("")
    for k, rec in enumerate(full_pick, start=1):
        lines.append(f"--- full raw {k}/{n_full} ---")
        lines.append(f"file: {rec['path']}")
        lines.append(f"row_index (0-based data row): {rec['row_index']}")
        if "question_id" in rec:
            lines.append(f"question_id: {rec['question_id']}")
        lines.append("raw_response (full):")
        lines.append(rec["raw"])
        lines.append("")
        lines.append("--- end full raw ---")
        lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="*", type=Path, help="CSV file(s) to process (default: auto-discover under results/)")
    parser.add_argument("--dry-run", action="store_true", help="Print stats without modifying files")
    parser.add_argument(
        "--dump-unparsable-samples",
        type=Path,
        metavar="PATH",
        default=None,
        help="Write a text file with 10 random unparsable previews and up to 2 full raw_response samples",
    )
    parser.add_argument(
        "--sample-seed",
        type=int,
        default=None,
        help="RNG seed for --dump-unparsable-samples (default: nondeterministic)",
    )
    args = parser.parse_args()

    targets = [p.expanduser().resolve() for p in args.files] if args.files else discover_csvs()

    if not targets:
        print("No CSV files found.")
        return

    print(f"Processing {len(targets)} file(s){'  [DRY RUN]' if args.dry_run else ''}:\n")

    totals = {"total": 0, "parsable": 0, "partial": 0, "unparsable": 0}
    files_with_unparsable: list[tuple[Path, int]] = []
    collector: Optional[List[Dict[str, Any]]] = [] if args.dump_unparsable_samples else None
    for path in targets:
        stats = process_file(path, dry_run=args.dry_run, unparsable_collector=collector)
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

    if args.dump_unparsable_samples:
        assert collector is not None
        dest = args.dump_unparsable_samples.expanduser().resolve()
        write_unparsable_sample_dump(dest, collector, seed=args.sample_seed)
        print(f"\nWrote unparsable observation sample to {dest}")


if __name__ == "__main__":
    main()
