#!/usr/bin/env python3
"""Strip Markdown and align pipe tables without changing the source by default."""

import argparse
import re
import sys
import unicodedata


def strip_markdown(text: str) -> str:
    """Remove supported Markdown while preserving cell values."""
    text = text.replace("**", "")
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\s*\(\[.*?\]\[.*?\]\)", "", text)
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    text = re.sub(r"(?<!\w)\*([^*]+)\*(?!\w)", r"\1", text)
    return text.strip()


def strip_non_table_markdown(line: str) -> str:
    """Remove supported Markdown from prose and reference definitions."""
    if re.match(r"^\s*\[[^\]]+\]:\s+\S+", line):
        return ""
    newline = "\n" if line.endswith("\n") else ""
    return strip_markdown(line.rstrip("\n")) + newline


def split_row(line: str) -> list[str] | None:
    """Split unescaped pipes outside inline code."""
    text = line.strip()
    cells = [""]
    in_code = False
    escaped = False
    trailing_delimiter = False

    for char in text:
        if escaped:
            cells[-1] += char
            escaped = False
            trailing_delimiter = False
        elif char == "\\":
            cells[-1] += char
            escaped = True
            trailing_delimiter = False
        elif char == "`":
            cells[-1] += char
            in_code = not in_code
            trailing_delimiter = False
        elif char == "|" and not in_code:
            cells.append("")
            trailing_delimiter = True
        else:
            cells[-1] += char
            trailing_delimiter = False

    if text.startswith("|"):
        cells.pop(0)
    if trailing_delimiter and cells:
        cells.pop()

    cells = [cell.strip() for cell in cells]
    return cells if len(cells) >= 2 else None


def is_separator(cells: list[str]) -> bool:
    return all(re.fullmatch(r":?-+:?", cell) for cell in cells)


def display_width(text: str) -> int:
    """Return terminal width for common Unicode text."""
    width = 0
    for char in text:
        if unicodedata.category(char) in {"Mn", "Me", "Cf"}:
            continue
        width += 2 if unicodedata.east_asian_width(char) in {"W", "F"} else 1
    return width


def pad(text: str, width: int) -> str:
    return text + " " * (width - display_width(text))


def find_tables(rows: list[list[str] | None]) -> list[tuple[int, int]]:
    """Find Markdown tables anchored by a header separator row."""
    tables = []
    claimed_until = -1

    for index, row in enumerate(rows):
        if index <= claimed_until or row is None or not is_separator(row):
            continue

        header = rows[index - 1] if index else None
        if header is None or is_separator(header) or len(header) != len(row):
            continue

        end = index
        while end + 1 < len(rows):
            next_row = rows[end + 1]
            if next_row is None or is_separator(next_row) or len(next_row) != len(row):
                break
            following_row = rows[end + 2] if end + 2 < len(rows) else None
            if following_row is not None and is_separator(following_row) and len(following_row) == len(row):
                break
            end += 1

        tables.append((index - 1, end))
        claimed_until = end

    return tables


def align_table(lines: list[str], strip: bool = False) -> list[str]:
    """Return aligned Markdown tables while preserving surrounding prose."""
    rows = [split_row(line) for line in lines]
    tables = find_tables(rows)
    if not tables:
        return lines

    output = [strip_non_table_markdown(line) if strip else line for line in lines]

    for start, end in tables:
        table_rows = [rows[index] for index in range(start, end + 1)]
        normalized = {}
        for index in range(start, end + 1):
            row = rows[index]
            assert row is not None
            if is_separator(row):
                continue
            if strip:
                row = [strip_markdown(cell) for cell in row]
            normalized[index] = [re.sub(r"(?<!\\)\|", r"\\|", cell) for cell in row]

        data_rows = list(normalized.values())
        widths = [max(display_width(row[column]) for row in data_rows) for column in range(len(data_rows[0]))]

        for index in range(start, end + 1):
            row = rows[index]
            assert row is not None
            newline = "\n" if lines[index].endswith("\n") else ""

            if is_separator(row):
                output[index] = "|" + "|".join("-" * (width + 2) for width in widths) + "|" + newline
                continue

            row = normalized[index]
            output[index] = "|" + "|".join(f" {pad(cell, widths[column])} " for column, cell in enumerate(row)) + "|" + newline

    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strip", action="store_true")
    parser.add_argument("--in-place", action="store_true")
    parser.add_argument("file_path")
    args = parser.parse_args()

    if args.file_path == "-":
        if args.in_place:
            parser.error("--in-place requires a file path")
        lines = sys.stdin.readlines()
    else:
        with open(args.file_path, encoding="utf-8") as source:
            lines = source.readlines()

    output = align_table(lines, strip=args.strip)
    if args.in_place:
        with open(args.file_path, "w", encoding="utf-8") as target:
            target.writelines(output)
    else:
        sys.stdout.writelines(output)


if __name__ == "__main__":
    main()
