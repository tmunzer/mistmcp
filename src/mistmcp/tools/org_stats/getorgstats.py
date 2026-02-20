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


class Stats_type(Enum):
    ORG = "org"
    SITE = "site"
    MXEDGE = "mxedge"
    DEVICES = "devices"
    BGP = "bgp"
    OSPF = "ospf"
    PEER_PATHS = "peer_paths"
    PORT = "port"


@mcp.tool(
    name="getOrgStats",
    description="""This tool can be used to retrieve various statistics about an organization. The type of statistics retrieved will depend on the `stats_type` parameter. When retrieving client stats, you can specify a time range for the stats using the `start_time` and `end_time` parameters. If not specified, the API will return stats for the last 24 hours.""",
    tags={"org_stats"},
    annotations={
        "title": "getOrgStats",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getOrgStats(
    stats_type: Annotated[
        Stats_type,
        Field(description="""Type of statistics to retrieve about the organization."""),
    ],
    org_id: Annotated[
        UUID,
        Field(description="""ID of the organization to retrieve statistics for."""),
    ],
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
            description="""Optional, ID or MAC to filter on: * When stats_type is `site`, this is not used as site stats do not require an object ID filter. * When stats_type is `mxedge`, this is the ID of the MX Edge device to retrieve statistics for. * When stats_type is `devices`, this is the ID of the device to retrieve statistics for. * When stats_type is `bgp`, this is the MAC address of the BGP peer to retrieve statistics for. * When stats_type is `ospf`, this is the MAC address of the OSPF neighbor to retrieve statistics for. * When stats_type is `peer_paths`, this is the MAC address of the peer to retrieve path statistics for. * When stats_type is `port`, this is the MAC address of the switch or gateway port to retrieve statistics for."""
        ),
    ] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """This tool can be used to retrieve various statistics about an organization. The type of statistics retrieved will depend on the `stats_type` parameter. When retrieving client stats, you can specify a time range for the stats using the `start_time` and `end_time` parameters. If not specified, the API will return stats for the last 24 hours."""

    logger.debug("Tool getOrgStats called")

    apisession, response_format = get_apisession()
    data = {}

    object_type = stats_type
    match object_type.value:
        case "org":
            response = mistapi.api.v1.orgs.stats.getOrgStats(
                apisession, org_id=str(org_id), start=str(start_time), end=str(end_time)
            )
            await process_response(response)
            data = response.data
        case "site":
            if object_id:
                response = mistapi.api.v1.sites.stats.getSiteStats(
                    apisession,
                    site_id=str(object_id),
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.stats.listOrgSiteStats(
                    apisession,
                    org_id=str(org_id),
                    start=str(start_time),
                    end=str(end_time),
                )
                await process_response(response)
                data = response.data
        case "mxedge":
            if object_id:
                response = mistapi.api.v1.orgs.stats.getOrgMxEdgeStats(
                    apisession, org_id=str(org_id), mxedge_id=str(object_id)
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.stats.listOrgMxEdgesStats(
                    apisession,
                    org_id=str(org_id),
                    start=str(start_time),
                    end=str(end_time),
                )
                await process_response(response)
                data = response.data
        case "devices":
            response = mistapi.api.v1.orgs.stats.listOrgDevicesStats(
                apisession,
                org_id=str(org_id),
                start=str(start_time),
                end=str(end_time),
                mac=str(object_id),
            )
            await process_response(response)
            data = response.data
        case "bgp":
            response = mistapi.api.v1.orgs.stats.searchOrgBgpStats(
                apisession,
                org_id=str(org_id),
                start=str(start_time),
                end=str(end_time),
                mac=str(object_id),
            )
            await process_response(response)
            data = response.data
        case "ospf":
            response = mistapi.api.v1.orgs.stats.searchOrgOspfStats(
                apisession,
                org_id=str(org_id),
                start=str(start_time),
                end=str(end_time),
                mac=str(object_id),
            )
            await process_response(response)
            data = response.data
        case "peer_paths":
            response = mistapi.api.v1.orgs.stats.searchOrgPeerPathStats(
                apisession,
                org_id=str(org_id),
                start=str(start_time),
                end=str(end_time),
                mac=str(object_id),
            )
            await process_response(response)
            data = response.data
        case "port":
            response = mistapi.api.v1.orgs.stats.searchOrgSwOrGwPorts(
                apisession, org_id=str(org_id), mac=str(object_id)
            )
            await process_response(response)
            data = response.data

        case _:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Stats_type]}",
                }
            )

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
