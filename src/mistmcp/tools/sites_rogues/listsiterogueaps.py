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


class Type(Enum):
    HONEYPOT = "honeypot"
    LAN = "lan"
    OTHERS = "others"
    SPOOF = "spoof"
    NONE = None


@mcp.tool(
    name="listSiteRogueAPs",
    description="""Get List of Site Rogue/Neighbor APs""",
    tags={"Sites Rogues"},
    annotations={
        "title": "listSiteRogueAPs",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def listSiteRogueAPs(
    site_id: Annotated[UUID, Field(description="""Site ID""")],
    type: Optional[Type | None] = Type.NONE,
    limit: Annotated[
        int, Field(description="""Max number of results per page""", default=100)
    ] = 100,
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
    interval: Annotated[
        Optional[str | None],
        Field(description="""Aggregation interval (e.g. 1h, 1d)"""),
    ] = None,
    rogue_bssid: Annotated[
        Optional[str | None],
        Field(description="""BSSID of the rogue AP to filter stats by"""),
    ] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """Get List of Site Rogue/Neighbor APs"""

    logger.debug("Tool listSiteRogueAPs called")

    apisession, response_format = get_apisession()

    if rogue_bssid:
        response = mistapi.api.v1.sites.rogues.getSiteRogueAP(
            apisession, site_id=str(site_id), rogue_bssid=rogue_bssid
        )
        await process_response(response)
    else:
        response = mistapi.api.v1.sites.insights.listSiteRogueAPs(
            apisession,
            site_id=str(site_id),
            type=type.value if type else None,
            limit=limit,
            start=start if start else None,
            end=end if end else None,
            duration=duration if duration else None,
            interval=interval if interval else None,
        )
        await process_response(response)

    return format_response(response, response_format)
