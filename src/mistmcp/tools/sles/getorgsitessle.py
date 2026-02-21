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


class Sle(Enum):
    WAN = "wan"
    WIFI = "wifi"
    WIRED = "wired"
    NONE = None


@mcp.tool(
    name="getOrgSitesSle",
    description="""Get Org Sites SLE""",
    tags={"sles"},
    annotations={
        "title": "getOrgSitesSle",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getOrgSitesSle(
    org_id: Annotated[UUID, Field(description="""Organization ID""")],
    sle: Optional[Sle | None] = Sle.NONE,
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
    limit: Annotated[
        int, Field(description="""Max number of results per page""", default=100)
    ] = 100,
    page: Annotated[
        int, Field(description="""Page number for pagination""", ge=1, default=1)
    ] = 1,
    ctx: Context | None = None,
) -> dict | list | str:
    """Get Org Sites SLE"""

    logger.debug("Tool getOrgSitesSle called")

    apisession, response_format = get_apisession()

    response = mistapi.api.v1.orgs.insights.getOrgSitesSle(
        apisession,
        org_id=str(org_id),
        sle=sle.value if sle else None,
        start=start if start else None,
        end=end if end else None,
        duration=duration if duration else None,
        interval=interval if interval else None,
        limit=limit,
        page=page,
    )
    await process_response(response)

    return format_response(response, response_format)
