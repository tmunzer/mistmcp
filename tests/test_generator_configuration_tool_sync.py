"""Guardrails to keep aggregated configuration tool generation deterministic."""

from pathlib import Path

import yaml

from mcp_generator.templates.tmpl_tool_change_configuration_objects import (
    CHANGE_CONFIGURATION_OBJECTS_TEMPLATE,
)
from mcp_generator.templates.tmpl_tool_update_configuration_objects import (
    UPDATE_CONFIGURATION_OBJECTS_TEMPLATE,
)

ROOT = Path(__file__).resolve().parents[1]
TOOLS_OPTIMIZATION_PATH = ROOT / "mcp_generator" / "tools_optimization.yaml"
CHANGE_TOOL_PATH = ROOT / "src" / "mistmcp" / \
    "tools" / "change_configuration_objects.py"
UPDATE_TOOL_PATH = ROOT / "src" / "mistmcp" / \
    "tools" / "update_configuration_objects.py"


def _normalize_leading_blank_lines(content: str) -> str:
    return content.lstrip("\n")


def test_aggregated_configuration_entries_are_not_in_optimization_yaml() -> None:
    data = yaml.safe_load(
        TOOLS_OPTIMIZATION_PATH.read_text(encoding="utf-8")) or {}
    assert "changeConfigurationObjects" not in data
    assert "updateConfigurationObjects" not in data


def test_change_configuration_tool_matches_generator_template() -> None:
    current = CHANGE_TOOL_PATH.read_text(encoding="utf-8")
    assert _normalize_leading_blank_lines(current) == _normalize_leading_blank_lines(
        CHANGE_CONFIGURATION_OBJECTS_TEMPLATE
    )


def test_update_configuration_tool_matches_generator_template() -> None:
    current = UPDATE_TOOL_PATH.read_text(encoding="utf-8")
    assert _normalize_leading_blank_lines(current) == _normalize_leading_blank_lines(
        UPDATE_CONFIGURATION_OBJECTS_TEMPLATE
    )
