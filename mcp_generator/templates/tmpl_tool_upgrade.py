UPGRADE_OPERATIONS = [
    "cancelOrgDeviceUpgrade",
    "cancelOrgMxEdgeUpgrade",
    "cancelOrgSsrUpgrade",
    "cancelSiteMxEdgeUpgrade",
    "getOrgDeviceUpgrade",
    "getOrgMxEdgeUpgrade",
    "getOrgSsrUpgrade",
    "getSiteMxEdgeUpgrade",
    "upgradeOrgDevices",
    "upgradeOrgMxEdges",
    "upgradeOrgSsrs",
    "upgradeSiteMxEdges",
]

# Template for individual tool files
TOOL_TEMPLATE_UPGRADE = '''"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import json
from enum import Enum
from typing import Annotated, Any
from uuid import UUID

import mistapi
from fastmcp import Context
from fastmcp.exceptions import ToolError
from pydantic import Field

from mistmcp.elicitation_processor import config_elicitation_handler
from mistmcp.logger import logger
from mistmcp.request_processor import get_apisession
from mistmcp.response_formatter import format_response
from mistmcp.response_processor import handle_network_error, process_response
from mistmcp.server import mcp


class UpgradeActionType(Enum):
    CANCEL_ORG_DEVICE_UPGRADE = "cancel_org_device_upgrade"
    CANCEL_ORG_MX_EDGE_UPGRADE = "cancel_org_mx_edge_upgrade"
    CANCEL_ORG_SSR_UPGRADE = "cancel_org_ssr_upgrade"
    CANCEL_SITE_MX_EDGE_UPGRADE = "cancel_site_mx_edge_upgrade"
    GET_ORG_DEVICE_UPGRADE = "get_org_device_upgrade"
    GET_ORG_MX_EDGE_UPGRADE = "get_org_mx_edge_upgrade"
    GET_ORG_SSR_UPGRADE = "get_org_ssr_upgrade"
    GET_SITE_MX_EDGE_UPGRADE = "get_site_mx_edge_upgrade"
    LIST_ORG_AVAILABLE_DEVICE_VERSIONS = "list_org_available_device_versions"
    LIST_ORG_AVAILABLE_SSR_VERSIONS = "list_org_available_ssr_versions"
    LIST_ORG_DEVICE_UPGRADES = "list_org_device_upgrades"
    LIST_ORG_MX_EDGE_UPGRADES = "list_org_mx_edge_upgrades"
    LIST_ORG_SSR_UPGRADES = "list_org_ssr_upgrades"
    LIST_SITE_AVAILABLE_DEVICE_VERSIONS = "list_site_available_device_versions"
    LIST_SITE_MX_EDGE_UPGRADES = "list_site_mx_edge_upgrades"
    UPGRADE_ORG_DEVICES = "upgrade_org_devices"
    UPGRADE_ORG_MX_EDGES = "upgrade_org_mx_edges"
    UPGRADE_ORG_SSRS = "upgrade_org_ssrs"
    UPGRADE_SITE_MX_EDGES = "upgrade_site_mx_edges"


class FirmwareType(Enum):
    AP = "ap"
    SWITCH = "switch"
    GATEWAY = "gateway"


class Channel(Enum):
    ALPHA = "alpha"
    BETA = "beta"
    STABLE = "stable"


MUTATING_UPGRADE_ACTIONS = {
    UpgradeActionType.CANCEL_ORG_DEVICE_UPGRADE,
    UpgradeActionType.CANCEL_ORG_MX_EDGE_UPGRADE,
    UpgradeActionType.CANCEL_ORG_SSR_UPGRADE,
    UpgradeActionType.CANCEL_SITE_MX_EDGE_UPGRADE,
    UpgradeActionType.UPGRADE_ORG_DEVICES,
    UpgradeActionType.UPGRADE_ORG_MX_EDGES,
    UpgradeActionType.UPGRADE_ORG_SSRS,
    UpgradeActionType.UPGRADE_SITE_MX_EDGES,
}

PAYLOAD_REQUIRED_ACTIONS = {
    UpgradeActionType.UPGRADE_ORG_DEVICES,
    UpgradeActionType.UPGRADE_ORG_MX_EDGES,
    UpgradeActionType.UPGRADE_ORG_SSRS,
    UpgradeActionType.UPGRADE_SITE_MX_EDGES,
}

PAYLOAD_CONTRACTS: dict[UpgradeActionType, dict[str, Any]] = {
    UpgradeActionType.UPGRADE_ORG_DEVICES: {
        "schema": "upgrade_org_devices",
        "required": [],
        "attributes": [
            "all_sites",
            "canary_phases",
            "device_type",
            "download_strategy",
            "max_failure_percentage",
            "max_failures",
            "models",
            "p2p_cluster_size",
            "p2p_parallelism",
            "reboot_at",
            "reboot_datetime",
            "reboot_strategy",
            "rrm_first_batch_percentage",
            "rrm_max_batch_percentage",
            "rrm_mesh_upgrade",
            "rrm_node_order",
            "rrm_slow_ramp",
            "rules",
            "site_ids",
            "snapshot",
            "start_datetime",
            "start_time",
            "strategy",
            "versions",
        ],
        "attribute_descriptions": {
            "all_sites": "When true, applies the upgrade across all organization sites.",
            "canary_phases": "Canary rollout percentages. Used when strategy is canary.",
            "device_type": "Target device type for this upgrade batch.",
            "download_strategy": "Image download strategy before reboot/activation.",
            "max_failure_percentage": "Stop rollout when failure percentage exceeds this threshold.",
            "max_failures": "Stop rollout when the absolute failure count exceeds this value.",
            "models": "Optional list of hardware models to target.",
            "p2p_cluster_size": "Peer-to-peer download cluster size.",
            "p2p_parallelism": "Number of peer-to-peer download groups processed in parallel.",
            "reboot_at": "Epoch timestamp for scheduled reboot.",
            "reboot_datetime": "Datetime string for scheduled reboot.",
            "reboot_strategy": "How reboots are orchestrated across devices.",
            "rrm_first_batch_percentage": "First rollout batch size percentage when using RRM strategy.",
            "rrm_max_batch_percentage": "Maximum rollout batch size percentage when using RRM strategy.",
            "rrm_mesh_upgrade": "RRM mesh upgrade behavior control.",
            "rrm_node_order": "Node ordering policy for RRM/mesh rollout.",
            "rrm_slow_ramp": "Enable slower progressive ramp-up for rollout.",
            "rules": "Selection rules to match devices by attributes such as name/model/role.",
            "site_ids": "Optional list of site IDs to scope the upgrade.",
            "snapshot": "When true, create a snapshot before upgrading.",
            "start_datetime": "Datetime string for scheduled start.",
            "start_time": "Epoch timestamp for scheduled start.",
            "strategy": "Rollout strategy (for example canary, serial, big_bang, rrm).",
            "versions": "List of firmware targets. Each item can specify firmware_type/model/version fields.",
        },
        "example": {
            "device_type": "ap",
            "all_sites": True,
            "strategy": "canary",
            "canary_phases": [1, 10, 50, 100],
            "max_failure_percentage": 20,
            "versions": [
                {
                    "firmware_type": "ap",
                    "version": "0.13.24558",
                }
            ],
            "start_time": 1735718400,
        },
    },
    UpgradeActionType.UPGRADE_ORG_MX_EDGES: {
        "schema": "mxedge_upgrade_multi",
        "required": ["mxedge_ids"],
        "attributes": [
            "allow_downgrades",
            "canary_phases",
            "channel",
            "distro",
            "max_failure_percentage",
            "mxedge_ids",
            "start_time",
            "strategy",
            "versions",
        ],
        "attribute_descriptions": {
            "allow_downgrades": "Allow target versions older than currently running versions.",
            "canary_phases": "Canary rollout percentages when strategy is canary.",
            "channel": "Release channel to use (alpha, beta, stable).",
            "distro": "Target distro/build train identifier.",
            "max_failure_percentage": "Stop rollout when failure percentage exceeds this threshold.",
            "mxedge_ids": "List of MX Edge IDs to upgrade.",
            "start_time": "Epoch timestamp for scheduled start.",
            "strategy": "Rollout strategy (canary, serial, big_bang).",
            "versions": "Per-component target versions (for example mxagent, tunterm).",
        },
        "example": {
            "mxedge_ids": ["00000000-0000-0000-0000-000000000001"],
            "channel": "stable",
            "strategy": "serial",
            "max_failure_percentage": 20,
            "versions": {
                "mxagent": "0.8.10",
                "tunterm": "0.8.10",
            },
            "start_time": 1735718400,
        },
    },
    UpgradeActionType.UPGRADE_ORG_SSRS: {
        "schema": "ssr_upgrade_multi",
        "required": ["device_ids"],
        "attributes": [
            "channel",
            "device_ids",
            "reboot_at",
            "start_time",
            "strategy",
            "version",
        ],
        "attribute_descriptions": {
            "channel": "Release channel to use (alpha, beta, stable).",
            "device_ids": "List of SSR device IDs to upgrade.",
            "reboot_at": "Epoch timestamp for scheduled reboot.",
            "start_time": "Epoch timestamp for scheduled start.",
            "strategy": "Rollout strategy (serial or big_bang).",
            "version": "Target SSR version string.",
        },
        "example": {
            "device_ids": ["00000000-0000-0000-0000-000000000001"],
            "version": "6.2.0",
            "channel": "stable",
            "strategy": "serial",
            "start_time": 1735718400,
        },
    },
    UpgradeActionType.UPGRADE_SITE_MX_EDGES: {
        "schema": "mxedge_upgrade_multi",
        "required": ["mxedge_ids"],
        "attributes": [
            "allow_downgrades",
            "canary_phases",
            "channel",
            "distro",
            "max_failure_percentage",
            "mxedge_ids",
            "start_time",
            "strategy",
            "versions",
        ],
        "attribute_descriptions": {
            "allow_downgrades": "Allow target versions older than currently running versions.",
            "canary_phases": "Canary rollout percentages when strategy is canary.",
            "channel": "Release channel to use (alpha, beta, stable).",
            "distro": "Target distro/build train identifier.",
            "max_failure_percentage": "Stop rollout when failure percentage exceeds this threshold.",
            "mxedge_ids": "List of MX Edge IDs to upgrade.",
            "start_time": "Epoch timestamp for scheduled start.",
            "strategy": "Rollout strategy (canary, serial, big_bang).",
            "versions": "Per-component target versions (for example mxagent, tunterm).",
        },
        "example": {
            "mxedge_ids": ["00000000-0000-0000-0000-000000000001"],
            "channel": "stable",
            "strategy": "serial",
            "versions": {
                "mxagent": "0.8.10",
                "tunterm": "0.8.10",
            },
            "start_time": 1735718400,
        },
    },
}


def _format_attribute_descriptions(contract: dict[str, Any]) -> str:
    descriptions: dict[str, str] = contract.get("attribute_descriptions", {})
    entries: list[str] = []
    for attribute in contract["attributes"]:
        details = descriptions.get(attribute, "No description available.")
        entries.append(f"{attribute}: {details}")
    return "; ".join(entries)


def _build_action_type_description() -> str:
    return "\n".join(
        [
            "Upgrade action to execute.",
            "Read actions: get_*, list_*.",
            "Write actions: cancel_*, upgrade_* (elicitation required).",
            "Payload format is documented in the `payload` parameter description.",
        ]
    )


def _build_payload_description() -> str:
    lines = [
        "Payload for upgrade_* actions only.",
        "Do not send `payload` for get_*, list_*, or cancel_* actions.",
        "Per-action payload contracts:",
    ]

    for action in sorted(PAYLOAD_REQUIRED_ACTIONS, key=lambda value: value.value):
        contract = PAYLOAD_CONTRACTS[action]
        required = ", ".join(contract["required"]
                             ) if contract["required"] else "none"
        attributes = ", ".join(contract["attributes"])
        attribute_descriptions = _format_attribute_descriptions(contract)
        example_text = json.dumps(contract["example"], ensure_ascii=True)
        lines.append(
            f"- {action.value}: schema `{contract['schema']}`, required keys: {required}, "
            f"allowed attributes: {attributes}, "
            f"attribute descriptions: {attribute_descriptions}, "
            f"example: `{example_text}`"
        )

    lines.append(
        "If unsure, use the matching list/get action first to discover valid versions/channels and targets, then submit payload."
    )
    return "\n".join(lines)


ACTION_TYPE_DESCRIPTION = _build_action_type_description()
PAYLOAD_DESCRIPTION = _build_payload_description()


def _ensure_parameter(value: Any, parameter_name: str, action: UpgradeActionType) -> None:
    if value is None:
        raise ToolError(
            {
                "status_code": 400,
                "message": f"`{parameter_name}` is required for `action_type={action.value}`.",
            }
        )


def _require_str(value: str | None, parameter_name: str, action: UpgradeActionType) -> str:
    _ensure_parameter(value, parameter_name, action)
    if value is None:
        raise AssertionError("unreachable")
    return value


def _require_payload(
    value: dict[str, Any] | list[Any] | None,
    action: UpgradeActionType,
) -> dict[str, Any] | list[Any]:
    _ensure_parameter(value, "payload", action)
    if value is None:
        raise AssertionError("unreachable")
    return value


def _require_payload_dict(
    value: dict[str, Any] | list[Any] | None,
    action: UpgradeActionType,
) -> dict[str, Any]:
    payload = _require_payload(value, action)
    if not isinstance(payload, dict):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"`payload` must be an object for `action_type={action.value}`.",
            }
        )
    return payload


async def _confirm_upgrade_write_action(ctx: Context, action_type: UpgradeActionType) -> dict[str, str] | None:
    try:
        elicitation_response = await config_elicitation_handler(
            message=(
                f"The LLM wants to run '{action_type.value}', which modifies device upgrade state. "
                "Do you accept to trigger the API call?"
            ),
            ctx=ctx,
        )
    except Exception as exc:
        raise ToolError(
            {
                "status_code": 400,
                "message": (
                    "AI App does not support elicitation. You cannot use it to "
                    "trigger upgrade write actions. Please use the Mist API "
                    "directly or use an AI App with elicitation support."
                ),
            }
        ) from exc

    if elicitation_response.action == "decline":
        return {"message": "Action declined by user."}
    if elicitation_response.action == "cancel":
        return {"message": "Action canceled by user."}
    return None


@mcp.tool(
    name="mist_upgrades",
    description="""Manage all Mist device upgrade operations in a single tool. Supports listing and retrieving upgrade jobs and available versions, and running upgrade/cancel actions for org/site devices, MX Edges, and SSR devices. All mutating actions are always gated by elicitation before calling the API.""",
    tags={"utilities_upgrade"},
    annotations={
        "title": "Upgrade operations",
        "readOnlyHint": False,
        "destructiveHint": True,
        "openWorldHint": True,
        "idempotentHint": False,
    },
)
async def upgrades(
    action_type: Annotated[
        UpgradeActionType,
        Field(
            description=ACTION_TYPE_DESCRIPTION
        ),
    ],
    org_id: Annotated[
        UUID | None,
        Field(
            description="""Organization ID. Required for org-scoped actions.""",
            default=None,
        ),
    ],
    site_id: Annotated[
        UUID | None,
        Field(
            description="""Site ID. Required for site-scoped actions.""",
            default=None,
        ),
    ],
    upgrade_id: Annotated[
        UUID | None,
        Field(
            description="""Upgrade job ID. Required for get/cancel actions on a specific upgrade.""",
            default=None,
        ),
    ],
    payload: Annotated[
        dict[str, Any] | list[Any] | None,
        Field(
            description=PAYLOAD_DESCRIPTION,
            default=None,
        ),
    ],
    firmware_type: Annotated[
        FirmwareType | None,
        Field(
            description="""Firmware type filter (ap, switch, gateway). Only for list_org_available_device_versions and list_site_available_device_versions.""",
            default=None,
        ),
    ],
    model: Annotated[
        str | None,
        Field(
            description="""Model filter for available device versions listing.""",
            default=None,
        ),
    ],
    channel: Annotated[
        Channel | None,
        Field(
            description="""SSR release channel for list_org_available_ssr_versions. Defaults to stable if omitted.""",
            default=None,
        ),
    ],
    mac: Annotated[
        str | None,
        Field(
            description="""MAC filter for list_org_available_ssr_versions.""",
            default=None,
        ),
    ],
    status: Annotated[
        str | None,
        Field(
            description="""Status filter for list_site_device_upgrades.""",
            default=None,
        ),
    ],
    ctx: Context,
) -> dict | list | str:
    """Manage all upgrade-related operations."""

    logger.debug("Tool upgrades called")
    logger.debug(
        "Input Parameters: action_type=%s org_id=%s site_id=%s upgrade_id=%s payload=%s firmware_type=%s model=%s channel=%s mac=%s status=%s",
        action_type,
        org_id,
        site_id,
        upgrade_id,
        payload,
        firmware_type,
        model,
        channel,
        mac,
        status,
    )

    if action_type in MUTATING_UPGRADE_ACTIONS:
        confirmation_result = await _confirm_upgrade_write_action(ctx, action_type)
        if confirmation_result is not None:
            return confirmation_result

    if payload is not None and action_type not in PAYLOAD_REQUIRED_ACTIONS:
        raise ToolError(
            {
                "status_code": 400,
                "message": (
                    f"`payload` is not supported for `action_type={action_type.value}`. "
                    "Use payload only with upgrade_* actions."
                ),
            }
        )

    apisession, response_format = await get_apisession()

    try:
        match action_type:
            case UpgradeActionType.CANCEL_ORG_DEVICE_UPGRADE:
                _ensure_parameter(org_id, "org_id", action_type)
                _ensure_parameter(upgrade_id, "upgrade_id", action_type)
                response = mistapi.api.v1.orgs.devices.cancelOrgDeviceUpgrade(
                    apisession,
                    org_id=str(org_id),
                    upgrade_id=str(upgrade_id),
                )
            case UpgradeActionType.CANCEL_ORG_MX_EDGE_UPGRADE:
                _ensure_parameter(org_id, "org_id", action_type)
                _ensure_parameter(upgrade_id, "upgrade_id", action_type)
                response = mistapi.api.v1.orgs.mxedges.cancelOrgMxEdgeUpgrade(
                    apisession,
                    org_id=str(org_id),
                    upgrade_id=str(upgrade_id),
                )
            case UpgradeActionType.CANCEL_ORG_SSR_UPGRADE:
                _ensure_parameter(org_id, "org_id", action_type)
                _ensure_parameter(upgrade_id, "upgrade_id", action_type)
                response = mistapi.api.v1.orgs.ssr.cancelOrgSsrUpgrade(
                    apisession,
                    org_id=str(org_id),
                    upgrade_id=str(upgrade_id),
                )
            case UpgradeActionType.CANCEL_SITE_MX_EDGE_UPGRADE:
                _ensure_parameter(site_id, "site_id", action_type)
                _ensure_parameter(upgrade_id, "upgrade_id", action_type)
                response = mistapi.api.v1.sites.mxedges.cancelSiteMxEdgeUpgrade(
                    apisession,
                    site_id=str(site_id),
                    upgrade_id=str(upgrade_id),
                )
            case UpgradeActionType.GET_ORG_DEVICE_UPGRADE:
                _ensure_parameter(org_id, "org_id", action_type)
                _ensure_parameter(upgrade_id, "upgrade_id", action_type)
                response = mistapi.api.v1.orgs.devices.getOrgDeviceUpgrade(
                    apisession,
                    org_id=str(org_id),
                    upgrade_id=str(upgrade_id),
                )
            case UpgradeActionType.GET_ORG_MX_EDGE_UPGRADE:
                _ensure_parameter(org_id, "org_id", action_type)
                _ensure_parameter(upgrade_id, "upgrade_id", action_type)
                response = mistapi.api.v1.orgs.mxedges.getOrgMxEdgeUpgrade(
                    apisession,
                    org_id=str(org_id),
                    upgrade_id=str(upgrade_id),
                )
            case UpgradeActionType.GET_ORG_SSR_UPGRADE:
                _ensure_parameter(org_id, "org_id", action_type)
                _ensure_parameter(upgrade_id, "upgrade_id", action_type)
                response = mistapi.api.v1.orgs.ssr.getOrgSsrUpgrade(
                    apisession,
                    org_id=str(org_id),
                    upgrade_id=str(upgrade_id),
                )
            case UpgradeActionType.GET_SITE_MX_EDGE_UPGRADE:
                _ensure_parameter(site_id, "site_id", action_type)
                _ensure_parameter(upgrade_id, "upgrade_id", action_type)
                response = mistapi.api.v1.sites.mxedges.getSiteMxEdgeUpgrade(
                    apisession,
                    site_id=str(site_id),
                    upgrade_id=str(upgrade_id),
                )
            case UpgradeActionType.LIST_ORG_AVAILABLE_DEVICE_VERSIONS:
                _ensure_parameter(org_id, "org_id", action_type)
                response = mistapi.api.v1.orgs.devices.listOrgAvailableDeviceVersions(
                    apisession,
                    org_id=str(org_id),
                    type=firmware_type.value if firmware_type else None,
                    model=model,
                )
            case UpgradeActionType.LIST_ORG_AVAILABLE_SSR_VERSIONS:
                _ensure_parameter(org_id, "org_id", action_type)
                response = mistapi.api.v1.orgs.ssr.listOrgAvailableSsrVersions(
                    apisession,
                    org_id=str(org_id),
                    channel=channel.value if channel else "stable",
                    mac=mac,
                )
            case UpgradeActionType.LIST_ORG_DEVICE_UPGRADES:
                _ensure_parameter(org_id, "org_id", action_type)
                response = mistapi.api.v1.orgs.devices.listOrgDeviceUpgrades(
                    apisession,
                    org_id=str(org_id),
                )
            case UpgradeActionType.LIST_ORG_MX_EDGE_UPGRADES:
                _ensure_parameter(org_id, "org_id", action_type)
                response = mistapi.api.v1.orgs.mxedges.listOrgMxEdgeUpgrades(
                    apisession,
                    org_id=str(org_id),
                )
            case UpgradeActionType.LIST_ORG_SSR_UPGRADES:
                _ensure_parameter(org_id, "org_id", action_type)
                response = mistapi.api.v1.orgs.ssr.listOrgSsrUpgrades(
                    apisession,
                    org_id=str(org_id),
                )
            case UpgradeActionType.LIST_SITE_AVAILABLE_DEVICE_VERSIONS:
                _ensure_parameter(site_id, "site_id", action_type)
                response = mistapi.api.v1.sites.devices.listSiteAvailableDeviceVersions(
                    apisession,
                    site_id=str(site_id),
                    type=firmware_type.value if firmware_type else None,
                    model=model,
                )
            case UpgradeActionType.LIST_SITE_MX_EDGE_UPGRADES:
                _ensure_parameter(site_id, "site_id", action_type)
                response = mistapi.api.v1.sites.mxedges.listSiteMxEdgeUpgrades(
                    apisession,
                    site_id=str(site_id),
                )
            case UpgradeActionType.UPGRADE_ORG_DEVICES:
                _ensure_parameter(org_id, "org_id", action_type)
                payload_value = _require_payload(payload, action_type)
                response = mistapi.api.v1.orgs.devices.upgradeOrgDevices(
                    apisession,
                    org_id=str(org_id),
                    body=payload_value,
                )
            case UpgradeActionType.UPGRADE_ORG_MX_EDGES:
                _ensure_parameter(org_id, "org_id", action_type)
                payload_value = _require_payload(payload, action_type)
                response = mistapi.api.v1.orgs.mxedges.upgradeOrgMxEdges(
                    apisession,
                    org_id=str(org_id),
                    body=payload_value,
                )
            case UpgradeActionType.UPGRADE_ORG_SSRS:
                _ensure_parameter(org_id, "org_id", action_type)
                payload_value = _require_payload(payload, action_type)
                response = mistapi.api.v1.orgs.ssr.upgradeOrgSsrs(
                    apisession,
                    org_id=str(org_id),
                    body=payload_value,
                )
            case UpgradeActionType.UPGRADE_SITE_MX_EDGES:
                _ensure_parameter(site_id, "site_id", action_type)
                payload_value = _require_payload(payload, action_type)
                response = mistapi.api.v1.sites.mxedges.upgradeSiteMxEdges(
                    apisession,
                    site_id=str(site_id),
                    body=payload_value,
                )
            case _:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": f"Invalid action_type: {action_type.value}",
                    }
                )

        await process_response(response)
        return format_response(response, response_format)
    except ToolError:
        raise
    except Exception as exc:
        await handle_network_error(exc)
        raise AssertionError("unreachable") from exc
'''
