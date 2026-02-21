"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import json
import mistapi
from fastmcp import Context
from fastmcp.exceptions import ToolError
from mistmcp.request_processor import get_apisession
from mistmcp.response_processor import process_response
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


@mcp.tool(
    name="listUpgrades",
    description="""List all available upgrades for the organization""",
    tags={"utilities_upgrade"},
    annotations={
        "title": "listUpgrades",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def listUpgrades(
    org_id: Annotated[UUID, Field(description="""Organization ID""")],
    device_type: Annotated[
        Device_type, Field(description="""Type of device to filter upgrades by""")
    ],
    upgrade_id: Annotated[
        Optional[UUID | None],
        Field(description="""ID of the specific upgrade to retrieve"""),
    ] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """List all available upgrades for the organization"""

    logger.debug("Tool listUpgrades called")

    apisession, response_format = get_apisession()

    object_type = device_type
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

        case _:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Device_type]}",
                }
            )

    return format_response(response, response_format)
