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


class For_site(Enum):
    ANY = "any"
    TRUE = "true"
    FALSE = "false"
    NONE = None


@mcp.tool(
    name="listOrgMxEdgesStats",
    description="""Get List of Org MxEdge Stats""",
    tags={"orgs_stats"},
    annotations={
        "title": "listOrgMxEdgesStats",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def listOrgMxEdgesStats(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    for_site: Annotated[
        Optional[For_site | None],
        Field(description="""Filter for site level mist edges"""),
    ] = For_site.NONE,
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
    mxedge_id: Annotated[
        Optional[str | None],
        Field(
            description="""ID of the Mist Edge to filter stats by. Optional, if not provided all MX Edges will be listed."""
        ),
    ] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """Get List of Org MxEdge Stats"""

    apisession, response_format = get_apisession()
    data = {}

    if mxedge_id:
        response = mistapi.api.v1.sites.stats.org_id(
            apisession, org_id=str(org_id), mxedge_id=mxedge_id
        )
        await process_response(response)
    else:
        response = mistapi.api.v1.orgs.stats.listOrgMxEdgesStats(
            apisession,
            org_id=str(org_id),
            for_site=for_site.value if for_site else None,
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
