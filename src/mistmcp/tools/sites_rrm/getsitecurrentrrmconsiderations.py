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
from enum import Enum


mcp = get_mcp()

if not mcp:
    raise RuntimeError(
        "MCP instance not found. Make sure to initialize the MCP server before defining tools."
    )


class Band(Enum):
    B24 = "24"
    B5 = "5"
    B6 = "6"


@mcp.tool(
    enabled=True,
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
) -> dict | list:
    """Get Current RRM Considerations for an AP on a Specific Band"""

    apisession = get_apisession()
    data = {}

    response = mistapi.api.v1.sites.rrm.getSiteCurrentRrmConsiderations(
        apisession,
        site_id=str(site_id),
        device_id=str(device_id),
        band=band.value,
    )
    await process_response(response)

    data = response.data

    return data
