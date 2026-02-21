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
    AP = "ap"
    GATEWAY = "gateway"
    SWITCH = "switch"


@mcp.tool(
    name="searchSiteDeviceConfigHistory",
    description="""Search for entries in device config history""",
    tags={"devices"},
    annotations={
        "title": "searchSiteDeviceConfigHistory",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchSiteDeviceConfigHistory(
    site_id: Annotated[UUID, Field(description="""Site ID""")],
    type: Optional[Type | None] = Type.AP,
    mac: Annotated[
        Optional[str | None], Field(description="""Device MAC Address""")
    ] = None,
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
    sort: Annotated[Optional[str | None], Field(description="""Sort field""")] = None,
    search_after: Annotated[
        Optional[str | None],
        Field(
            description="""Pagination cursor from '_next' URL of previous response"""
        ),
    ] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """Search for entries in device config history"""

    logger.debug("Tool searchSiteDeviceConfigHistory called")

    apisession, response_format = get_apisession()

    response = mistapi.api.v1.sites.devices.searchSiteDeviceConfigHistory(
        apisession,
        site_id=str(site_id),
        type=type.value if type else Type.AP.value,
        mac=mac if mac else None,
        limit=limit,
        start=start if start else None,
        end=end if end else None,
        duration=duration if duration else None,
        sort=sort if sort else None,
        search_after=search_after if search_after else None,
    )
    await process_response(response)

    return format_response(response, response_format)
