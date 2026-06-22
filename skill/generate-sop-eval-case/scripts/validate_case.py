#!/usr/bin/env python3
"""Validate a generated SOP evaluation case."""

from __future__ import annotations

import argparse
import re
import json
import sys
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parents[1]
SCHEMA_DIR = SKILL_DIR / "schemas"

CASE_FILES = {
    "item_change_ticket": "item_change_ticket.json",
    "white_screen_logs": "white_screen_logs.json",
    "black_screen_logs": "black_screen_logs.json",
    "screen_semantic_events": "screen_semantic_events.json",
    "ground_truth": "ground_truth.json"
}

SCHEMA_FILES = {
    "item_change_ticket": "item_change_ticket.schema.json",
    "white_screen_logs": "white_screen_logs.schema.json",
    "black_screen_logs": "black_screen_logs.schema.json",
    "screen_semantic_events": "screen_semantic_events.schema.json",
    "ground_truth": "ground_truth.schema.json"
}

FORBIDDEN_FIELDS = {
    "对应SOP阶段",
    "对应SOP步骤ID",
    "对应SOP步骤名称",
    "candidate_expected_event_id",
    "expected_event_id",
    "sop_phase",
    "sop_step_name"
}

QUESTION_FILES = {
    "white_screen_logs",
    "black_screen_logs",
    "screen_semantic_events"
}

PLACEHOLDER_PATTERNS = [
    re.compile(r"<[^>]+>"),
    re.compile(r"\bresource-bucket\b"),
    re.compile(r"\bbiz_timestamp\b"),
    re.compile(r"\$\{[^}]+\}")
]

DATE_TOKEN_RE = re.compile(r"20\d{6}")


class ValidationError(Exception):
    pass


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as exc:
        raise ValidationError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON: {path}: {exc}") from exc


def require_type(value: Any, expected: Any, path: str) -> None:
    if isinstance(expected, list):
        if not any(_type_matches(value, item) for item in expected):
            raise ValidationError(f"{path}: expected one of {expected}, got {type(value).__name__}")
        return
    if not _type_matches(value, expected):
        raise ValidationError(f"{path}: expected {expected}, got {type(value).__name__}")


def _type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return True


