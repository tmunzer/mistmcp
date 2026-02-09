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
    name="searchOrgWanClients",
    description="""Search Org WAN Clients""",
    tags={"clients"},
    annotations={
        "title": "searchOrgWanClients",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchOrgWanClients(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    mac: Annotated[
        Optional[str | None], Field(description="""Partial / full MAC address""")
    ] = None,
    hostname: Annotated[
        Optional[str | None], Field(description="""Partial / full hostname""")
    ] = None,
    ip: Annotated[Optional[str | None], Field(description="""Client IP""")] = None,
    network: Annotated[Optional[str | None], Field(description="""Network""")] = None,
    ip_src: Annotated[Optional[str | None], Field(description="""IP source""")] = None,
    mfg: Annotated[Optional[str | None], Field(description="""Manufacture""")] = None,
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
) -> dict | list:
    """Search Org WAN Clients"""

    apisession = get_apisession()
    data = {}

    response = mistapi.api.v1.orgs.wan_clients.searchOrgWanClients(
        apisession,
        org_id=str(org_id),
        mac=mac if mac else None,
        hostname=hostname if hostname else None,
        ip=ip if ip else None,
        network=network if network else None,
        ip_src=ip_src if ip_src else None,
        mfg=mfg if mfg else None,
        limit=limit if limit else None,
        start=start if start else None,
        end=end if end else None,
        duration=duration if duration else None,
        sort=sort if sort else None,
        search_after=search_after if search_after else None,
    )
    await process_response(response)

    data = response.data

    return data
