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
    name="searchSiteGuestAuthorization",
    description="""Search Authorized Guest""",
    tags={"clients"},
    annotations={
        "title": "searchSiteGuestAuthorization",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchSiteGuestAuthorization(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    wlan_id: Annotated[
        Optional[str | None], Field(description="""ID of the Mist Wlan""")
    ] = None,
    auth_method: Optional[str | None] = None,
    ssid: Optional[str | None] = None,
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
    guest_mac: Annotated[
        Optional[str | None],
        Field(
            description="""MAC address of the guest to filter authorization by. Optional, if not provided all guest authorizations will be listed."""
        ),
    ] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """Search Authorized Guest"""

    apisession, response_format = get_apisession()
    data = {}

    if guest_mac:
        response = mistapi.api.v1.sites.guests.getSiteGuestAuthorization(
            apisession, site_id=str(site_id), guest_mac=guest_mac
        )
        await process_response(response)
    else:
        response = mistapi.api.v1.sites.guests.searchSiteGuestAuthorization(
            apisession,
            site_id=str(site_id),
            wlan_id=wlan_id if wlan_id else None,
            auth_method=auth_method if auth_method else None,
            ssid=ssid if ssid else None,
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
