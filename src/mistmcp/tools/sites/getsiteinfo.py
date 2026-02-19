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
    name="getSiteInfo",
    description="""Provides information about the site, including its name, address,timezone, and associated templates. This endpoint is useful for retrievingthe current configuration and details of a specific site.""",
    tags={"Sites"},
    annotations={
        "title": "getSiteInfo",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getSiteInfo(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    ctx: Context | None = None,
) -> dict | list | str:
    """Provides information about the site, including its name, address,timezone, and associated templates. This endpoint is useful for retrievingthe current configuration and details of a specific site."""

    logger.debug("Tool getSiteInfo called")

    apisession, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.sites.sites.getSiteInfo(
        apisession,
        site_id=str(site_id),
    )
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
