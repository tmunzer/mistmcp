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


class Event_source(Enum):
    DEVICE = "device"
    MXEDGE = "mxedge"
    WAN_CLIENT = "wan_client"
    WIRELESS_CLIENT = "wireless_client"
    NAC_CLIENT = "nac_client"
    ROAMING = "roaming"
    ROGUE = "rogue"


@mcp.tool(
    name="searchEvents",
    description="""This tool can be used to search for events in an organization. You can specify a time range for the search using the `start_time` and `end_time` parameters, and you can also filter the search by event type using the `event_type` parameter""",
    tags={"events"},
    annotations={
        "title": "searchEvents",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchEvents(
    event_source: Annotated[
        Event_source,
        Field(
            description="""Source of events to search for.  * `device`: events related to devices in the organization or site * `mxedge`: events related to MX Edge devices in the organization or site * `wan_client`: events related to WAN clients in the organization or site * `wireless_client`: events related to wireless clients in the organization or site * `nac_client`: events related to NAC clients in the organization or site * `roaming`: events related to wireless client roaming in the site. This required `site_id` parameter is required * `rogue`: events related to rogue devices in the site. This required `site_id` parameter is required"""
        ),
    ],
    org_id: Annotated[UUID, Field(description="""Organization ID""")],
    start_time: Annotated[
        Optional[str | None],
        Field(
            description="""Start time (epoch timestamp in seconds, or relative string like '-1d', '-1w')"""
        ),
    ] = None,
    end_time: Annotated[
        Optional[str | None],
        Field(
            description="""End time (epoch timestamp in seconds, or relative string like '-1d', '-2h', 'now')"""
        ),
    ] = None,
    event_type: Annotated[
        Optional[str | None],
        Field(
            description="""Type of events to search for. The list of possible event types can be obtained with the `getConstants` tool"""
        ),
    ] = None,
    site_id: Annotated[Optional[UUID | None], Field(description="""Site ID""")] = None,
    mac: Annotated[
        Optional[UUID | None],
        Field(
            description="""ID of the device to filter events by. Not applicable when searching for wireless client events"""
        ),
    ] = None,
    text: Annotated[
        Optional[str | None],
        Field(
            description="""Text to search for in the event details. Only applicable when searching for device events or nac client events"""
        ),
    ] = None,
    ssid: Annotated[
        Optional[str | None],
        Field(
            description="""SSID to filter wireless client events by. Only applicable when searching for wireless client events, nac client events, or rogue events"""
        ),
    ] = None,
    limit: Annotated[
        int, Field(description="""Max number of results per page""", default=10)
    ] = 10,
    ctx: Context | None = None,
) -> dict | list | str:
    """This tool can be used to search for events in an organization. You can specify a time range for the search using the `start_time` and `end_time` parameters, and you can also filter the search by event type using the `event_type` parameter"""

    logger.debug("Tool searchEvents called")

    apisession, response_format = get_apisession()

    object_type = event_source

    if object_type.value == "roaming":
        if not site_id:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`site_id` parameter is required when `object_type` is "roaming".',
                }
            )

    if object_type.value == "rogue":
        if not site_id:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`site_id` parameter is required when `object_type` is "rogue".',
                }
            )

    match object_type.value:
        case "device":
            if site_id:
                response = mistapi.api.v1.sites.devices.searchSiteDeviceEvents(
                    apisession,
                    site_id=str(site_id),
                    start=str(start_time) if start_time else None,
                    end=str(end_time) if end_time else None,
                    type=str(event_type) if event_type else None,
                    mac=str(mac) if mac else None,
                    text=str(text) if text else None,
                    limit=limit,
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.devices.searchOrgDeviceEvents(
                    apisession,
                    org_id=str(org_id),
                    start=str(start_time) if start_time else None,
                    end=str(end_time) if end_time else None,
                    type=str(event_type) if event_type else None,
                    mac=str(mac) if mac else None,
                    text=str(text) if text else None,
                    limit=limit,
                )
                await process_response(response)
        case "mxedge":
            if site_id:
                response = mistapi.api.v1.sites.mxedges.searchSiteMistEdgeEvents(
                    apisession,
                    site_id=str(site_id),
                    start=str(start_time) if start_time else None,
                    end=str(end_time) if end_time else None,
                    type=str(event_type) if event_type else None,
                    mxedge_id=f"00000000-0000-0000-1000-{str(mac)}" if mac else None,
                    limit=limit,
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.mxedges.searchOrgMistEdgeEvents(
                    apisession,
                    org_id=str(org_id),
                    start=str(start_time) if start_time else None,
                    end=str(end_time) if end_time else None,
                    type=str(event_type) if event_type else None,
                    mxedge_id=f"00000000-0000-0000-1000-{str(mac)}" if mac else None,
                    limit=limit,
                )
                await process_response(response)
        case "wan_client":
            if site_id:
                response = mistapi.api.v1.sites.wan_clients.searchSiteWanClientEvents(
                    apisession,
                    site_id=str(site_id),
                    start=str(start_time) if start_time else None,
                    end=str(end_time) if end_time else None,
                    type=str(event_type) if event_type else None,
                    mac=str(mac) if mac else None,
                    limit=limit,
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.wan_clients.searchOrgWanClientEvents(
                    apisession,
                    org_id=str(org_id),
                    start=str(start_time) if start_time else None,
                    end=str(end_time) if end_time else None,
                    type=str(event_type) if event_type else None,
                    mac=str(mac) if mac else None,
                    limit=limit,
                )
                await process_response(response)
        case "wireless_client":
            if site_id:
                response = mistapi.api.v1.sites.clients.searchSiteWirelessClientEvents(
                    apisession,
                    site_id=str(site_id),
                    start=str(start_time) if start_time else None,
                    end=str(end_time) if end_time else None,
                    type=str(event_type) if event_type else None,
                    ssid=str(ssid) if ssid else None,
                    limit=limit,
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.clients.searchOrgWirelessClientEvents(
                    apisession,
                    org_id=str(org_id),
                    start=str(start_time) if start_time else None,
                    end=str(end_time) if end_time else None,
                    type=str(event_type) if event_type else None,
                    ssid=str(ssid) if ssid else None,
                    limit=limit,
                )
                await process_response(response)
        case "nac_client":
            if site_id:
                response = mistapi.api.v1.sites.nac_clients.searchSiteNacClientEvents(
                    apisession,
                    site_id=str(site_id),
                    start=str(start_time) if start_time else None,
                    end=str(end_time) if end_time else None,
                    type=str(event_type) if event_type else None,
                    mac=str(mac) if mac else None,
                    text=str(text) if text else None,
                    ssid=str(ssid) if ssid else None,
                    limit=limit,
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.nac_clients.searchOrgNacClientEvents(
                    apisession,
                    org_id=str(org_id),
                    start=str(start_time) if start_time else None,
                    end=str(end_time) if end_time else None,
                    type=str(event_type) if event_type else None,
                    mac=str(mac) if mac else None,
                    text=str(text) if text else None,
                    ssid=str(ssid) if ssid else None,
                    limit=limit,
                )
                await process_response(response)
        case "roaming":
            response = mistapi.api.v1.sites.events.listSiteRoamingEvents(
                apisession,
                site_id=str(site_id),
                start=str(start_time) if start_time else None,
                end=str(end_time) if end_time else None,
                type=str(event_type) if event_type else None,
                limit=limit,
            )
            await process_response(response)
        case "rogue":
            response = mistapi.api.v1.sites.rogues.searchSiteRogueEvents(
                apisession,
                site_id=str(site_id),
                start=str(start_time) if start_time else None,
                end=str(end_time) if end_time else None,
                type=str(event_type) if event_type else None,
                ssid=str(ssid) if ssid else None,
                ap_mac=str(mac) if mac else None,
                limit=limit,
            )
            await process_response(response)

        case _:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Event_source]}",
                }
            )

    return format_response(response, response_format)
