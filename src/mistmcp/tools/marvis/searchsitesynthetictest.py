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
from enum import Enum


class Type(Enum):
    ARP = "arp"
    CURL = "curl"
    DHCP = "dhcp"
    DHCP6 = "dhcp6"
    DNS = "dns"
    LAN_CONNECTIVITY = "lan_connectivity"
    RADIUS = "radius"
    SPEEDTEST = "speedtest"
    NONE = None


class Protocol(Enum):
    PING = "ping"
    TRACEROUTE = "traceroute"
    NONE = None


@mcp.tool(
    name="searchSiteSyntheticTest",
    description="""Search Site Synthetic Testing""",
    tags={"marvis"},
    annotations={
        "title": "searchSiteSyntheticTest",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchSiteSyntheticTest(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    mac: Annotated[
        Optional[str | None], Field(description="""Device MAC Address""")
    ] = None,
    port_id: Annotated[
        Optional[str | None],
        Field(description="""Port_id used to run the test (for SSR only)"""),
    ] = None,
    vlan_id: Annotated[Optional[str | None], Field(description="""VLAN ID""")] = None,
    by: Annotated[
        Optional[str | None], Field(description="""Entity who triggers the test""")
    ] = None,
    reason: Annotated[
        Optional[str | None], Field(description="""Test failure reason""")
    ] = None,
    type: Annotated[
        Optional[Type | None], Field(description="""Synthetic test type""")
    ] = Type.NONE,
    protocol: Annotated[
        Optional[Protocol | None], Field(description="""Connectivity protocol""")
    ] = Protocol.NONE,
    tenant: Annotated[
        Optional[str | None],
        Field(description="""Tenant network in which lan_connectivity test was run"""),
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
    search_after: Annotated[
        Optional[str | None],
        Field(
            description="""Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed."""
        ),
    ] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """Search Site Synthetic Testing"""

    logger.debug("Tool searchSiteSyntheticTest called")

    apisession, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.sites.synthetic_test.searchSiteSyntheticTest(
        apisession,
        site_id=str(site_id),
        mac=mac if mac else None,
        port_id=port_id if port_id else None,
        vlan_id=vlan_id if vlan_id else None,
        by=by if by else None,
        reason=reason if reason else None,
        type=type.value if type else None,
        protocol=protocol.value if protocol else None,
        tenant=tenant if tenant else None,
        limit=limit if limit else None,
        start=start if start else None,
        end=end if end else None,
        duration=duration if duration else None,
        search_after=search_after if search_after else None,
    )
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
