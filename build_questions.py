#!/usr/bin/env python3
"""Build questions.json from the Markdown question bank.

Supported Markdown structures per question:

Style A (legacy):
- Starts with a heading like: ### 1. Some Title
- Contains **Question:**, **Options:**, **Analysis:** blocks.

Style B (current):
- Starts with a line like: Question 1:
- Followed by question text until a line "Options:"
- Options are lines like "A. ..." and the correct option has a trailing "✅".
- Analysis starts after a line "Analysis:" and continues until the next question.

Usage:
    python build_questions.py --input 5004question_bank.md --output questions.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


QUESTION_HEADING_RE = re.compile(r"^#+\s+(\d+)\.\s*(.*)\s*$")
QUESTION_LABEL_RE = re.compile(r"^\s*Question\s+(\d+)\s*:\s*$", re.IGNORECASE)
OPTION_LINE_RE = re.compile(r"^\s*([A-Z])[\.)]\s+(.*)\s*$")
CODE_FENCE_RE = re.compile(r"^\s*```")


def _is_marker_line(line: str, marker: str) -> bool:
    def _normalize(s: str) -> str:
        s = s.strip().lower()
        # Some exported banks include literal HTML entities on marker lines.
        s = s.replace("&#x20;", "")
        s = s.replace("&nbsp;", "")
        s = re.sub(r"\s+", " ", s)
        return s.strip()

    ln = _normalize(line)
    mk = _normalize(marker)
    return ln == mk or ln.startswith(mk)


def _find_marker_index(lines: List[str], marker: str) -> Optional[int]:
    for i, ln in enumerate(lines):
        if _is_marker_line(ln, marker):
            return i
    return None


def _extract_between_markers(lines: List[str], start_marker: str, end_markers: List[str]) -> List[str]:
    start_idx = _find_marker_index(lines, start_marker)
    if start_idx is None:
        return []
    end_idx = len(lines)
    for j in range(start_idx + 1, len(lines)):
        for m in end_markers:
            if _is_marker_line(lines[j], m):
                end_idx = j
                break
        if end_idx != len(lines):
            break
    return lines[start_idx + 1 : end_idx]


def _analysis_has_options_prefix(analysis: str) -> bool:
    first_nonempty = ""
    for ln in analysis.splitlines():
        if ln.strip():
            first_nonempty = ln.strip()
            break
    if not first_nonempty:
        return False
    lowered = first_nonempty.lower()
    return lowered.startswith("options:") or lowered.startswith("choices:") or lowered.startswith("选项:")


def _prepend_options_to_analysis(analysis: str, options: Dict[str, str]) -> str:
    """Add A–E option texts to analysis for readability.

    This is designed to be idempotent: if analysis already starts with an
    options/choices block, it will not add another.
    """
    analysis = _normalize_whitespace(analysis)
    if _analysis_has_options_prefix(analysis):
        return analysis

    lines: List[str] = ["Options:"]
    for letter in ["A", "B", "C", "D", "E"]:
        if letter in options:
            lines.append(f"{letter}. {options[letter]}")

    prefix = "\n".join(lines)
    if analysis:
        return f"{prefix}\n\n{analysis}"
    return prefix


def _strip_md_emphasis(text: str) -> str:
    # Keep this intentionally light-touch; we just want analysis readable in plain text.
    text = text.replace("**", "")
    # Convert markdown list bullets like "* " and "- " to "- "
    text = re.sub(r"^\s*\*\s+", "- ", text, flags=re.MULTILINE)
    # Drop remaining inline emphasis markers.
    text = text.replace("*", "")
    text = text.replace("_", "")
    return text


def _remove_markdown_headings(text: str) -> str:
    lines = []
    for ln in text.splitlines():
        if re.match(r"^\s*#{2,}\s+", ln):
            continue
        lines.append(ln)
    return "\n".join(lines)


def _clean_analysis_text(text: str) -> str:
    text = _strip_md_emphasis(_remove_markdown_headings(text))

    # Strip stray continuation markers seen in some exports.
    text = text.replace("↳", "")

    # Remove redundant lead-in like "The correct answer is B." (answer key exists separately).
    text = re.sub(
        r"^\s*The\s+correct\s+answer\s+is\s+([A-Z])\s*\.\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"^\s*Correct\s+answer\s*:\s*([A-Z])\s*\.\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Replace common LaTeX arrow notations with a plain arrow.
    text = text.replace("$\\rightarrow$", "→")
    text = text.replace("$\\to$", "→")
    text = text.replace("\\rightarrow", "→")
    text = text.replace("\\to", "→")

    # Normalize spacing around arrows.
    text = re.sub(r"\s*→\s*", " → ", text)
    text = re.sub(r"[ \t]+", " ", text)

    return _normalize_whitespace(text)


def _normalize_whitespace(text: str) -> str:
    lines = [ln.rstrip() for ln in text.splitlines()]
    # Trim leading/trailing blank lines
    while lines and lines[0].strip() == "":
        lines.pop(0)
    while lines and lines[-1].strip() == "":
        lines.pop()
    # Collapse 3+ blank lines to max 2
    out: List[str] = []
    blank_run = 0
    for ln in lines:
        if ln.strip() == "":
            blank_run += 1
            if blank_run <= 2:
                out.append("")
        else:
            blank_run = 0
            out.append(ln)
    return "\n".join(out).strip()


def _split_into_question_blocks(md: str) -> List[Tuple[str, str]]:
    """Return list of (heading_line, block_text_after_heading)."""
    lines = md.splitlines()
    indices: List[int] = []
    for i, ln in enumerate(lines):
        stripped = ln.strip()
        if QUESTION_HEADING_RE.match(stripped) or QUESTION_LABEL_RE.match(stripped):
            indices.append(i)

    blocks: List[Tuple[str, str]] = []
    for idx, start in enumerate(indices):
        end = indices[idx + 1] if idx + 1 < len(indices) else len(lines)
        heading = lines[start].strip()
        body = "\n".join(lines[start + 1 : end])
        blocks.append((heading, body))

    return blocks


def _extract_section(body: str, start_marker: str, end_markers: List[str]) -> str:
    """Extract text after start_marker until the earliest end_marker line."""
    lines = body.splitlines()
    start_idx: Optional[int] = None
    for i, ln in enumerate(lines):
        if ln.strip().startswith(start_marker):
            start_idx = i
            break
    if start_idx is None:
        return ""

    # Include any content on the marker line after the marker itself
    first_line = lines[start_idx].strip()
    after = first_line[len(start_marker) :].lstrip()

    collected: List[str] = []
    if after:
        collected.append(after)

    for j in range(start_idx + 1, len(lines)):
        if any(lines[j].strip().startswith(m) for m in end_markers):
            break
        collected.append(lines[j])

    return "\n".join(collected)


def parse_markdown(md: str) -> List[Dict]:
    blocks = _split_into_question_blocks(md)
    questions: List[Dict] = []

    for heading, body in blocks:
        heading_stripped = heading.strip()
        is_style_a = "**Question:**" in body or "**Options:**" in body or "**Analysis:**" in body

        if is_style_a:
            # Style A (legacy)
            q_text = _extract_section(body, "**Question:**", ["**Options:**", "**Analysis:**"])
            if not q_text.strip():
                before_options = body.split("**Options:**", 1)[0] if "**Options:**" in body else ""
                q_text = before_options

            q_text = _normalize_whitespace(_strip_md_emphasis(q_text))

            options_raw = _extract_section(body, "**Options:**", ["**Analysis:**"])
            options_lines = options_raw.splitlines()

            analysis = _extract_section(body, "**Analysis:**", [])
        else:
            # Style B (current)
            body_lines = body.splitlines()
            options_block = _extract_between_markers(body_lines, "Options:", ["Analysis:"])
            analysis_block = _extract_between_markers(body_lines, "Analysis:", [])

            # Everything before "Options:" is question text.
            opt_idx = _find_marker_index(body_lines, "Options:")
            question_lines = body_lines[:opt_idx] if opt_idx is not None else body_lines

            # Some banks include an explicit "Question:" marker line.
            first_nonempty_idx: Optional[int] = None
            for i, ln in enumerate(question_lines):
                if ln.strip():
                    first_nonempty_idx = i
                    break
            if first_nonempty_idx is not None and _is_marker_line(question_lines[first_nonempty_idx], "Question:"):
                question_lines = question_lines[first_nonempty_idx + 1 :]

            # Drop stray fences in question text.
            question_lines = [ln for ln in question_lines if not CODE_FENCE_RE.match(ln)]
            q_text = _normalize_whitespace(_strip_md_emphasis("\n".join(question_lines)))

            options_lines = [ln for ln in options_block if not CODE_FENCE_RE.match(ln)]
            analysis = "\n".join([ln for ln in analysis_block if not CODE_FENCE_RE.match(ln)])

        options: Dict[str, str] = {}
        correct_letter: Optional[str] = None
        current_letter: Optional[str] = None
        current_text_parts: List[str] = []

        def flush_current():
            nonlocal current_letter, current_text_parts, correct_letter
            if current_letter is None:
                return
            text = " ".join([t.strip() for t in current_text_parts if t.strip()]).strip()
            # Remove correct markers from option text
            if "✅" in text:
                correct_letter = current_letter
                text = text.replace("✅", "").strip()
            if "✔" in text:
                correct_letter = current_letter
                text = text.replace("✔", "").strip()
            options[current_letter] = _normalize_whitespace(_strip_md_emphasis(text))
            current_letter = None
            current_text_parts = []

        for ln in options_lines:
            if CODE_FENCE_RE.match(ln):
                continue
            m = OPTION_LINE_RE.match(ln)
            if m:
                flush_current()
                current_letter = m.group(1)
                current_text_parts = [m.group(2)]
            else:
                # Continuation line for previous option
                if current_letter is not None:
                    if ln.strip() == "":
                        # preserve paragraph break in long options minimally
                        current_text_parts.append(" ")
                    else:
                        current_text_parts.append(ln.strip())

        flush_current()

        analysis = _clean_analysis_text(analysis)
        analysis = _prepend_options_to_analysis(analysis, options)

        if not q_text:
            raise ValueError(f"Failed to parse question text for block: {heading}")
        if len(options) < 2:
            raise ValueError(f"Failed to parse options for block: {heading}")
        if correct_letter is None:
            raise ValueError(
                f"No correct option marked (✅/✔) for block: {heading}. "
                "Mark the correct choice with a trailing ✅ in the Markdown."
            )

        questions.append(
            {
                "question": q_text,
                "options": options,
                "answer": correct_letter,
                "analysis": analysis,
            }
        )

    return questions


def main() -> int:
    parser = argparse.ArgumentParser(description="Build questions.json from Markdown")
    parser.add_argument(
        "--input",
        default="5004question_bank.md",
        help="Path to the Markdown question bank",
    )
    parser.add_argument(
        "--output", default="questions.json", help="Path to write questions.json"
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    try:
        md = input_path.read_text(encoding="utf-8")
        questions = parse_markdown(md)

        output_path.write_text(
            json.dumps(questions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"Successfully processed '{input_path.name}'.")
        print(f"Wrote {len(questions)} questions to '{output_path.name}'.")
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        return 1
    except ValueError as e:
        print(f"Error during parsing: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
