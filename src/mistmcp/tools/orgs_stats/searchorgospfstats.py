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


@mcp.tool(
    name="searchOrgOspfStats",
    description="""Search OSPF Neighbor Stats""",
    tags={"orgs_stats"},
    annotations={
        "title": "searchOrgOspfStats",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchOrgOspfStats(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    site_id: Annotated[
        Optional[str | None], Field(description="""ID of the Mist Site""")
    ] = None,
    mac: Optional[str | None] = None,
    vrf_name: Optional[str | None] = None,
    peer_ip: Optional[str | None] = None,
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
    limit: Optional[int | None] = None,
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
    """Search OSPF Neighbor Stats"""

    logger.debug("Tool searchOrgOspfStats called")

    apisession, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.orgs.stats.searchOrgOspfStats(
        apisession,
        org_id=str(org_id),
        site_id=site_id if site_id else None,
        mac=mac if mac else None,
        vrf_name=vrf_name if vrf_name else None,
        peer_ip=peer_ip if peer_ip else None,
        start=start if start else None,
        end=end if end else None,
        limit=limit if limit else None,
        sort=sort if sort else None,
        search_after=search_after if search_after else None,
    )
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
