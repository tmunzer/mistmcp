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
    name="searchOrgClient",
    description="""This tool can be used to search for clients in an organization or site. You can filter the search by client type, client name, or MAC address using the `client_type`, `name`, and `mac` parameters, respectivelyIMPORTANT: this tool only returns clients that are currently connected to Mist""",
    tags={"clients"},
    annotations={
        "title": "searchOrgClient",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchOrgClient(
    client_type: Annotated[
        Client_type, Field(description="""Type of client to search for""")
    ],
    org_id: Annotated[UUID, Field(description="""Organization ID""")],
    site_id: Annotated[Optional[UUID | None], Field(description="""Site ID""")] = None,
    device_mac: Annotated[
        Optional[str | None],
        Field(
            description="""MAC address of the device the client is connected to. Not applicable when searching for wan or nac clients"""
        ),
    ] = None,
    band: Annotated[
        Optional[Band | None],
        Field(
            description="""802.11 Band the client is connected on. Only applicable when searching for wireless clients"""
        ),
    ] = None,
    ssid: Annotated[
        Optional[str | None],
        Field(
            description="""SSID the client is connected to. Only applicable when searching for wireless or nac clients"""
        ),
    ] = None,
    mac: Annotated[
        Optional[str | None], Field(description="""Partial / full MAC address""")
    ] = None,
    hostname: Annotated[
        Optional[str | None],
        Field(
            description="""Partial / full hostname. Not applicable when searching for wan and wired clients"""
        ),
    ] = None,
    ip: Annotated[
        Optional[str | None],
        Field(
            description="""IP address. Not applicable when searching for nac clients"""
        ),
    ] = None,
    text: Annotated[
        Optional[str | None],
        Field(
            description="""Text to search for in the client details. Not applicable when searching for wan clients"""
        ),
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
    """This tool can be used to search for clients in an organization or site. You can filter the search by client type, client name, or MAC address using the `client_type`, `name`, and `mac` parameters, respectivelyIMPORTANT: this tool only returns clients that are currently connected to Mist"""

    logger.debug("Tool searchOrgClient called")

    apisession, response_format = get_apisession()

    object_type = client_type
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

    return format_response(response, response_format)
