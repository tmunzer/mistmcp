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
from mistmcp.response_formatter import format_response
from mistmcp.server import mcp
from mistmcp.logger import logger

from pydantic import Field
from typing import Annotated
from uuid import UUID


@mcp.tool(
    name="getSiteDeviceSyntheticTest",
    description="""Get Device Synthetic Test""",
    tags={"marvis"},
    annotations={
        "title": "getSiteDeviceSyntheticTest",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getSiteDeviceSyntheticTest(
    site_id: Annotated[UUID, Field(description="""Site ID""")],
    device_id: Annotated[UUID, Field(description="""ID of the Mist Device""")],
    ctx: Context | None = None,
) -> dict | list | str:
    """Get Device Synthetic Test"""

    logger.debug("Tool getSiteDeviceSyntheticTest called")

    apisession, response_format = get_apisession()

    response = mistapi.api.v1.sites.devices.getSiteDeviceSyntheticTest(
        apisession,
        site_id=str(site_id),
        device_id=str(device_id),
    )
    await process_response(response)

    return format_response(response, response_format)
