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
from mistmcp.server import mcp


@mcp.tool(
    name="getSelfLoginFailures",
    description="""Get a list of failed login attempts across all Orgs for the current admin""",
    tags={"Self Account"},
    annotations={
        "title": "getSelfLoginFailures",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getSelfLoginFailures(
    ctx: Context | None = None,
) -> dict | list | str:
    """Get a list of failed login attempts across all Orgs for the current admin"""

    apisession, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.self.login_failures.getSelfLoginFailures(
        apisession,
    )
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
