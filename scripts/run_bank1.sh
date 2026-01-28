#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Prefer your conda python if present, else fall back to python3.
PYTHON_BIN="${PYTHON_BIN:-python3}"
if [[ -x "/opt/miniconda3/bin/python" ]]; then
  PYTHON_BIN="/opt/miniconda3/bin/python"
fi

BANK_MD="other/question_bank1.md"
BANK_JSON="questions_bank1.json"

if [[ ! -f "$BANK_JSON" || "$BANK_MD" -nt "$BANK_JSON" ]]; then
  "$PYTHON_BIN" build_questions.py --input "$BANK_MD" --output "$BANK_JSON"
fi

export QUESTIONS_FILE="$BANK_JSON"
export PORT="${PORT:-5001}"

exec "$PYTHON_BIN" app.py
