"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import mistapi
from fastmcp import Context
from fastmcp.exceptions import ToolError
from mistmcp.request_processor import get_apisession
from mistmcp.response_processor import process_response, handle_network_error
from mistmcp.response_formatter import format_response
from mistmcp.server import mcp
from mistmcp.logger import logger

from pydantic import Field
from typing import Annotated
from enum import Enum
from uuid import UUID


class Scope(Enum):
    ORG = "org"
    SITE = "site"


@mcp.tool(
    name="mist_search_guest_authorization",
    description="""Search for guest authorization entries in an organization or site""",
    tags={"clients"},
    annotations={
        "title": "Search guest authorization",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def search_guest_authorization(
    scope: Annotated[
        Scope,
        Field(
            description="""Whether to search in the entire organization or a specific site. If `site` is selected, the `site_id` parameter is required"""
        ),
    ],
    org_id: Annotated[UUID, Field(description="""Organization ID""")],
    site_id: Annotated[UUID, Field(description="""Site ID""", default=None)],
    guest_mac: Annotated[
        str,
        Field(
            description="""MAC address of the guest to search for in the authorization entries""",
            default=None,
        ),
    ],
    wlan_id: Annotated[
        UUID,
        Field(
            description="""ID of the WLAN to filter guest authorization entries by""",
            default=None,
        ),
    ],
    auth_method: Annotated[
        str,
        Field(
            description="""Authentication method to filter guest authorization entries by""",
            default=None,
        ),
    ],
    ssid: Annotated[
        str,
        Field(
            description="""SSID to filter guest authorization entries by""",
            default=None,
        ),
    ],
    start: Annotated[
        int, Field(description="""Start of time range (epoch seconds)""", default=None)
    ],
    end: Annotated[
        int, Field(description="""End of time range (epoch seconds)""", default=None)
    ],
    limit: Annotated[
        int, Field(description="""Max number of results per page""", default=20)
    ] = 20,
) -> dict | list | str:
    """Search for guest authorization entries in an organization or site"""

    logger.debug("Tool search_guest_authorization called")

    apisession, response_format = await get_apisession()

    try:
        object_type = scope

        if object_type.value == "site":
            if not site_id:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": '`site_id` parameter is required when `scope` is "site".',
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
                        start=str(start) if start else None,
                        end=str(end) if end else None,
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
                        start=str(start) if start else None,
                        end=str(end) if end else None,
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

    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
