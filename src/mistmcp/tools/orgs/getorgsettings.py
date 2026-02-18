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
from typing import Annotated
from uuid import UUID



mcp = get_mcp()

if not mcp:
    raise RuntimeError(
        "MCP instance not found. Make sure to initialize the MCP server before defining tools."
    )





@mcp.tool(
    enabled=True,
    name = "getOrgSettings",
    description = """Get Org Settings""",
    tags = {"orgs"},
    annotations = {
        "title": "getOrgSettings",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getOrgSettings(
    
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
) -> dict|list:
    """Get Org Settings"""

    apisession = get_apisession()
    data = {}
    
    
    response = mistapi.api.v1.orgs.setting.getOrgSettings(
            apisession,
            org_id=str(org_id),
    )
    await process_response(response)
    
    data = response.data


    return data
