#!/usr/bin/env python3
"""Validate a normalized schema model and render an interactive ERD."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = SKILL_DIR / "assets" / "interactive-erd.html"
PLACEHOLDER = "__ERD_MODEL_JSON__"
CARDINALITIES = {"0..1", "1", "0..*", "1..*", "unknown"}
ENFORCEMENTS = {"foreign-key", "logical", "derived"}
CONSTRAINT_KINDS = {
    "primary-key",
    "unique",
    "check",
    "index",
    "exclusion",
    "invariant",
}


class ModelError(ValueError):
    """Raised when the normalized ERD model is invalid."""


def fail(path: str, message: str) -> None:
    raise ModelError(f"{path}: {message}")


def require_object(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(path, "must be an object")
    return value


def require_list(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        fail(path, "must be an array")
    return value


def require_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(path, "must be a non-empty string")
    return value


def optional_string(obj: dict[str, Any], key: str, path: str) -> None:
    if key in obj and obj[key] is not None and not isinstance(obj[key], str):
        fail(f"{path}.{key}", "must be a string")


def optional_bool(
    obj: dict[str, Any], key: str, default: bool, path: str
) -> bool:
    value = obj.get(key, default)
    if not isinstance(value, bool):
        fail(f"{path}.{key}", "must be a boolean")
    obj[key] = value
    return value


def validate_model(raw_model: Any) -> dict[str, Any]:
    """Return a normalized copy of a validated ERD model."""
    model = copy.deepcopy(require_object(raw_model, "$"))
    require_string(model.get("title"), "$.title")
    optional_string(model, "subtitle", "$")
    optional_string(model, "version", "$")

    sources = require_list(model.get("sources", []), "$.sources")
    for index, source in enumerate(sources):
        require_string(source, f"$.sources[{index}]")
    model["sources"] = sources

    groups = require_list(model.get("groups"), "$.groups")
    if not groups:
        fail("$.groups", "must contain at least one group")
    group_ids: set[str] = set()
    for index, raw_group in enumerate(groups):
        path = f"$.groups[{index}]"
        group = require_object(raw_group, path)
        group_id = require_string(group.get("id"), f"{path}.id")
        if group_id in group_ids:
            fail(f"{path}.id", f"duplicate group id {group_id!r}")
        group_ids.add(group_id)
        require_string(group.get("label"), f"{path}.label")
        optional_string(group, "description", path)

    tables = require_list(model.get("tables"), "$.tables")
    if not tables:
        fail("$.tables", "must contain at least one table")
    table_ids: set[str] = set()
    columns_by_table: dict[str, set[str]] = {}
    candidate_keys_by_table: dict[str, set[tuple[str, ...]]] = {}
    for index, raw_table in enumerate(tables):
        path = f"$.tables[{index}]"
        table = require_object(raw_table, path)
        table_id = require_string(table.get("id"), f"{path}.id")
        if table_id in table_ids:
            fail(f"{path}.id", f"duplicate table id {table_id!r}")
        table_ids.add(table_id)
        require_string(table.get("name"), f"{path}.name")
        group_id = require_string(table.get("group"), f"{path}.group")
        if group_id not in group_ids:
            fail(f"{path}.group", f"unknown group {group_id!r}")
        optional_bool(table, "existing", False, path)
        optional_string(table, "note", path)
        optional_string(table, "source", path)

        columns = require_list(table.get("columns"), f"{path}.columns")
        if not columns:
            fail(f"{path}.columns", "must contain at least one column")
        column_names: set[str] = set()
        for column_index, raw_column in enumerate(columns):
            column_path = f"{path}.columns[{column_index}]"
            column = require_object(raw_column, column_path)
            name = require_string(column.get("name"), f"{column_path}.name")
            if name in column_names:
                fail(f"{column_path}.name", f"duplicate column name {name!r}")
            column_names.add(name)
            require_string(column.get("type"), f"{column_path}.type")
            nullable = optional_bool(column, "nullable", True, column_path)
            primary_key = optional_bool(
                column, "primaryKey", False, column_path
            )
            optional_bool(column, "unique", False, column_path)
            optional_string(column, "note", column_path)
            if primary_key and nullable:
                column["nullable"] = False
        columns_by_table[table_id] = column_names
        columns_by_name = {column["name"]: column for column in columns}

        constraints = require_list(
            table.get("constraints", []), f"{path}.constraints"
        )
        table["constraints"] = constraints
        candidate_keys: set[tuple[str, ...]] = {
            (column["name"],) for column in columns if column["unique"]
        }
        flagged_primary_key = tuple(
            column["name"] for column in columns if column["primaryKey"]
        )
        if flagged_primary_key:
            candidate_keys.add(flagged_primary_key)
        structured_primary_key: tuple[str, ...] | None = None
        for constraint_index, raw_constraint in enumerate(constraints):
            constraint_path = f"{path}.constraints[{constraint_index}]"
            constraint = require_object(raw_constraint, constraint_path)
            kind = require_string(
                constraint.get("kind"), f"{constraint_path}.kind"
            )
            if kind not in CONSTRAINT_KINDS:
                fail(
                    f"{constraint_path}.kind",
                    f"must be one of {', '.join(sorted(CONSTRAINT_KINDS))}",
                )
            require_string(
                constraint.get("text"), f"{constraint_path}.text"
            )
            if kind in {"primary-key", "unique"}:
                key_columns = require_list(
                    constraint.get("columns"), f"{constraint_path}.columns"
                )
                if not key_columns:
                    fail(f"{constraint_path}.columns", "must not be empty")
                normalized_key_columns = []
                for key_index, key_column in enumerate(key_columns):
                    key_column = require_string(
                        key_column,
                        f"{constraint_path}.columns[{key_index}]",
                    )
                    if key_column not in column_names:
                        fail(
                            f"{constraint_path}.columns[{key_index}]",
                            f"unknown column {table_id}.{key_column}",
                        )
                    normalized_key_columns.append(key_column)
                if len(set(normalized_key_columns)) != len(normalized_key_columns):
                    fail(
                        f"{constraint_path}.columns",
                        "must not contain duplicates",
                    )
                constraint["columns"] = normalized_key_columns
                key_tuple = tuple(normalized_key_columns)
                candidate_keys.add(key_tuple)
                if kind == "primary-key":
                    if structured_primary_key is not None:
                        fail(path, "must not declare more than one primary key")
                    structured_primary_key = key_tuple

        if (
            structured_primary_key is not None
            and flagged_primary_key
            and structured_primary_key != flagged_primary_key
        ):
            fail(
                path,
                "primaryKey column flags conflict with the structured primary-key constraint",
            )
        if structured_primary_key is not None:
            for column_name in structured_primary_key:
                columns_by_name[column_name]["primaryKey"] = True
                columns_by_name[column_name]["nullable"] = False
        candidate_keys_by_table[table_id] = candidate_keys

    relationships = require_list(
        model.get("relationships"), "$.relationships"
    )
    relationship_ids: set[str] = set()
    for index, raw_relationship in enumerate(relationships):
        path = f"$.relationships[{index}]"
        relationship = require_object(raw_relationship, path)
        relationship_id = require_string(
            relationship.get("id"), f"{path}.id"
        )
        if relationship_id in relationship_ids:
            fail(f"{path}.id", f"duplicate relationship id {relationship_id!r}")
        relationship_ids.add(relationship_id)

        enforcement = require_string(
            relationship.get("enforcement"), f"{path}.enforcement"
        )
        if enforcement not in ENFORCEMENTS:
            fail(
                f"{path}.enforcement",
                f"must be one of {', '.join(sorted(ENFORCEMENTS))}",
            )
        optional_string(relationship, "label", path)
        optional_string(relationship, "note", path)
        optional_string(relationship, "source", path)
        optional_string(relationship, "onDelete", path)
        optional_string(relationship, "onUpdate", path)
        if enforcement != "foreign-key" and (
            relationship.get("onDelete") or relationship.get("onUpdate")
        ):
            fail(
                path,
                "onDelete and onUpdate are valid only for foreign-key relationships",
            )

        endpoints: dict[str, dict[str, Any]] = {}
        for endpoint_name in ("from", "to"):
            endpoint_path = f"{path}.{endpoint_name}"
            endpoint = require_object(
                relationship.get(endpoint_name), endpoint_path
            )
            endpoints[endpoint_name] = endpoint
            table_id = require_string(
                endpoint.get("table"), f"{endpoint_path}.table"
            )
            if table_id not in table_ids:
                fail(f"{endpoint_path}.table", f"unknown table {table_id!r}")
            columns = require_list(
                endpoint.get("columns"), f"{endpoint_path}.columns"
            )
            if not columns:
                fail(f"{endpoint_path}.columns", "must not be empty")
            normalized_columns = []
            for column_index, column in enumerate(columns):
                column = require_string(
                    column, f"{endpoint_path}.columns[{column_index}]"
                )
                normalized_columns.append(column)
                if column not in columns_by_table[table_id]:
                    fail(
                        f"{endpoint_path}.columns[{column_index}]",
                        f"unknown column {table_id}.{column}",
                    )
            if len(set(normalized_columns)) != len(normalized_columns):
                fail(f"{endpoint_path}.columns", "must not contain duplicates")
            endpoint["columns"] = normalized_columns
            cardinality = require_string(
                endpoint.get("cardinality"), f"{endpoint_path}.cardinality"
            )
            if cardinality not in CARDINALITIES:
                fail(
                    f"{endpoint_path}.cardinality",
                    f"must be one of {', '.join(sorted(CARDINALITIES))}",
                )

        if len(endpoints["from"]["columns"]) != len(
            endpoints["to"]["columns"]
        ):
            fail(path, "from.columns and to.columns must have equal length")
        if enforcement == "foreign-key":
            target_key = tuple(endpoints["to"]["columns"])
            target_table = endpoints["to"]["table"]
            if target_key not in candidate_keys_by_table[target_table]:
                fail(
                    f"{path}.to.columns",
                    "foreign-key target must match a declared primary or unique key",
                )

    return model


def load_model(path: Path) -> dict[str, Any]:
    try:
        raw_model = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ModelError(f"input file not found: {path}") from error
    except json.JSONDecodeError as error:
        raise ModelError(
            f"{path}:{error.lineno}:{error.colno}: invalid JSON: {error.msg}"
        ) from error
    except OSError as error:
        raise ModelError(f"could not read {path}: {error}") from error
    return validate_model(raw_model)


def model_json_for_html(model: dict[str, Any]) -> str:
    payload = json.dumps(
        model, ensure_ascii=False, separators=(",", ":")
    )
    return payload.replace("<", "\\u003c").replace(">", "\\u003e")


def render(model: dict[str, Any]) -> str:
    try:
        template = TEMPLATE_PATH.read_text(encoding="utf-8")
    except OSError as error:
        raise ModelError(f"could not read renderer template: {error}") from error
    if template.count(PLACEHOLDER) != 1:
        raise ModelError(
            f"renderer template must contain exactly one {PLACEHOLDER} placeholder"
        )
    return template.replace(PLACEHOLDER, model_json_for_html(model))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="normalized ERD JSON model")
    parser.add_argument("--output", type=Path, help="standalone HTML output path")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="validate the input without producing HTML",
    )
    parser.add_argument(
        "--force", action="store_true", help="replace an existing output file"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        model = load_model(args.input)
        summary = (
            f"{len(model['tables'])} tables, "
            f"{sum(len(table['columns']) for table in model['tables'])} columns, "
            f"{len(model['relationships'])} relationships"
        )
        if args.validate_only:
            print(f"Validated {args.input}: {summary}")
            return 0
        if args.output is None:
            raise ModelError("--output is required unless --validate-only is used")
        if args.output.exists() and not args.force:
            raise ModelError(
                f"output already exists: {args.output}; pass --force to replace it"
            )
        if not args.output.parent.is_dir():
            raise ModelError(f"output directory does not exist: {args.output.parent}")
        html = render(model)
        args.output.write_text(html, encoding="utf-8")
        print(f"Rendered {args.output}: {summary}")
        return 0
    except (ModelError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
