"""Validate workflow and trigger eval JSON definitions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


EVAL_SCHEMAS = {
    "evals.json": {
        "id": "integer",
        "prompt": "string",
        "expected_output": "string",
        "files": "string_list",
        "expectations": "nonempty_string_list",
    },
    "trigger-evals.json": {
        "id": "integer",
        "prompt": "string",
        "should_trigger": "boolean",
    },
}


def matches_type(value: Any, expected: str) -> bool:
    """Match one eval value against the repository's JSON conventions."""
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "string":
        return isinstance(value, str) and bool(value.strip())
    if expected == "string_list":
        return isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value)
    if expected == "nonempty_string_list":
        return bool(value) and matches_type(value, "string_list")
    raise ValueError(f"unsupported schema type: {expected}")


def validate_eval_file(path: Path, skill_name: str, repo_root: Path) -> tuple[list[str], int, int]:
    """Validate one workflow or trigger eval file and return its results."""
    errors: list[str] = []
    relative = path.relative_to(repo_root)
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"{relative}: invalid JSON: {error}"], 0, 0

    if not isinstance(document, dict):
        return [f"{relative}: top level must be an object"], 0, 0
    if set(document) != {"skill_name", "evals"}:
        errors.append(f"{relative}: top-level keys must be skill_name and evals")
    if document.get("skill_name") != skill_name:
        errors.append(f"{relative}: skill_name must be {skill_name!r}")

    cases = document.get("evals")
    if not isinstance(cases, list) or not cases:
        errors.append(f"{relative}: evals must be a non-empty array")
        return errors, 0, 0

    schema = EVAL_SCHEMAS[path.name]
    seen_ids = set()
    fixtureless = 0
    for index, case in enumerate(cases):
        location = f"{relative}: evals[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{location} must be an object")
            continue
        if set(case) != set(schema):
            errors.append(f"{location} keys must be {', '.join(schema)}")
        for field, expected in schema.items():
            if field not in case or not matches_type(case[field], expected):
                errors.append(f"{location}.{field} must be {expected.replace('_', ' ')}")
        case_id = case.get("id")
        if matches_type(case_id, "integer"):
            if case_id in seen_ids:
                errors.append(f"{location}.id duplicates {case_id}")
            seen_ids.add(case_id)
        if path.name == "evals.json" and case.get("files") == []:
            fixtureless += 1
    return errors, len(cases), fixtureless


def validate_evals(repo_root: Path, skills: list[Path]) -> tuple[list[str], dict[str, int | list[str]]]:
    """Validate all eval files and collect coverage statistics."""
    errors: list[str] = []
    workflow_cases = 0
    trigger_cases = 0
    fixtureless_cases = 0
    eval_files = 0
    missing_evals = []

    for skill in skills:
        relative = skill.relative_to(repo_root)
        eval_paths = [skill / "evals" / name for name in EVAL_SCHEMAS]
        present = [path for path in eval_paths if path.is_file()]
        if not present:
            missing_evals.append(skill.name)
            continue
        if len(present) != len(eval_paths):
            missing = [path.name for path in eval_paths if not path.is_file()]
            errors.append(f"{relative}/evals: missing {', '.join(missing)}")

        for path in present:
            eval_files += 1
            file_errors, cases, fixtureless = validate_eval_file(path, skill.name, repo_root)
            errors.extend(file_errors)
            if path.name == "evals.json":
                workflow_cases += cases
                fixtureless_cases += fixtureless
            else:
                trigger_cases += cases

        eval_directory = skill / "evals"
        unexpected = sorted(
            path.name for path in eval_directory.glob("*.json") if path.name not in EVAL_SCHEMAS
        )
        if unexpected:
            errors.append(f"{relative}/evals: unsupported JSON files: {', '.join(unexpected)}")

    return errors, {
        "eval_files": eval_files,
        "workflow_cases": workflow_cases,
        "trigger_cases": trigger_cases,
        "fixtureless_cases": fixtureless_cases,
        "missing_evals": missing_evals,
    }
