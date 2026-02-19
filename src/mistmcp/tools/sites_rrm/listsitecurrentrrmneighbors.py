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

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


class Band(Enum):
    B24 = "24"
    B5 = "5"
    B6 = "6"


@mcp.tool(
    name="listSiteCurrentRrmNeighbors",
    description="""List Current RRM observed neighbors""",
    tags={"Sites RRM"},
    annotations={
        "title": "listSiteCurrentRrmNeighbors",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def listSiteCurrentRrmNeighbors(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    band: Annotated[Band, Field(description="""802.11 Band""")],
    limit: Optional[int | None] = None,
    page: Annotated[Optional[int | None], Field(ge=1)] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """List Current RRM observed neighbors"""

    apisession, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.sites.rrm.listSiteCurrentRrmNeighbors(
        apisession,
        site_id=str(site_id),
        band=band.value,
        limit=limit if limit else None,
        page=page if page else None,
    )
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
