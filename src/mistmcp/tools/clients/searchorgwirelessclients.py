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
    name="searchOrgWirelessClients",
    description="""Search Org Wireless Clients""",
    tags={"clients"},
    annotations={
        "title": "searchOrgWirelessClients",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchOrgWirelessClients(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    site_id: Annotated[Optional[UUID | None], Field(description="""Site ID""")] = None,
    mac: Annotated[
        Optional[str | None], Field(description="""Partial / full MAC address""")
    ] = None,
    ip: Optional[str | None] = None,
    hostname: Annotated[
        Optional[str | None], Field(description="""Partial / full hostname""")
    ] = None,
    band: Annotated[
        Optional[str | None], Field(description="""Radio band. enum: `24`, `5`, `6`""")
    ] = None,
    device: Annotated[
        Optional[str | None],
        Field(description="""Device type, e.g. Mac, Nvidia, iPhone"""),
    ] = None,
    os: Annotated[
        Optional[str | None],
        Field(
            description="""Only available for clients running the Marvis Client app, os, e.g. Sierra, Yosemite, Windows 10"""
        ),
    ] = None,
    model: Annotated[
        Optional[str | None],
        Field(
            description="""Only available for clients running the Marvis Client app, model, e.g. 'MBP 15 late 2013', 6, 6s, '8+ GSM'"""
        ),
    ] = None,
    ap: Annotated[
        Optional[str | None],
        Field(description="""AP mac where the client has connected to"""),
    ] = None,
    psk_id: Annotated[Optional[str | None], Field(description="""PSK ID""")] = None,
    psk_name: Annotated[
        Optional[str | None],
        Field(
            description="""Only available for clients using PPSK authentication, the Name of the PSK"""
        ),
    ] = None,
    username: Annotated[
        Optional[str | None],
        Field(
            description="""Only available for clients using 802.1X authentication, partial / full username"""
        ),
    ] = None,
    vlan: Annotated[Optional[str | None], Field(description="""VLAN""")] = None,
    ssid: Annotated[Optional[str | None], Field(description="""SSID""")] = None,
    text: Annotated[
        Optional[str | None],
        Field(
            description="""Partial / full MAC address, hostname, username, psk_name or ip"""
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
    ctx: Context | None = None,
) -> dict | list | str:
    """Search Org Wireless Clients"""

    logger.debug("Tool searchOrgWirelessClients called")

    apisession, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.orgs.clients.searchOrgWirelessClients(
        apisession,
        org_id=str(org_id),
        site_id=str(site_id) if site_id else None,
        mac=mac if mac else None,
        ip=ip if ip else None,
        hostname=hostname if hostname else None,
        band=band if band else None,
        device=device if device else None,
        os=os if os else None,
        model=model if model else None,
        ap=ap if ap else None,
        psk_id=psk_id if psk_id else None,
        psk_name=psk_name if psk_name else None,
        username=username if username else None,
        vlan=vlan if vlan else None,
        ssid=ssid if ssid else None,
        text=text if text else None,
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
