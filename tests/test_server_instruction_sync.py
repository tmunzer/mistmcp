"""Guardrails keeping server instructions aligned with the public tool catalog."""

from mistmcp.server import _instructions


REMOVED_TOOL_NAMES = {
    "mist_get_self",
    "mist_get_org_licenses",
    "mist_get_constants",
    "mist_get_configuration_object_schema",
    "mist_search_device",
    "mist_search_client",
    "mist_get_configuration_objects",
    "mist_search_device_config_history",
    "mist_search_events",
    "mist_search_audit_logs",
    "mist_search_nac_user_macs",
    "mist_list_rogue_devices",
    "mist_get_insight_metrics",
    "mist_get_site_rrm_info",
}


PUBLIC_WORKFLOW_TOOLS = {
    "mist_get_account",
    "mist_describe",
    "mist_search_assets",
    "mist_get_configuration",
    "mist_search_activity",
    "mist_search_security",
    "mist_get_site_insights",
    "mist_get_sle",
    "mist_get_stats",
    "mist_topology",
    "mist_troubleshoot",
    "mist_utilities",
    "mist_upgrades",
    "mist_get_next_page",
}


def test_instructions_route_to_every_public_workflow_tool() -> None:
    for tool_name in PUBLIC_WORKFLOW_TOOLS:
        assert f"`{tool_name}" in _instructions


def test_instructions_do_not_advertise_replaced_handlers() -> None:
    for tool_name in REMOVED_TOOL_NAMES:
        assert f"`{tool_name}`" not in _instructions
