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


@mcp.tool(
    name="searchSiteWanUsage",
    description="""Search Site WAN Usages""",
    tags={"stats"},
    annotations={
        "title": "searchSiteWanUsage",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchSiteWanUsage(
    site_id: Annotated[UUID, Field(description="""Site ID""")],
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
    ctx: Context | None = None,
) -> dict | list | str:
    """Search Site WAN Usages"""

    logger.debug("Tool searchSiteWanUsage called")

    apisession, response_format = get_apisession()

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
        limit=limit,
        start=start if start else None,
        end=end if end else None,
        duration=duration if duration else None,
        sort=sort if sort else None,
    )
    await process_response(response)

    return format_response(response, response_format)
