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
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    band: Annotated[
        Optional[Band | None], Field(description="""802.11 Band""")
    ] = Band.NONE,
    start: Annotated[
        Optional[str | None],
        Field(
            description="""Start time (epoch timestamp in seconds, or relative string like '-1d', '-1w')"""
        ),
    ] = None,
    end: Annotated[
        Optional[str | None],
        Field(
            description="""End time (epoch timestamp in seconds, or relative string like '-1d', '-2h', 'now')"""
        ),
    ] = None,
    duration: Annotated[
        Optional[str | None], Field(description="""Duration like 7d, 2w""")
    ] = None,
    limit: Optional[int | None] = None,
    page: Annotated[Optional[int | None], Field(ge=1)] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """List Site RRM Events"""

    logger.debug("Tool listSiteRrmEvents called")

    apisession, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.sites.rrm.listSiteRrmEvents(
        apisession,
        site_id=str(site_id),
        band=band.value if band else None,
        start=start if start else None,
        end=end if end else None,
        duration=duration if duration else None,
        limit=limit if limit else None,
        page=page if page else None,
    )
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
