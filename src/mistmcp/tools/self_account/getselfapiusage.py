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
    name = "getSelfApiUsage",
    description = """Get the status of the API usage for the current user or API Token""",
    tags = {"Self Account"},
    annotations = {
        "title": "getSelfApiUsage",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getSelfApiUsage(
    ) -> dict|list:
    """Get the status of the API usage for the current user or API Token"""

    apisession = get_apisession()
    data = {}
    
    
    response = mistapi.api.v1.self.usage.getSelfApiUsage(
            apisession,
    )
    await process_response(response)
    
    data = response.data


    return data
