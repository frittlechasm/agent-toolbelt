#!/usr/bin/env python3
"""Align columns in a pipe-delimited plain-text table.

Usage:
    python3 align_table.py <file_path>

Reads the file, finds all pipe-delimited table rows, aligns columns
to uniform width, and writes the result back in place.
"""

import re
import sys


def strip_markdown(text: str) -> str:
    """Remove common markdown formatting from text."""
    # Remove bold
    text = text.replace("**", "")
    # Remove markdown reference links like ([label][ref])
    text = re.sub(r"\s*\(\[.*?\]\[.*?\]\)", "", text)
    # Remove inline markdown links [text](url) -> text
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    # Remove italic (single *) but not inside words like don't
    text = re.sub(r"(?<!\w)\*([^*]+)\*(?!\w)", r"\1", text)
    # Remove common marker emojis
    text = text.replace("✅", "").replace("❌", "")
    return text.strip()


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 align_table.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    strip = "--strip" in sys.argv

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

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
            non_table[i] = line

    if not table_rows:
        print("No table found in file.")
        sys.exit(0)

    # Calculate column widths from non-separator rows
    data_rows = [r for r in table_rows if r is not None]
    if not data_rows:
        print("No data rows found.")
        sys.exit(0)

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

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(output_lines)

    print(f"Done. Aligned {len(table_indices)} table rows ({num_cols} columns).")


if __name__ == "__main__":
    main()
