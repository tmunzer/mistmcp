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


@mcp.tool(
    name="searchOrgMistEdgeEvents",
    description="""Search Org Mist Edge Events""",
    tags={"devices"},
    annotations={
        "title": "searchOrgMistEdgeEvents",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchOrgMistEdgeEvents(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    mxedge_id: Annotated[
        Optional[str | None], Field(description="""Mist edge id""")
    ] = None,
    mxcluster_id: Annotated[
        Optional[str | None], Field(description="""Mist edge cluster id""")
    ] = None,
    type: Annotated[
        Optional[str | None],
        Field(
            description="""See [List Device Events Definitions](/#operations/listDeviceEventsDefinitions)"""
        ),
    ] = None,
    service: Annotated[
        Optional[str | None],
        Field(description="""Service running on mist edge(mxagent, tunterm etc)"""),
    ] = None,
    component: Annotated[
        Optional[str | None], Field(description="""Component like PS1, PS2""")
    ] = None,
    limit: Optional[int | None] = None,
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
    sort: Annotated[
        Optional[str | None],
        Field(
            description="""On which field the list should be sorted, -prefix represents DESC order"""
        ),
    ] = None,
    search_after: Annotated[
        Optional[str | None],
        Field(
            description="""Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed."""
        ),
    ] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """Search Org Mist Edge Events"""

    apisession, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.orgs.mxedges.searchOrgMistEdgeEvents(
        apisession,
        org_id=str(org_id),
        mxedge_id=mxedge_id if mxedge_id else None,
        mxcluster_id=mxcluster_id if mxcluster_id else None,
        type=type if type else None,
        service=service if service else None,
        component=component if component else None,
        limit=limit if limit else None,
        start=start if start else None,
        end=end if end else None,
        duration=duration if duration else None,
        sort=sort if sort else None,
        search_after=search_after if search_after else None,
    )
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
