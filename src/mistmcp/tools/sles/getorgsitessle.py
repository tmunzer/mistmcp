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
from mistmcp.server import get_mcp

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


mcp = get_mcp()

if not mcp:
    raise RuntimeError(
        "MCP instance not found. Make sure to initialize the MCP server before defining tools."
    )


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
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    sle: Optional[Sle | None] = Sle.NONE,
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
    interval: Annotated[
        Optional[str | None],
        Field(
            description="""Aggregation works by giving a time range plus interval (e.g. 1d, 1h, 10m) where aggregation function would be applied to."""
        ),
    ] = None,
    limit: Optional[int | None] = None,
    page: Annotated[Optional[int | None], Field(ge=1)] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """Get Org Sites SLE"""

    apisession, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.orgs.insights.getOrgSitesSle(
        apisession,
        org_id=str(org_id),
        sle=sle.value if sle else None,
        start=start if start else None,
        end=end if end else None,
        duration=duration if duration else None,
        interval=interval if interval else None,
        limit=limit if limit else None,
        page=page if page else None,
    )
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
