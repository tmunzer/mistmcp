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
from typing import Annotated, Optional
from uuid import UUID


mcp = get_mcp()

if not mcp:
    raise RuntimeError(
        "MCP instance not found. Make sure to initialize the MCP server before defining tools."
    )


@mcp.tool(
    enabled=True,
    name="getOrgStats",
    description="""Get Org Stats""",
    tags={"Orgs Stats"},
    annotations={
        "title": "getOrgStats",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getOrgStats(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
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
) -> dict | list:
    """Get Org Stats"""

    apisession = get_apisession()
    data = {}

    response = mistapi.api.v1.orgs.stats.getOrgStats(
        apisession,
        org_id=str(org_id),
        start=start if start else None,
        end=end if end else None,
        duration=duration if duration else None,
        limit=limit if limit else None,
        page=page if page else None,
    )
    await process_response(response)

    data = response.data

    return data
