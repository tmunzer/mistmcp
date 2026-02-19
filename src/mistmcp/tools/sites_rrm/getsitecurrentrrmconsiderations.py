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
from enum import Enum


class Band(Enum):
    B24 = "24"
    B5 = "5"
    B6 = "6"


@mcp.tool(
    name="getSiteCurrentRrmConsiderations",
    description="""Get Current RRM Considerations for an AP on a Specific Band""",
    tags={"Sites RRM"},
    annotations={
        "title": "getSiteCurrentRrmConsiderations",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getSiteCurrentRrmConsiderations(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    device_id: Annotated[UUID, Field(description="""ID of the Mist Device""")],
    band: Annotated[Band, Field(description="""802.11 Band""")],
    ctx: Context | None = None,
) -> dict | list | str:
    """Get Current RRM Considerations for an AP on a Specific Band"""

    logger.debug("Tool getSiteCurrentRrmConsiderations called")

    apisession, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.sites.rrm.getSiteCurrentRrmConsiderations(
        apisession,
        site_id=str(site_id),
        device_id=str(device_id),
        band=band.value,
    )
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
