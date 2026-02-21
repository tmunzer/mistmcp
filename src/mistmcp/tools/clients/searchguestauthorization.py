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
from enum import Enum
from uuid import UUID


class Scope(Enum):
    ORG = "org"
    SITE = "site"


@mcp.tool(
    name="searchGuestAuthorization",
    description="""This tool can be used to search for guest authorization entries in an organization or site""",
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
            description="""Whether to search in the entire organization or a specific site. If `site` is selected, the `site_id` parameter is required"""
        ),
    ],
    org_id: Annotated[UUID, Field(description="""Organization ID""")],
    site_id: Annotated[Optional[UUID | None], Field(description="""Site ID""")] = None,
    guest_mac: Annotated[
        Optional[str | None],
        Field(
            description="""MAC address of the guest to search for in the authorization entries"""
        ),
    ] = None,
    wlan_id: Annotated[
        Optional[UUID | None],
        Field(
            description="""ID of the WLAN to filter guest authorization entries by"""
        ),
    ] = None,
    auth_method: Annotated[
        Optional[str | None],
        Field(
            description="""Authentication method to filter guest authorization entries by"""
        ),
    ] = None,
    ssid: Annotated[
        Optional[str | None],
        Field(description="""SSID to filter guest authorization entries by"""),
    ] = None,
    start: Annotated[
        Optional[str | None],
        Field(description="""Start of time range (epoch seconds)"""),
    ] = None,
    end: Annotated[
        Optional[str | None], Field(description="""End of time range (epoch seconds)""")
    ] = None,
    limit: Annotated[
        int, Field(description="""Max number of results per page""", default=10)
    ] = 10,
    ctx: Context | None = None,
) -> dict | list | str:
    """This tool can be used to search for guest authorization entries in an organization or site"""

    logger.debug("Tool searchGuestAuthorization called")

    apisession, response_format = get_apisession()

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
            else:
                response = mistapi.api.v1.orgs.guests.searchOrgGuestAuthorization(
                    apisession,
                    org_id=str(org_id),
                    wlan_id=str(wlan_id) if wlan_id else None,
                    auth_method=auth_method if auth_method else None,
                    ssid=ssid if ssid else None,
                    start=start if start else None,
                    end=end if end else None,
                    limit=limit,
                )
                await process_response(response)
        case "site":
            if guest_mac:
                response = mistapi.api.v1.sites.guests.getSiteGuestAuthorization(
                    apisession, site_id=str(site_id), guest_mac=str(guest_mac)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.sites.guests.searchSiteGuestAuthorization(
                    apisession,
                    site_id=str(site_id),
                    wlan_id=str(wlan_id) if wlan_id else None,
                    auth_method=auth_method if auth_method else None,
                    ssid=ssid if ssid else None,
                    start=start if start else None,
                    end=end if end else None,
                    limit=limit,
                )
                await process_response(response)

        case _:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Scope]}",
                }
            )

    return format_response(response, response_format)
