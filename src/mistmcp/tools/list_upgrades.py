"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import mistapi
from fastmcp import Context
from fastmcp.exceptions import ToolError
from mistmcp.request_processor import get_apisession
from mistmcp.response_processor import process_response, handle_network_error
from mistmcp.response_formatter import format_response
from mistmcp.server import mcp
from mistmcp.logger import logger

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


class Device_type(Enum):
    AP = "ap"
    SWITCH = "switch"
    SRX = "srx"
    MXEDGE = "mxedge"
    SSR = "ssr"
    AVAILABLE_DEVICE_VERSIONS = "available_device_versions"
    AVAILABLE_SSR_VERSIONS = "available_ssr_versions"


class Firmware_type(Enum):
    AP = "ap"
    SWITCH = "switch"
    GATEWAY = "gateway"


class Channel(Enum):
    ALPHA = "alpha"
    BETA = "beta"
    STABLE = "stable"


@mcp.tool(
    name="mist_list_upgrades",
    description="""Retrieve upgrade-related information for the organization. Use device types (ap, switch, srx, mxedge, ssr) to list or retrieve upgrade jobs. Use available_device_versions to list available firmware versions for AP/switch/gateway devices. Use available_ssr_versions to list available SSR firmware versions.""",
    tags={"utilities_upgrade"},
    annotations={
        "title": "List upgrades",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def list_upgrades(
    org_id: Annotated[UUID, Field(description="""Organization ID""")],
    device_type: Annotated[
        Device_type,
        Field(
            description="""Type of query: use ap/switch/srx/mxedge/ssr to list upgrade jobs for that device type; use available_device_versions to list available firmware versions for AP/switch/gateway devices; use available_ssr_versions to list available SSR firmware versions"""
        ),
    ],
    upgrade_id: Annotated[
        Optional[UUID],
        Field(
            description="""ID of a specific upgrade job to retrieve. Only applicable when device_type is ap, switch, srx, mxedge, or ssr"""
        ),
    ],
    firmware_type: Annotated[
        Optional[Firmware_type],
        Field(
            description="""Device model type to filter available firmware versions by. Only applicable when device_type is available_device_versions"""
        ),
    ],
    model: Annotated[
        Optional[str],
        Field(
            description="""Device model to filter available firmware versions by. Only applicable when device_type is available_device_versions"""
        ),
    ],
    channel: Annotated[
        Optional[Channel],
        Field(
            description="""SSR firmware release channel to filter by. Only applicable when device_type is available_ssr_versions. Defaults to stable"""
        ),
    ],
    mac: Annotated[
        Optional[str],
        Field(
            description="""MAC address (or comma-separated list) of SSR device(s) to retrieve available versions for. Only applicable when device_type is available_ssr_versions"""
        ),
    ],
) -> dict | list | str:
    """Retrieve upgrade-related information for the organization. Use device types (ap, switch, srx, mxedge, ssr) to list or retrieve upgrade jobs. Use available_device_versions to list available firmware versions for AP/switch/gateway devices. Use available_ssr_versions to list available SSR firmware versions."""

    logger.debug("Tool list_upgrades called")

    apisession, response_format = await get_apisession()

    try:
        object_type = device_type

        if upgrade_id and device_type.value not in [
            "ap",
            "switch",
            "srx",
            "mxedge",
            "ssr",
        ]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`upgrade_id` parameter can only be used when `device_type` is in "ap", "switch", "srx", "mxedge", "ssr".',
                }
            )

        if firmware_type and device_type.value not in ["available_device_versions"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`firmware_type` parameter can only be used when `device_type` is "available_device_versions".',
                }
            )

        if model and device_type.value not in ["available_device_versions"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`model` parameter can only be used when `device_type` is "available_device_versions".',
                }
            )

        if channel and device_type.value not in ["available_ssr_versions"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`channel` parameter can only be used when `device_type` is "available_ssr_versions".',
                }
            )

        if mac and device_type.value not in ["available_ssr_versions"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`mac` parameter can only be used when `device_type` is "available_ssr_versions".',
                }
            )

        match object_type.value:
            case "ap":
                if upgrade_id:
                    response = mistapi.api.v1.orgs.devices.getOrgDeviceUpgrade(
                        apisession, org_id=str(org_id), upgrade_id=str(upgrade_id)
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.devices.listOrgDeviceUpgrades(
                        apisession, org_id=str(org_id)
                    )
                    await process_response(response)
            case "switch":
                if upgrade_id:
                    response = mistapi.api.v1.orgs.devices.getOrgDeviceUpgrade(
                        apisession, org_id=str(org_id), upgrade_id=str(upgrade_id)
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.devices.listOrgDeviceUpgrades(
                        apisession, org_id=str(org_id)
                    )
                    await process_response(response)
            case "srx":
                if upgrade_id:
                    response = mistapi.api.v1.orgs.devices.getOrgDeviceUpgrade(
                        apisession, org_id=str(org_id), upgrade_id=str(upgrade_id)
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.devices.listOrgDeviceUpgrades(
                        apisession, org_id=str(org_id)
                    )
                    await process_response(response)
            case "mxedge":
                if upgrade_id:
                    response = mistapi.api.v1.orgs.mxedges.getOrgMxEdgeUpgrade(
                        apisession, org_id=str(org_id), upgrade_id=str(upgrade_id)
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.mxedges.listOrgMxEdgeUpgrades(
                        apisession, org_id=str(org_id)
                    )
                    await process_response(response)
            case "ssr":
                if upgrade_id:
                    response = mistapi.api.v1.orgs.ssr.getOrgSsrUpgrade(
                        apisession, org_id=str(org_id), upgrade_id=str(upgrade_id)
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.ssr.listOrgSsrUpgrades(
                        apisession, org_id=str(org_id)
                    )
                    await process_response(response)
            case "available_device_versions":
                response = mistapi.api.v1.orgs.devices.listOrgAvailableDeviceVersions(
                    apisession,
                    org_id=str(org_id),
                    type=firmware_type.value if firmware_type else None,
                    model=model if model else None,
                )
                await process_response(response)
            case "available_ssr_versions":
                response = mistapi.api.v1.orgs.ssr.listOrgAvailableSsrVersions(
                    apisession,
                    org_id=str(org_id),
                    channel=channel.value if channel else "stable",
                    mac=mac if mac else None,
                )
                await process_response(response)

            case _:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Device_type]}",
                    }
                )

    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
