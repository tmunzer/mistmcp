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
from fastmcp.exceptions import ToolError
from mistmcp.request_processor import get_apisession
from mistmcp.response_processor import process_response
from mistmcp.server import get_mcp

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum



mcp = get_mcp()

if not mcp:
    raise RuntimeError(
        "MCP instance not found. Make sure to initialize the MCP server before defining tools."
    )



class Device_type(Enum):
    AP = "ap"
    SWITCH = "switch"
    SRX = "srx"
    MXEDGE = "mxedge"
    SSR = "ssr"



@mcp.tool(
    enabled=True,
    name = "listUpgrades",
    description = """List all available upgrades for the organization.""",
    tags = {"utilities_upgrade"},
    annotations = {
        "title": "listUpgrades",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def listUpgrades(
    
    org_id: Annotated[UUID, Field(description="""ID of the organization to list upgrades for.""")],
    device_type: Annotated[Device_type, Field(description="""Type of device to filter upgrades by. Optional, if not provided all upgrades will be listed.""")],
    upgrade_id: Annotated[Optional[UUID | None], Field(description="""ID of the specific upgrade to retrieve. Optional, if not provided all upgrades will be listed.""")] = None,
) -> dict|list:
    """List all available upgrades for the organization."""

    apisession = get_apisession()
    data = {}
    
    
    object_type = device_type
    match object_type.value:
        case 'ap':
            if upgrade_id:
                response = mistapi.api.v1.orgs.devices.getOrgDeviceUpgrade(apisession, org_id=str(org_id), upgrade_id=str(upgrade_id))
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.devices.listOrgDeviceUpgrades(apisession, org_id=str(org_id), limit=1000)
                await process_response(response)
                data = response.data
        case 'switch':
            if upgrade_id:
                response = mistapi.api.v1.orgs.devices.getOrgDeviceUpgrade(apisession, org_id=str(org_id), upgrade_id=str(upgrade_id))
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.devices.listOrgDeviceUpgrades(apisession, org_id=str(org_id), limit=1000)
                await process_response(response)
                data = response.data
        case 'srx':
            if upgrade_id:
                response = mistapi.api.v1.orgs.devices.getOrgDeviceUpgrade(apisession, org_id=str(org_id), upgrade_id=str(upgrade_id))
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.devices.listOrgDeviceUpgrades(apisession, org_id=str(org_id), limit=1000)
                await process_response(response)
                data = response.data
        case 'mxedge':
            if upgrade_id:
                response = mistapi.api.v1.orgs.mxedges.getOrgMxEdgeUpgrade(apisession, org_id=str(org_id), upgrade_id=str(upgrade_id))
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.mxedges.listOrgMxEdgeUpgrades(apisession, org_id=str(org_id), limit=1000)
                await process_response(response)
                data = response.data
        case 'ssr':
            if upgrade_id:
                response = mistapi.api.v1.orgs.ssr.getOrgSsrUpgrade(apisession, org_id=str(org_id), upgrade_id=str(upgrade_id))
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.ssr.listOrgSsrUpgrades(apisession, org_id=str(org_id), limit=1000)
                await process_response(response)
                data = response.data

        case _:
            raise ToolError({
                "status_code": 400,
                "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Device_type]}",
            })
            

    return data
