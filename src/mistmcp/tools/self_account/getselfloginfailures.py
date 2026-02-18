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




mcp = get_mcp()

if not mcp:
    raise RuntimeError(
        "MCP instance not found. Make sure to initialize the MCP server before defining tools."
    )





@mcp.tool(
    enabled=True,
    name = "getSelfLoginFailures",
    description = """Get a list of failed login attempts across all Orgs for the current admin""",
    tags = {"Self Account"},
    annotations = {
        "title": "getSelfLoginFailures",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getSelfLoginFailures(
    ) -> dict|list:
    """Get a list of failed login attempts across all Orgs for the current admin"""

    apisession = get_apisession()
    data = {}
    
    
    response = mistapi.api.v1.self.login_failures.getSelfLoginFailures(
            apisession,
    )
    await process_response(response)
    
    data = response.data


    return data
