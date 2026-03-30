#!/usr/bin/env bash
# Generate PPTX from Marp slides using marp-cli
# Usage: ./scripts/generate_pptx.sh [output_path]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

INPUT="$REPO_ROOT/presentation/marp_slides.md"
OUTPUT="${1:-$REPO_ROOT/presentation/marp_slides.pptx}"

if ! command -v npx &>/dev/null; then
  echo "Error: npx not found. Please install Node.js." >&2
  exit 1
fi

echo "Converting: $INPUT"
echo "Output:     $OUTPUT"

npx @marp-team/marp-cli \
  --pptx \
  --allow-local-files \
  --input-dir "$(dirname "$INPUT")" \
  "$INPUT" \
  -o "$OUTPUT"

echo "Done: $OUTPUT"
