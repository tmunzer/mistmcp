SEARCH_CLIENT_OPERATION_IDS = [
    "searchOrgWanClients",
    "searchOrgWiredClients",
    "searchOrgWirelessClients",
    "searchOrgNacClients",
    "getOrgGuestAuthorization",
    "searchOrgGuestAuthorization",
    "getSiteGuestAuthorization",
    "searchSiteGuestAuthorization",
]

SEARCH_CLIENT_TEMPLATE = '''"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

from enum import Enum
from typing import Annotated
from uuid import UUID

import mistapi
from fastmcp.exceptions import ToolError
from pydantic import Field

from mistmcp.logger import logger
from mistmcp.request_processor import get_apisession
from mistmcp.response_formatter import format_response
from mistmcp.response_processor import handle_network_error, process_response
from mistmcp.server import mcp


class Client_type(Enum):
    WAN = "wan"
    WIRED = "wired"
    WIRELESS = "wireless"
    NAC = "nac"
    ORG_GUEST = "org_guest"
    SITE_GUEST = "site_guest"


class Band(Enum):
    B24 = "24"
    B5 = "5"
    B6 = "6"


@mcp.tool(
    name="mist_search_client",
    description="""Search for clients across an organization or specific site. 
Supports searching by client type (WAN, wired, wireless, NAC), MAC address, hostname, IP address, and more.
Use wildcards (*) for partial matches on MAC address, hostname, IP, and text fields.
Different client types support different filter parameters - the tool will validate compatibility.

NOTE:
- For org_guest and site_guest client types, results represent CONNECTED guest sessions — clients that have actively authenticated through the captive portal within the time window (default: last 24h). This is NOT the same as guest authorizations.
- Guest authorizations (pre-created access records that allow a specific MAC to bypass the portal, even without an active connection) must be retrieved separately using mist_get_configuration_objects with object_type='org_guest_authorizations' or 'site_guest_authorizations'.
- For org_guest and site_guest, only sessions created after the "start" timestamp (default: 24h ago) and before the "end" timestamp (default: now) will be returned.
""",
    tags={"clients"},
    annotations={
        "title": "Search client",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def search_client(
    client_type: Annotated[
        Client_type,
        Field(
            description="""Type of client: WAN, wired, wireless, NAC, Org guest, or Site guest"""
        ),
    ],
    org_id: Annotated[UUID, Field(description="""Organization ID""")],
    site_id: Annotated[
        UUID,
        Field(
            description="""Site ID. Required for site_guest, optional for other client types""",
            default=None,
        ),
    ],
    device_mac: Annotated[
        str,
        Field(
            description="""Partial / full MAC Address of the Access Point or the Switch. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `aabbcc*` and `*bbcc*` match `aabbccddeeff`). Suffix-only wildcards (e.g. `*bccddeeff`) are not supported. Not applicable for WAN clients or Org/Site Guests""",
            default=None,
        ),
    ],
    band: Annotated[
        Band,
        Field(
            description="""802.11 band (24 or 5 or 6 GHz). Wireless clients only""",
            default=None,
        ),
    ],
    mac: Annotated[
        str,
        Field(
            description="""Partial / full Client MAC Address. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `aabbcc*` and `*bbcc*` match `aabbccddeeff`). Suffix-only wildcards (e.g. `*bccddeeff`) are not supported""",
            default=None,
        ),
    ],
    hostname: Annotated[
        str,
        Field(
            description="""Partial / full Client hostname. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `everest*` and `*rest*` match `my-everest-client`). Suffix-only wildcards (e.g. `*everest`) are not supported. Not applicable for wired clients or Org/Site Guests""",
            default=None,
        ),
    ],
    ip: Annotated[
        str,
        Field(
            description="""Partial / full Client IP Address.  Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `10.100.10.*` and  `*100.10.*` match `10.100.10.54`). Suffix-only wildcards (e.g. `*.54`) are not supported. Not applicable for NAC clients or Org/Site Guests""",
            default=None,
        ),
    ],
    ssid: Annotated[
        str,
        Field(
            description="""SSID name to filter by. Only applicable for wireless clients, Guests, and NAC clients""",
            default=None,
        ),
    ],
    text: Annotated[
        str,
        Field(
            description="""Free text search in client details (supports * wildcard). Not applicable for WAN clients or Org/Site Guests""",
            default=None,
        ),
    ],
    start: Annotated[
        int, Field(
            description="""Start of time range (epoch seconds)""", default=None)
    ],
    end: Annotated[
        int, Field(
            description="""End of time range (epoch seconds)""", default=None)
    ],
    limit: Annotated[
        int, Field(description="""Max number of results per page""", default=20)
    ] = 20,
) -> dict | list | str:
    """Search for clients across an organization or specific site.
    Supports searching by client type (WAN, wired, wireless, NAC), MAC address, hostname, IP address, and more.
    Use wildcards (*) for partial matches on MAC address, hostname, IP, and text fields.
    Different client types support different filter parameters - the tool will validate compatibility."""

    logger.debug("Tool search_client called")
    logger.debug(
        "Input Parameters: client_type: %s, org_id: %s, site_id: %s, device_mac: %s, band: %s, mac: %s, hostname: %s, ip: %s, ssid: %s, text: %s, start: %s, end: %s, limit: %s",
        client_type,
        org_id,
        site_id,
        device_mac,
        band,
        mac,
        hostname,
        ip,
        ssid,
        text,
        start,
        end,
        limit,
    )

    apisession, response_format = await get_apisession()

    try:
        object_type = client_type

        if device_mac and client_type.value not in ["wireless", "wired"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`device_mac` parameter can only be used when `client_type` is in "wireless", "wired".',
                }
            )

        if band and client_type.value not in ["wireless"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`band` parameter can only be used when `client_type` is "wireless".',
                }
            )

        if hostname and client_type.value not in ["wireless", "nac", "wan"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`hostname` parameter can only be used when `client_type` is in "wireless", "nac", "wan".',
                }
            )

        if ip and client_type.value not in ["wan", "wired", "wireless"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`ip` parameter can only be used when `client_type` is in "wan", "wired", "wireless".',
                }
            )

        if ssid and client_type.value not in [
            "wireless",
            "org_guest",
            "site_guest",
            "nac",
        ]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`ssid` parameter can only be used when `client_type` is in "wireless", "org_guest", "site_guest", "nac".',
                }
            )

        if text and client_type.value not in ["wired", "wireless", "nac"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`text` parameter can only be used when `client_type` is in "wired", "wireless", "nac".',
                }
            )

        match object_type.value:
            case "wan":
                response = mistapi.api.v1.orgs.wan_clients.searchOrgWanClients(
                    apisession,
                    org_id=str(org_id),
                    site_id=str(site_id) if site_id else None,
                    mac=str(mac) if mac else None,
                    hostname=str(hostname) if hostname else None,
                    ip=str(ip) if ip else None,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    limit=limit,
                )
                await process_response(response)
            case "wired":
                response = mistapi.api.v1.orgs.wired_clients.searchOrgWiredClients(
                    apisession,
                    org_id=str(org_id),
                    site_id=str(site_id) if site_id else None,
                    device_mac=str(device_mac) if device_mac else None,
                    mac=str(mac) if mac else None,
                    ip=str(ip) if ip else None,
                    text=str(text) if text else None,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    limit=limit,
                )
                await process_response(response)
            case "wireless":
                response = mistapi.api.v1.orgs.clients.searchOrgWirelessClients(
                    apisession,
                    org_id=str(org_id),
                    site_id=str(site_id) if site_id else None,
                    ap=str(device_mac) if device_mac else None,
                    band=str(band) if band else None,
                    ssid=str(ssid) if ssid else None,
                    mac=str(mac) if mac else None,
                    hostname=str(hostname) if hostname else None,
                    ip=str(ip) if ip else None,
                    text=str(text) if text else None,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    limit=limit,
                )
                await process_response(response)
            case "nac":
                response = mistapi.api.v1.orgs.nac_clients.searchOrgNacClients(
                    apisession,
                    org_id=str(org_id),
                    site_id=str(site_id) if site_id else None,
                    ssid=str(ssid) if ssid else None,
                    mac=str(mac) if mac else None,
                    hostname=str(hostname) if hostname else None,
                    text=str(text) if text else None,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    limit=limit,
                )
                await process_response(response)
            case "org_guest":
                if mac:
                    response = mistapi.api.v1.orgs.guests.getOrgGuestAuthorization(
                        apisession, org_id=str(org_id), guest_mac=str(mac)
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.guests.searchOrgGuestAuthorization(
                        apisession,
                        org_id=str(org_id),
                        ssid=str(ssid) if ssid else None,
                        start=str(start) if start else None,
                        end=str(end) if end else None,
                        limit=limit,
                    )
                    await process_response(response)
            case "site_guest":
                if not site_id:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": '`site_id` parameter is required when `client_type` is "site_guest".',
                        }
                    )
                if mac:
                    response = mistapi.api.v1.sites.guests.getSiteGuestAuthorization(
                        apisession, site_id=str(site_id), guest_mac=str(mac)
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.sites.guests.searchSiteGuestAuthorization(
                        apisession,
                        site_id=str(site_id),
                        ssid=str(ssid) if ssid else None,
                        start=str(start) if start else None,
                        end=str(end) if end else None,
                        limit=limit,
                    )
                    await process_response(response)

            case _:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Client_type]}",
                    }
                )

    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
'''
