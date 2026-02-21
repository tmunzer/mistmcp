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


class Stats_type(Enum):
    ORG = "org"
    SITES = "sites"
    ORG_MXEDGES = "org_mxedges"
    ORG_DEVICES = "org_devices"
    ORG_BGP = "org_bgp"
    ORG_OSPF = "org_ospf"
    ORG_PEER_PATHS = "org_peer_paths"
    ORG_PORTS = "org_ports"
    SITE_MXEDGES = "site_mxedges"
    SITE_WIRELESS_CLIENTS = "site_wireless_clients"
    SITE_DEVICES = "site_devices"
    SITE_BGP = "site_bgp"
    SITE_OSPF = "site_ospf"
    SITE_PORTS = "site_ports"


@mcp.tool(
    name="getStats",
    description="""This tool can be used to retrieve various statistics""",
    tags={"stats"},
    annotations={
        "title": "getStats",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getStats(
    stats_type: Annotated[
        Stats_type, Field(description="""Type of statistics to retrieve""")
    ],
    org_id: Annotated[UUID, Field(description="""Organization ID""")],
    site_id: Annotated[Optional[UUID | None], Field(description="""Site ID""")] = None,
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
    object_id: Annotated[
        Optional[UUID | None],
        Field(
            description="""Optional, ID or MAC to filter on: * When stats_type is `sites`, this is not used as site stats do not require an object ID filter * When stats_type is `org_mxedges` or `site_mxedges`, this is the ID of the MX Edge device to retrieve statistics for * When stats_type is `org_devices` or `site_devices`, this is the ID of the device to retrieve statistics for * When stats_type is `org_bgp` or `site_bgp`, this is the MAC address of the BGP peer to retrieve statistics for * When stats_type is `org_ospf` or `site_ospf`, this is the MAC address of the OSPF neighbor to retrieve statistics for * When stats_type is `org_peer_paths` or `site_peer_paths`, this is the MAC address of the peer to retrieve path statistics for * When stats_type is `org_ports` or `site_ports`, this is the MAC address of the switch or gateway port to retrieve statistics for"""
        ),
    ] = None,
    limit: Annotated[
        int, Field(description="""Max number of results per page""", default=10)
    ] = 10,
    ctx: Context | None = None,
) -> dict | list | str:
    """This tool can be used to retrieve various statistics"""

    logger.debug("Tool getStats called")

    apisession, response_format = get_apisession()

    object_type = stats_type

    if object_type.value == "site_mxedges":
        if not site_id:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`site_id` parameter is required when `object_type` is "site_mxedges".',
                }
            )

    if object_type.value == "site_wireless_clients":
        if not site_id:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`site_id` parameter is required when `object_type` is "site_wireless_clients".',
                }
            )

    if object_type.value == "site_devices":
        if not site_id:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`site_id` parameter is required when `object_type` is "site_devices".',
                }
            )

    if object_type.value == "site_bgp":
        if not site_id:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`site_id` parameter is required when `object_type` is "site_bgp".',
                }
            )

    if object_type.value == "site_ospf":
        if not site_id:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`site_id` parameter is required when `object_type` is "site_ospf".',
                }
            )

    if object_type.value == "site_ports":
        if not site_id:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`site_id` parameter is required when `object_type` is "site_ports".',
                }
            )

    match object_type.value:
        case "org":
            response = mistapi.api.v1.orgs.stats.getOrgStats(
                apisession, org_id=str(org_id), start=str(start_time), end=str(end_time)
            )
            await process_response(response)
        case "sites":
            if object_id:
                response = mistapi.api.v1.sites.stats.getSiteStats(
                    apisession,
                    site_id=str(object_id),
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.stats.listOrgSiteStats(
                    apisession,
                    org_id=str(org_id),
                    start=str(start_time),
                    end=str(end_time),
                    limit=limit,
                )
                await process_response(response)
        case "org_mxedges":
            if object_id:
                response = mistapi.api.v1.orgs.stats.getOrgMxEdgeStats(
                    apisession, org_id=str(org_id), mxedge_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.stats.listOrgMxEdgesStats(
                    apisession,
                    org_id=str(org_id),
                    start=str(start_time),
                    end=str(end_time),
                    limit=limit,
                )
                await process_response(response)
        case "org_devices":
            response = mistapi.api.v1.orgs.stats.listOrgDevicesStats(
                apisession,
                org_id=str(org_id),
                start=str(start_time),
                end=str(end_time),
                mac=str(object_id),
                limit=limit,
            )
            await process_response(response)
        case "org_bgp":
            response = mistapi.api.v1.orgs.stats.searchOrgBgpStats(
                apisession,
                org_id=str(org_id),
                start=str(start_time),
                end=str(end_time),
                mac=str(object_id),
                limit=limit,
            )
            await process_response(response)
        case "org_ospf":
            response = mistapi.api.v1.orgs.stats.searchOrgOspfStats(
                apisession,
                org_id=str(org_id),
                start=str(start_time),
                end=str(end_time),
                mac=str(object_id),
            )
            await process_response(response)
        case "org_peer_paths":
            response = mistapi.api.v1.orgs.stats.searchOrgPeerPathStats(
                apisession,
                org_id=str(org_id),
                start=str(start_time),
                end=str(end_time),
                mac=str(object_id),
                limit=limit,
            )
            await process_response(response)
        case "org_ports":
            response = mistapi.api.v1.orgs.stats.searchOrgSwOrGwPorts(
                apisession, org_id=str(org_id), mac=str(object_id), limit=limit
            )
            await process_response(response)
        case "site_mxedges":
            if object_id:
                response = mistapi.api.v1.sites.stats.getSiteMxEdgeStats(
                    apisession,
                    site_id=str(site_id),
                    start=str(start_time),
                    end=str(end_time),
                    mxedge_id=str(object_id),
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.sites.stats.listSiteMxEdgesStats(
                    apisession,
                    site_id=str(site_id),
                    start=str(start_time),
                    end=str(end_time),
                    limit=limit,
                )
                await process_response(response)
        case "site_wireless_clients":
            if object_id:
                response = mistapi.api.v1.sites.stats.getSiteWirelessClientStats(
                    apisession, site_id=str(site_id), client_mac=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.sites.stats.listSiteWirelessClientsStats(
                    apisession,
                    site_id=str(site_id),
                    start=str(start_time),
                    end=str(end_time),
                    limit=limit,
                )
                await process_response(response)
        case "site_devices":
            if object_id:
                response = mistapi.api.v1.sites.stats.getSiteDeviceStats(
                    apisession, site_id=str(site_id), device_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.sites.stats.listSiteDevicesStats(
                    apisession, site_id=str(site_id), limit=limit
                )
                await process_response(response)
        case "site_bgp":
            response = mistapi.api.v1.sites.stats.searchSiteBgpStats(
                apisession,
                site_id=str(site_id),
                start=str(start_time),
                end=str(end_time),
                mac=str(object_id),
                limit=limit,
            )
            await process_response(response)
        case "site_ospf":
            response = mistapi.api.v1.sites.stats.searchSiteOspfStats(
                apisession,
                site_id=str(site_id),
                start=str(start_time),
                end=str(end_time),
                mac=str(object_id),
                limit=limit,
            )
            await process_response(response)
        case "site_ports":
            response = mistapi.api.v1.sites.stats.searchSiteSwOrGwPorts(
                apisession, site_id=str(site_id), mac=str(object_id), limit=limit
            )
            await process_response(response)

        case _:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Stats_type]}",
                }
            )

    return format_response(response, response_format)
