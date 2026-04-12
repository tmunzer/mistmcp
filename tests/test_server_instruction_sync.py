"""Guardrails to keep MCP instruction object lists aligned with tool enums."""

import re

from mistmcp.server import _instructions
from mistmcp.tools.change_configuration_objects import Object_type as WriteObjectType
from mistmcp.tools.get_configuration_objects import Object_type as ReadObjectType


def _extract_table_values(section_title: str) -> set[str]:
    """Extract first-column values from a markdown table section in _instructions."""
    pattern = rf"## {re.escape(section_title)}\n(.*?)(?:\n## |\n# |\Z)"
    match = re.search(pattern, _instructions, flags=re.DOTALL)
    assert match is not None, f"Section '{section_title}' not found in instructions"

    values: set[str] = set()
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        if "object_type" in line or "org_*" in line:
            continue
        if line.startswith("| -"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if parts and parts[0]:
            values.add(parts[0])
    return values


def test_id_resolution_uses_current_device_tool() -> None:
    assert "| device MAC/ID | mist_search_device |" in _instructions


def test_site_devices_name_filter_exception_present() -> None:
    assert "`name` filtering is not supported for `site_devices`; use `mist_search_device`." in _instructions


def test_read_object_tables_match_enum_values() -> None:
    org_read = _extract_table_values("Org-Level Read Types")
    site_read = _extract_table_values("Site-Level Read Types")
    helper_read = _extract_table_values(
        "Read-Only Helper Types (mist_get_configuration_objects only)")

    documented_read = org_read | site_read | helper_read
    enum_read = {e.value for e in ReadObjectType}

    assert documented_read == enum_read


def test_write_object_table_matches_enum_values() -> None:
    documented_write = _extract_table_values("Write-Capable Object Types")
    enum_write = {e.value for e in WriteObjectType}

    assert documented_write == enum_write
