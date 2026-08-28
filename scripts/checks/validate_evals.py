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
OPTIONAL_EVAL_FIELDS = {
    "evals.json": {"setup": "nonempty_string_list"},
    "trigger-evals.json": {},
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
    optional = OPTIONAL_EVAL_FIELDS[path.name]
    seen_ids = set()
    setup_cases = 0
    for index, case in enumerate(cases):
        location = f"{relative}: evals[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{location} must be an object")
            continue
        missing = set(schema) - set(case)
        unexpected = set(case) - set(schema) - set(optional)
        if missing:
            errors.append(f"{location} missing keys: {', '.join(sorted(missing))}")
        if unexpected:
            errors.append(f"{location} unsupported keys: {', '.join(sorted(unexpected))}")
        for field, expected in schema.items():
            if field not in case or not matches_type(case[field], expected):
                errors.append(f"{location}.{field} must be {expected.replace('_', ' ')}")
        for field, expected in optional.items():
            if field in case and not matches_type(case[field], expected):
                errors.append(f"{location}.{field} must be {expected.replace('_', ' ')}")
        case_id = case.get("id")
        if matches_type(case_id, "integer"):
            if case_id in seen_ids:
                errors.append(f"{location}.id duplicates {case_id}")
            seen_ids.add(case_id)
        if path.name == "evals.json" and "setup" in case:
            setup_cases += 1
    return errors, len(cases), setup_cases


def validate_evals(repo_root: Path, skills: list[Path]) -> tuple[list[str], dict[str, int | list[str]]]:
    """Validate all eval files and collect coverage statistics."""
    errors: list[str] = []
    workflow_cases = 0
    trigger_cases = 0
    setup_cases = 0
    eval_files = 0
    missing_workflow_evals = []
    missing_trigger_evals = []

    for skill in skills:
        relative = skill.relative_to(repo_root)
        eval_paths = {name: skill / "evals" / name for name in EVAL_SCHEMAS}
        if not eval_paths["evals.json"].is_file():
            missing_workflow_evals.append(skill.name)
        if not eval_paths["trigger-evals.json"].is_file():
            missing_trigger_evals.append(skill.name)

        for path in (path for path in eval_paths.values() if path.is_file()):
            eval_files += 1
            file_errors, cases, file_setup_cases = validate_eval_file(path, skill.name, repo_root)
            errors.extend(file_errors)
            if path.name == "evals.json":
                workflow_cases += cases
                setup_cases += file_setup_cases
            else:
                trigger_cases += cases

        unexpected = sorted(
            path.name
            for path in (skill / "evals").glob("*.json")
            if path.name not in EVAL_SCHEMAS
        )
        if unexpected:
            errors.append(f"{relative}/evals: unsupported JSON files: {', '.join(unexpected)}")

    return errors, {
        "eval_files": eval_files,
        "workflow_cases": workflow_cases,
        "trigger_cases": trigger_cases,
        "setup_cases": setup_cases,
        "missing_workflow_evals": missing_workflow_evals,
        "missing_trigger_evals": missing_trigger_evals,
    }
