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



class Type(Enum):
    AP = "ap"
    GATEWAY = "gateway"
    SWITCH = "switch"



@mcp.tool(
    enabled=True,
    name = "listOrgAvailableDeviceVersions",
    description = """Get List of Available Device Versions""",
    tags = {"Utilities Upgrade"},
    annotations = {
        "title": "listOrgAvailableDeviceVersions",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def listOrgAvailableDeviceVersions(
    
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    type: Optional[Type | None] = Type.AP,
    model: Annotated[Optional[str | None], Field(description="""Fetch version for device model, use/combine with `type` as needed (for switch and gateway devices)""")] = None,
) -> dict|list:
    """Get List of Available Device Versions"""

    apisession = get_apisession()
    data = {}
    
    
    response = mistapi.api.v1.orgs.devices.listOrgAvailableDeviceVersions(
            apisession,
            org_id=str(org_id),
            type=type.value if type else Type.AP.value,
            model=model if model else None,
    )
    await process_response(response)
    
    data = response.data


    return data
