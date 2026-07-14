"""Tests ensuring facade tools survive OpenAPI regeneration."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mcp_generator import generate_from_openapi as generator  # noqa: E402

REPLACED_TOOL_NAMES = set().union(
    *(facade["replaces"] for facade in generator.FACADE_TOOLS)
)


def test_replaced_source_files_do_not_exist() -> None:
    existing = [
        tool_name
        for tool_name in REPLACED_TOOL_NAMES
        if (generator.OUTPUT_DIR / f"{tool_name.removeprefix('mist_')}.py").exists()
    ]
    assert existing == []


def test_every_preserved_facade_source_exists() -> None:
    missing = [
        filename
        for filename in generator.PRESERVED_TOOL_FILES
        if not (generator.OUTPUT_DIR / filename).is_file()
    ]
    assert missing == []


def test_preserved_sources_round_trip(monkeypatch, tmp_path: Path) -> None:
    source_dir = generator.OUTPUT_DIR
    monkeypatch.setattr(generator, "OUTPUT_DIR", tmp_path)

    for filename in generator.PRESERVED_TOOL_FILES:
        (tmp_path / filename).write_text(
            (source_dir / filename).read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    preserved = generator._read_preserved_tool_files()
    for filename in generator.PRESERVED_TOOL_FILES:
        (tmp_path / filename).unlink()
    generator._restore_preserved_tool_files(preserved)

    assert (
        set(path.name for path in tmp_path.iterdir()) == generator.PRESERVED_TOOL_FILES
    )


def test_generator_removes_replaced_source_files(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(generator, "OUTPUT_DIR", tmp_path)
    for tool_name in REPLACED_TOOL_NAMES:
        (tmp_path / f"{tool_name.removeprefix('mist_')}.py").write_text(
            "generated endpoint module", encoding="utf-8"
        )

    generator._remove_replaced_tool_files()

    assert list(tmp_path.iterdir()) == []


def test_apply_facade_catalog_removes_handlers_and_adds_facades() -> None:
    tag_defs = {
        facade["tag"]: {
            "description": "test",
            "tools": sorted(facade["replaces"]),
        }
        for facade in generator.FACADE_TOOLS
    }

    generator._apply_facade_catalog(tag_defs)

    exposed = {
        tool_name for tag_data in tag_defs.values() for tool_name in tag_data["tools"]
    }
    assert exposed == {facade["name"] for facade in generator.FACADE_TOOLS}
    assert not (exposed & REPLACED_TOOL_NAMES)


def test_configuration_template_keeps_facade_regression_fixes() -> None:
    template = (ROOT / "mcp_generator/templates/tmpl_get_configuration_objets.py").read_text(
        encoding="utf-8"
    )
    org_services = template.split('case "org_services":', 1)[1].split(
        'case "org_servicepolicies":', 1
    )[0]
    assert "services.listOrgServices" in org_services
    assert "networktemplates.listOrgNetworkTemplates" not in org_services
    assert "computed=computed if computed else None" in template
    assert '_search_object(assigned_wlans, name, "ssid"' in template


def test_search_client_template_serializes_band_enum_value() -> None:
    template = (ROOT / "mcp_generator/templates/tmpl_search_client.py").read_text(
        encoding="utf-8"
    )
    assert "band=band.value if band else None" in template
    assert "band=str(band) if band else None" not in template
