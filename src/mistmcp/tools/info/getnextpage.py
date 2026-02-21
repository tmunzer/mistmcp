"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

from typing import Annotated

from pydantic import Field

from fastmcp import Context
from mistmcp.request_processor import get_apisession
from mistmcp.response_processor import process_response
from mistmcp.response_formatter import format_response
from mistmcp.server import mcp
from mistmcp.logger import logger


@mcp.tool(
    name="getNextPage",
    description="Retrieve the next page of results using the '_next' URL returned by a previous tool call.",
    tags={"info"},
    annotations={
        "title": "getNextPage",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getNextPage(
    url: Annotated[
        str,
        Field(description="The '_next' URL from a previous response"),
    ],
    ctx: Context | None = None,
) -> dict | list | str:
    """Retrieve the next page of results using the '_next' URL returned by a previous tool call."""

    logger.debug("Tool getNextPage called")

    apisession, response_format = get_apisession()
    response = apisession.mist_get(url)
    await process_response(response)
    return format_response(response, response_format)
