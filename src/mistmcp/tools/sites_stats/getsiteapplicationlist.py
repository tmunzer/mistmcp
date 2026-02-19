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

from pydantic import Field
from typing import Annotated
from uuid import UUID


@mcp.tool(
    name="getSiteApplicationList",
    description="""Get Application List""",
    tags={"sites_stats"},
    annotations={
        "title": "getSiteApplicationList",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getSiteApplicationList(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    ctx: Context | None = None,
) -> dict | list | str:
    """Get Application List"""

    logger.debug("Tool getSiteApplicationList called")

    apisession, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.sites.wxtags.getSiteApplicationList(
        apisession,
        site_id=str(site_id),
    )
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
