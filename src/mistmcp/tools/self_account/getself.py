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
from mistmcp.logger import logger


@mcp.tool(
    name="getSelf",
    description="""Get ‘whoami’ and privileges (which org and which sites I have access to)""",
    tags={"Self Account"},
    annotations={
        "title": "getSelf",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getSelf(
    ctx: Context | None = None,
) -> dict | list | str:
    """Get ‘whoami’ and privileges (which org and which sites I have access to)"""

    logger.debug("Tool getSelf called")

    apisession, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.self.self.getSelf(
        apisession,
    )
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
