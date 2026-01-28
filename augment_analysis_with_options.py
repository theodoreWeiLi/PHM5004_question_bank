#!/usr/bin/env python3
"""Prepend an Options (A–E) block to each question's analysis in questions.json.

Idempotent: if analysis already starts with an Options/Choices/选项 prefix, it won't add another.

Usage:
  python augment_analysis_with_options.py --input questions.json --output questions.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def _analysis_has_options_prefix(analysis: str) -> bool:
    for ln in (analysis or "").splitlines():
        if ln.strip():
            first = ln.strip().lower()
            return first.startswith("options:") or first.startswith("choices:") or first.startswith("选项:")
    return False


def _normalize_whitespace(text: str) -> str:
    lines = [ln.rstrip() for ln in (text or "").splitlines()]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    out: List[str] = []
    blank_run = 0
    for ln in lines:
        if not ln.strip():
            blank_run += 1
            if blank_run <= 2:
                out.append("")
        else:
            blank_run = 0
            out.append(ln)

    return "\n".join(out).strip()


def _prepend_options_to_analysis(analysis: str, options: Dict[str, str]) -> str:
    analysis = _normalize_whitespace(analysis)
    if _analysis_has_options_prefix(analysis):
        return analysis

    lines: List[str] = ["Options:"]
    for letter in ["A", "B", "C", "D", "E"]:
        if letter in options:
            lines.append(f"{letter}. {options[letter]}")

    prefix = "\n".join(lines)
    return f"{prefix}\n\n{analysis}" if analysis else prefix


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="questions.json")
    parser.add_argument("--output", default="questions.json")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    questions: List[Dict[str, Any]] = json.loads(input_path.read_text(encoding="utf-8"))

    changed = 0
    for q in questions:
        options = q.get("options") or {}
        before = q.get("analysis") or ""
        after = _prepend_options_to_analysis(before, options)
        if after != before:
            q["analysis"] = after
            changed += 1

    output_path.write_text(
        json.dumps(questions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Updated {changed} questions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
