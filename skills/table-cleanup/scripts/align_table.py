#!/usr/bin/env python3
"""Align columns in a pipe-delimited plain-text table.

Usage:
    python3 align_table.py [--strip] [--in-place] <file_path|->

Reads the file, finds all pipe-delimited table rows, aligns columns
to uniform width, and prints the result to stdout by default.
"""

import re
import sys


def strip_markdown(text: str) -> str:
    """Remove common markdown formatting from text."""
    # Remove bold
    text = text.replace("**", "")
    # Remove inline code markers while preserving the code/value text
    text = re.sub(r"`([^`]+)`", r"\1", text)
    # Remove markdown reference links like ([label][ref])
    text = re.sub(r"\s*\(\[.*?\]\[.*?\]\)", "", text)
    # Remove inline markdown links [text](url) -> text
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    # Remove italic (single *) but not inside words like don't
    text = re.sub(r"(?<!\w)\*([^*]+)\*(?!\w)", r"\1", text)
    # Remove common marker emojis
    text = text.replace("✅", "").replace("❌", "")
    return text.strip()


def strip_non_table_markdown(line: str) -> str:
    """Remove markdown artifacts from non-table lines while preserving content."""
    if re.match(r"^\s*\[[^\]]+\]:\s+\S+", line):
        return ""
    return strip_markdown(line.rstrip("\n")) + ("\n" if line.endswith("\n") else "")


def align_table(lines: list[str], strip: bool = False) -> list[str]:
    """Return table-aligned lines without mutating the source file."""

    # Identify table lines (start with |)
    table_indices = []
    table_rows = []
    non_table = {}

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("|"):
            cells = [c.strip() for c in stripped.split("|")]
            cells = cells[1:-1]  # drop empty first/last from leading/trailing pipes

            # Check if this is a separator row
            if cells and all(re.match(r"^[-:]+$", c) for c in cells):
                table_indices.append(i)
                table_rows.append(None)  # sentinel for separator
            else:
                if strip:
                    cells = [strip_markdown(c) for c in cells]
                table_indices.append(i)
                table_rows.append(cells)
        else:
            non_table[i] = strip_non_table_markdown(line) if strip else line

    if not table_rows:
        return lines

    # Calculate column widths from non-separator rows
    data_rows = [r for r in table_rows if r is not None]
    if not data_rows:
        return lines

    num_cols = max(len(r) for r in data_rows)
    col_widths = [0] * num_cols
    for row in data_rows:
        for j, cell in enumerate(row):
            col_widths[j] = max(col_widths[j], len(cell))

    # Rebuild lines
    def format_row(cells):
        parts = []
        for j in range(num_cols):
            cell = cells[j] if j < len(cells) else ""
            parts.append(" " + cell.ljust(col_widths[j]) + " ")
        return "|" + "|".join(parts) + "|"

    def format_separator():
        parts = ["-" * (w + 2) for w in col_widths]
        return "|" + "|".join(parts) + "|"

    output_lines = [""] * len(lines)

    # Place non-table lines
    for i, line in non_table.items():
        output_lines[i] = line

    # Place table lines
    for idx, row in zip(table_indices, table_rows):
        if row is None:
            output_lines[idx] = format_separator() + "\n"
        else:
            output_lines[idx] = format_row(row) + "\n"

    return output_lines


def main():
    args = sys.argv[1:]
    strip = "--strip" in args
    in_place = "--in-place" in args
    paths = [arg for arg in args if not arg.startswith("--")]

    if len(paths) != 1:
        print("Usage: python3 align_table.py [--strip] [--in-place] <file_path|->", file=sys.stderr)
        sys.exit(1)

    file_path = paths[0]
    if file_path == "-":
        lines = sys.stdin.readlines()
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

    output_lines = align_table(lines, strip=strip)

    if in_place:
        if file_path == "-":
            print("--in-place requires a file path, not stdin", file=sys.stderr)
            sys.exit(1)
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(output_lines)
        return

    sys.stdout.writelines(output_lines)


if __name__ == "__main__":
    main()
