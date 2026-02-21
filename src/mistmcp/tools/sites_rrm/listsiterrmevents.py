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
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


class Band(Enum):
    B24 = "24"
    B5 = "5"
    B6 = "6"
    NONE = None


@mcp.tool(
    name="listSiteRrmEvents",
    description="""List Site RRM Events""",
    tags={"Sites RRM"},
    annotations={
        "title": "listSiteRrmEvents",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def listSiteRrmEvents(
    site_id: Annotated[UUID, Field(description="""Site ID""")],
    band: Annotated[
        Optional[Band | None], Field(description="""802.11 Band""")
    ] = Band.NONE,
    start: Annotated[
        Optional[str | None],
        Field(description="""Start of time range (epoch seconds)"""),
    ] = None,
    end: Annotated[
        Optional[str | None], Field(description="""End of time range (epoch seconds)""")
    ] = None,
    duration: Annotated[
        Optional[str | None],
        Field(description="""Time range duration (e.g. 1d, 1h, 10m)"""),
    ] = None,
    limit: Annotated[
        int, Field(description="""Max number of results per page""", default=100)
    ] = 100,
    page: Annotated[
        int, Field(description="""Page number for pagination""", ge=1, default=1)
    ] = 1,
    ctx: Context | None = None,
) -> dict | list | str:
    """List Site RRM Events"""

    logger.debug("Tool listSiteRrmEvents called")

    apisession, response_format = get_apisession()

    response = mistapi.api.v1.sites.rrm.listSiteRrmEvents(
        apisession,
        site_id=str(site_id),
        band=band.value if band else None,
        start=start if start else None,
        end=end if end else None,
        duration=duration if duration else None,
        limit=limit,
        page=page,
    )
    await process_response(response)

    return format_response(response, response_format)
