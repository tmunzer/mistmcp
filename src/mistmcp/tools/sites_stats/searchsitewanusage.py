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


mcp = get_mcp()

if not mcp:
    raise RuntimeError(
        "MCP instance not found. Make sure to initialize the MCP server before defining tools."
    )


@mcp.tool(
    name="searchSiteWanUsage",
    description="""Search Site WAN Usages""",
    tags={"sites_stats"},
    annotations={
        "title": "searchSiteWanUsage",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchSiteWanUsage(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    mac: Annotated[Optional[str | None], Field(description="""MAC address""")] = None,
    peer_mac: Annotated[
        Optional[str | None], Field(description="""Peer MAC address""")
    ] = None,
    port_id: Annotated[
        Optional[str | None], Field(description="""Port ID for the device""")
    ] = None,
    peer_port_id: Annotated[
        Optional[str | None], Field(description="""Peer Port ID for the device""")
    ] = None,
    policy: Annotated[
        Optional[str | None], Field(description="""Policy for the wan path""")
    ] = None,
    tenant: Annotated[
        Optional[str | None],
        Field(description="""Tenant network in which the packet is sent"""),
    ] = None,
    path_type: Annotated[
        Optional[str | None], Field(description="""path_type of the port""")
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
    ctx: Context | None = None,
) -> dict | list | str:
    """Search Site WAN Usages"""

    apisession, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.sites.wan_usages.searchSiteWanUsage(
        apisession,
        site_id=str(site_id),
        mac=mac if mac else None,
        peer_mac=peer_mac if peer_mac else None,
        port_id=port_id if port_id else None,
        peer_port_id=peer_port_id if peer_port_id else None,
        policy=policy if policy else None,
        tenant=tenant if tenant else None,
        path_type=path_type if path_type else None,
        limit=limit if limit else None,
        start=start if start else None,
        end=end if end else None,
        duration=duration if duration else None,
        sort=sort if sort else None,
    )
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
