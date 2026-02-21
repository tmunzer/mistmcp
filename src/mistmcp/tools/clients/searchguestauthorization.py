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
from enum import Enum
from uuid import UUID


class Scope(Enum):
    ORG = "org"
    SITE = "site"


@mcp.tool(
    name="searchGuestAuthorization",
    description="""This tool can be used to search for guest authorization entries in an organization or site.""",
    tags={"clients"},
    annotations={
        "title": "searchGuestAuthorization",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchGuestAuthorization(
    scope: Annotated[
        Scope,
        Field(
            description="""Whether to search in the entire organization or a specific site. If `site` is selected, the `site_id` parameter is required."""
        ),
    ],
    org_id: Annotated[
        UUID,
        Field(
            description="""ID of the organization to search for guest authorization entries in."""
        ),
    ],
    site_id: Annotated[
        Optional[UUID | None],
        Field(
            description="""ID of the site to search for guest authorization entries in. If not specified, entries from all sites in the organization will be included in the search."""
        ),
    ] = None,
    guest_mac: Annotated[
        Optional[str | None],
        Field(
            description="""MAC address of the guest to search for in the authorization entries. If not specified, entries will not be filtered by guest MAC address."""
        ),
    ] = None,
    wlan_id: Annotated[
        Optional[UUID | None],
        Field(
            description="""ID of the WLAN to filter guest authorization entries by. If not specified, entries will not be filtered by WLAN."""
        ),
    ] = None,
    auth_method: Annotated[
        Optional[str | None],
        Field(
            description="""Authentication method to filter guest authorization entries by. If not specified, entries will not be filtered by authentication method."""
        ),
    ] = None,
    ssid: Annotated[
        Optional[str | None],
        Field(
            description="""SSID to filter guest authorization entries by. If not specified, entries will not be filtered by SSID."""
        ),
    ] = None,
    start: Annotated[
        Optional[str | None],
        Field(
            description="""Start time (epoch timestamp in seconds, or relative string like '-1d', '-1w') to filter guest authorization entries by. If not specified, entries will not be filtered by start time."""
        ),
    ] = None,
    end: Annotated[
        Optional[str | None],
        Field(
            description="""End time (epoch timestamp in seconds, or relative string like '-1d', '-1w') to filter guest authorization entries by. If not specified, entries will not be filtered by end time."""
        ),
    ] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """This tool can be used to search for guest authorization entries in an organization or site."""

    logger.debug("Tool searchGuestAuthorization called")

    apisession, response_format = get_apisession()
    data = {}

    object_type = scope

    if object_type.value == "site":
        if not site_id:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`site_id` parameter is required when `object_type` is "site".',
                }
            )

    match object_type.value:
        case "org":
            if guest_mac:
                response = mistapi.api.v1.orgs.guests.getOrgGuestAuthorization(
                    apisession, org_id=str(org_id), guest_mac=str(guest_mac)
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.guests.searchOrgGuestAuthorization(
                    apisession,
                    org_id=str(org_id),
                    wlan_id=str(wlan_id) if wlan_id else None,
                    auth_method=auth_method if auth_method else None,
                    ssid=ssid if ssid else None,
                    start=start if start else None,
                    end=end if end else None,
                )
                await process_response(response)
                data = response.data
        case "site":
            if guest_mac:
                response = mistapi.api.v1.sites.guests.getSiteGuestAuthorization(
                    apisession, site_id=str(site_id), guest_mac=str(guest_mac)
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.sites.guests.searchSiteGuestAuthorization(
                    apisession,
                    site_id=str(site_id),
                    wlan_id=str(wlan_id) if wlan_id else None,
                    auth_method=auth_method if auth_method else None,
                    ssid=ssid if ssid else None,
                    start=start if start else None,
                    end=end if end else None,
                )
                await process_response(response)
                data = response.data

        case _:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Scope]}",
                }
            )

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
