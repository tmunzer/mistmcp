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
from enum import Enum


mcp = get_mcp()

if not mcp:
    raise RuntimeError(
        "MCP instance not found. Make sure to initialize the MCP server before defining tools."
    )


class Type(Enum):
    HONEYPOT = "honeypot"
    LAN = "lan"
    OTHERS = "others"
    SPOOF = "spoof"
    NONE = None


@mcp.tool(
    enabled=True,
    name="searchSiteRogueEvents",
    description="""Search Rogue Events""",
    tags={"Sites Rogues"},
    annotations={
        "title": "searchSiteRogueEvents",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchSiteRogueEvents(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    type: Optional[Type | None] = Type.NONE,
    ssid: Annotated[
        Optional[str | None],
        Field(description="""SSID of the network detected as threat"""),
    ] = None,
    bssid: Annotated[
        Optional[str | None],
        Field(description="""BSSID of the network detected as threat"""),
    ] = None,
    ap_mac: Annotated[
        Optional[str | None],
        Field(
            description="""MAC of the device that had strongest signal strength for ssid/bssid pair"""
        ),
    ] = None,
    channel: Annotated[
        Optional[int | None],
        Field(description="""Channel over which ap_mac heard ssid/bssid pair"""),
    ] = None,
    seen_on_lan: Annotated[
        Optional[bool | None],
        Field(
            description="""Whether the reporting AP see a wireless client (on LAN) connecting to it"""
        ),
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
) -> dict | list:
    """Search Rogue Events"""

    apisession = get_apisession()
    data = {}

    response = mistapi.api.v1.sites.rogues.searchSiteRogueEvents(
        apisession,
        site_id=str(site_id),
        type=type.value if type else None,
        ssid=ssid if ssid else None,
        bssid=bssid if bssid else None,
        ap_mac=ap_mac if ap_mac else None,
        channel=channel if channel else None,
        seen_on_lan=seen_on_lan if seen_on_lan else None,
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
