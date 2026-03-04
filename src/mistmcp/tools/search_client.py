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
from typing import Annotated, Optional
from enum import Enum
from uuid import UUID


class Client_type(Enum):
    WAN = "wan"
    WIRED = "wired"
    WIRELESS = "wireless"
    NAC = "nac"


class Band(Enum):
    B24 = "24"
    B5 = "5"
    B6 = "6"


@mcp.tool(
    name="mist_search_client",
    description="""This tool can be used to search for clients in an organization or site. You can filter the search by client type, client name, or MAC address using the `client_type`, `name`, and `mac` parameters, respectively. IMPORTANT:  Use wildcard (`*`) before or after the value for partial search when applicable.""",
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
        Client_type, Field(description="""Type of client to search for""")
    ],
    org_id: Annotated[UUID, Field(description="""Organization ID""")],
    site_id: Annotated[Optional[UUID], Field(description="""Site ID""")],
    device_mac: Annotated[
        Optional[str],
        Field(
            description="""MAC address of the device the client is connected to. Not applicable when searching for wan or nac clients"""
        ),
    ],
    band: Annotated[
        Optional[Band],
        Field(
            description="""802.11 Band the client is connected on. Only applicable when searching for wireless clients"""
        ),
    ],
    ssid: Annotated[
        Optional[str],
        Field(
            description="""SSID the client is connected to. Only applicable when searching for wireless or nac clients"""
        ),
    ],
    mac: Annotated[Optional[str], Field(description="""Partial / full MAC address""")],
    hostname: Annotated[
        Optional[str],
        Field(
            description="""Partial / full hostname. Not applicable when searching for wan and wired clients"""
        ),
    ],
    ip: Annotated[
        Optional[str],
        Field(
            description="""IP address. Not applicable when searching for nac clients"""
        ),
    ],
    text: Annotated[
        Optional[str],
        Field(
            description="""Text to search for in the client details. Not applicable when searching for wan clients"""
        ),
    ],
    start: Annotated[
        Optional[int], Field(description="""Start of time range (epoch seconds)""")
    ],
    end: Annotated[
        Optional[int], Field(description="""End of time range (epoch seconds)""")
    ],
    limit: Annotated[
        int, Field(description="""Max number of results per page""", default=20)
    ] = 20,
    ctx: Context | None = None,
) -> dict | list | str:
    """This tool can be used to search for clients in an organization or site. You can filter the search by client type, client name, or MAC address using the `client_type`, `name`, and `mac` parameters, respectively. IMPORTANT:  Use wildcard (`*`) before or after the value for partial search when applicable."""

    logger.debug("Tool search_client called")

    apisession, response_format = await get_apisession()

    try:
        object_type = client_type

        if band and client_type.value not in ["wireless"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`band` parameter can only be used when `client_type` is "wireless".',
                }
            )

        if ssid and client_type.value not in ["wireless", "nac"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`ssid` parameter can only be used when `client_type` is in "wireless", "nac".',
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