def resolve_ref(schema: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/$defs/"):
        raise ValidationError(f"unsupported schema ref: {ref}")
    name = ref.split("/")[-1]
    return schema["$defs"][name]


def validate_schema(value: Any, rule: dict[str, Any], root: dict[str, Any], path: str = "$") -> None:
    if "$ref" in rule:
        validate_schema(value, resolve_ref(root, rule["$ref"]), root, path)
        return

    if "type" in rule:
        require_type(value, rule["type"], path)

    if "enum" in rule and value not in rule["enum"]:
        raise ValidationError(f"{path}: expected enum {rule['enum']}, got {value!r}")

    rule_type = rule.get("type")
    if rule_type == "object" or (isinstance(rule_type, list) and "object" in rule_type and isinstance(value, dict)):
        if not isinstance(value, dict):
            return
        required = rule.get("required", [])
        for key in required:
            if key not in value:
                raise ValidationError(f"{path}: missing required key {key!r}")
        props = rule.get("properties", {})
        if rule.get("additionalProperties") is False:
            extra = set(value) - set(props)
            if extra:
                raise ValidationError(f"{path}: additional properties not allowed: {sorted(extra)}")
        for key, item in value.items():
            if key in props:
                validate_schema(item, props[key], root, f"{path}.{key}")

    if rule_type == "array" or (isinstance(rule_type, list) and "array" in rule_type and isinstance(value, list)):
        if not isinstance(value, list):
            return
        item_rule = rule.get("items")
        if item_rule:
            for index, item in enumerate(value):
                validate_schema(item, item_rule, root, f"{path}[{index}]")


def find_forbidden_fields(value: Any, path: str = "$") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            item_path = f"{path}.{key}"
            if key in FORBIDDEN_FIELDS:
                hits.append(item_path)
            hits.extend(find_forbidden_fields(item, item_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            hits.extend(find_forbidden_fields(item, f"{path}[{index}]"))
    return hits


def iter_strings(value: Any, path: str = "$"):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from iter_strings(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from iter_strings(item, f"{path}[{index}]")
    elif isinstance(value, str):
        yield path, value


def find_placeholders(value: Any) -> list[str]:
    hits: list[str] = []
    for path, text in iter_strings(value):
        if re.fullmatch(r"\$\.custom_variable\[\d+\]", path):
            if "=" in text:
                hits.append(f"{path}: custom_variable should contain variable names, not assignments: {text}")
            continue
        for pattern in PLACEHOLDER_PATTERNS:
            if pattern.search(text):
                hits.append(f"{path}: {text}")
                break
    return hits


def find_invalid_dates(value: Any) -> list[str]:
    hits: list[str] = []
    for path, text in iter_strings(value):
        for token in DATE_TOKEN_RE.findall(text):
            month = int(token[4:6])
            day = int(token[6:8])
            if month < 1 or month > 12 or day < 1 or day > 31:
                hits.append(f"{path}: invalid date token {token!r} in {text!r}")
    return hits


def collect_sop_steps(ticket: dict[str, Any]) -> set[tuple[str, str]]:
    steps: set[tuple[str, str]] = set()
    for phase in ("check_before_change", "change_implement", "change_verified", "change_rollback"):
        for step in ticket.get(phase, []):
            steps.add((phase, step.get("sop_step_id", "")))
    return steps


def collect_case_ids(data: dict[str, Any]) -> dict[str, set[str]]:
    return {
        "white_log_ids": {log.get("日志ID") for log in data["white_screen_logs"].get("logs", []) if log.get("日志ID")},
        "black_log_ids": {
            log.get("堡垒机内部单号")
            for log in data["black_screen_logs"].get("logs", [])
            if log.get("堡垒机内部单号")
        },
        "semantic_event_ids": {
            event.get("event_id")
            for event in data["screen_semantic_events"].get("events", [])
            if event.get("event_id")
        },
        "expected_event_ids": {
            mapping.get("expected_event_id")
            for mapping in data["ground_truth"].get("mappings", [])
            if mapping.get("expected_event_id")
        }
    }


def case_shape_signature(data: dict[str, Any]) -> tuple[Any, ...]:
    ticket = data["item_change_ticket"]
    phase_names = []
    for phase in ("check_before_change", "change_implement", "change_verified", "change_rollback"):
        phase_names.append(tuple(step.get("check_name", "") for step in ticket.get(phase, [])))
    return (
        tuple(phase_names),
        len(data["white_screen_logs"].get("logs", [])),
        len(data["black_screen_logs"].get("logs", [])),
        len(data["screen_semantic_events"].get("events", [])),
        len(data["ground_truth"].get("mappings", []))
    )


def validate_case(case_dir: Path) -> list[str]:
    errors: list[str] = []
    data: dict[str, Any] = {}

    for name, filename in CASE_FILES.items():
        try:
            data[name] = load_json(case_dir / filename)
        except ValidationError as exc:
            errors.append(str(exc))

    if errors:
        return errors

    for name, schema_file in SCHEMA_FILES.items():
        schema = load_json(SCHEMA_DIR / schema_file)
        try:
            validate_schema(data[name], schema, schema)
        except ValidationError as exc:
            errors.append(f"{CASE_FILES[name]} schema failed: {exc}")

    for name in QUESTION_FILES:
        hits = find_forbidden_fields(data[name])
        if hits:
            errors.append(f"{CASE_FILES[name]} contains forbidden answer fields: {', '.join(hits)}")

    for name, value in data.items():
        placeholder_hits = find_placeholders(value)
        if placeholder_hits:
            errors.append(f"{CASE_FILES[name]} contains uninstantiated placeholders: {'; '.join(placeholder_hits[:5])}")
        invalid_date_hits = find_invalid_dates(value)
        if invalid_date_hits:
            errors.append(f"{CASE_FILES[name]} contains invalid date-like tokens: {'; '.join(invalid_date_hits[:5])}")

    for step in data["item_change_ticket"].get("change_implement", []):
        if len(step.get("command_list", [])) > 1:
            errors.append(
                "item_change_ticket.json has a change_implement step with multiple commands; "
                f"split operationally distinct commands into separate steps: {step.get('sop_step_id')}"
            )

    change_ids = {
        name: value.get("change_instance_id")
        for name, value in data.items()
        if name != "item_change_ticket" and isinstance(value, dict)
    }
    unique_change_ids = {item for item in change_ids.values() if item}
    if len(unique_change_ids) > 1:
        errors.append(f"change_instance_id mismatch: {change_ids}")
    gt_change_id = data["ground_truth"].get("change_instance_id")
    if gt_change_id and unique_change_ids and gt_change_id not in unique_change_ids:
        errors.append(f"ground_truth change_instance_id {gt_change_id!r} not found in evidence files")

    white_ids = {log.get("日志ID") for log in data["white_screen_logs"].get("logs", [])}
    black_ids = {log.get("堡垒机内部单号") for log in data["black_screen_logs"].get("logs", [])}
    event_ids = {event.get("event_id") for event in data["screen_semantic_events"].get("events", [])}
    sop_steps = collect_sop_steps(data["item_change_ticket"])

    for index, mapping in enumerate(data["ground_truth"].get("mappings", [])):
        prefix = f"ground_truth.mappings[{index}]"
        step_key = (mapping.get("sop_phase"), mapping.get("sop_step_id"))
        if step_key not in sop_steps:
            errors.append(f"{prefix}: SOP step does not exist: {step_key}")
        evidence_count = (
            len(mapping.get("white_log_ids", []))
            + len(mapping.get("black_log_ids", []))
            + len(mapping.get("semantic_event_ids", []))
        )
        if evidence_count == 0:
            errors.append(f"{prefix}: mapping has no evidence ids")
        for log_id in mapping.get("white_log_ids", []):
            if log_id not in white_ids:
                errors.append(f"{prefix}: missing white log id {log_id!r}")
        for log_id in mapping.get("black_log_ids", []):
            if log_id not in black_ids:
                errors.append(f"{prefix}: missing black log id {log_id!r}")
        for event_id in mapping.get("semantic_event_ids", []):
            if event_id not in event_ids:
                errors.append(f"{prefix}: missing semantic event id {event_id!r}")

    for event in data["screen_semantic_events"].get("events", []):
        for evidence in event.get("evidence_refs", []):
            table = evidence.get("log_table")
            log_id = evidence.get("log_id")
            if table == "white_screen" and log_id not in white_ids:
                errors.append(f"{event.get('event_id')}: evidence missing white log id {log_id!r}")
            if table == "black_screen" and log_id not in black_ids:
                errors.append(f"{event.get('event_id')}: evidence missing black log id {log_id!r}")

    return errors


def validate_batch(base_dir: Path) -> list[str]:
    errors: list[str] = []
    case_dirs = sorted(path for path in base_dir.iterdir() if path.is_dir() and path.name.startswith("case_"))
    if not case_dirs:
        return [f"no case_* directories found under {base_dir}"]

    shapes: dict[str, tuple[Any, ...]] = {}
    seen_ids: dict[str, dict[str, str]] = {
        "white_log_ids": {},
        "black_log_ids": {},
        "semantic_event_ids": {},
        "expected_event_ids": {}
    }

    for case_dir in case_dirs:
        case_errors = validate_case(case_dir)
        errors.extend(f"{case_dir.name}: {error}" for error in case_errors)
        if case_errors:
            continue

        data = {name: load_json(case_dir / filename) for name, filename in CASE_FILES.items()}
        shapes[case_dir.name] = case_shape_signature(data)
        for id_group, ids in collect_case_ids(data).items():
            for item_id in ids:
                previous = seen_ids[id_group].get(item_id)
                if previous:
                    errors.append(f"{case_dir.name}: duplicate {id_group} {item_id!r}, already used by {previous}")
                else:
                    seen_ids[id_group][item_id] = case_dir.name

    if len(case_dirs) >= 3 and len(set(shapes.values())) == 1:
        errors.append(
            "batch appears fully template-homogeneous: all cases have the same phase steps and evidence counts"
        )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a SOP evaluation case directory.")
    parser.add_argument("case_dir", type=Path)
    parser.add_argument("--batch", action="store_true", help="Validate a directory containing case_* subdirectories.")
    args = parser.parse_args()

    target = args.case_dir.resolve()
    if args.batch or not (target / CASE_FILES["item_change_ticket"]).exists():
        errors = validate_batch(target)
    else:
        errors = validate_case(target)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("OK: case validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
