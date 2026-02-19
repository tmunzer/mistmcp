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
from fastmcp.exceptions import ToolError
from mistmcp.request_processor import get_apisession
from mistmcp.response_processor import process_response
from mistmcp.server import get_mcp

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


mcp = get_mcp()

if not mcp:
    raise RuntimeError(
        "MCP instance not found. Make sure to initialize the MCP server before defining tools."
    )


class Object_type(Enum):
    SITE = "site"
    CLIENT = "client"
    AP = "ap"
    GATEWAY = "gateway"
    MXEDGE = "mxedge"
    SWITCH = "switch"


@mcp.tool(
    enabled=True,
    name="getInsightMetrics",
    description="""Get insight metrics for a given object""",
    tags={"sites_insights"},
    annotations={
        "title": "getInsightMetrics",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getInsightMetrics(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    object_type: Annotated[
        Object_type, Field(description="""Type of object to retrieve metrics for.""")
    ],
    metric: Annotated[
        str,
        Field(
            description="""Name of the metric to retrieve. Use the tool `listSiteInsightMetrics` to see available metrics."""
        ),
    ],
    mac: Annotated[
        Optional[str | None],
        Field(
            description="""MAC address of the client or device to retrieve metrics for. Required if object_type is 'client', 'ap', 'mxedge' or 'switch'."""
        ),
    ] = None,
    device_id: Annotated[
        Optional[UUID | None],
        Field(
            description="""ID of the gateway device to retrieve metrics for. Required if object_type is 'gateway'."""
        ),
    ] = None,
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
    interval: Annotated[
        Optional[str | None],
        Field(
            description="""Aggregation works by giving a time range plus interval (e.g. 1d, 1h, 10m) where aggregation function would be applied to."""
        ),
    ] = None,
    page: Annotated[Optional[int | None], Field(description="""Page number""")] = None,
    limit: Annotated[
        Optional[int | None], Field(description="""Number of records per page""")
    ] = None,
) -> dict | list | str:
    """Get insight metrics for a given object"""

    apisession, _, response_format = get_apisession()
    data = {}

    match object_type.value:
        case "site":
            response = mistapi.api.v1.sites.insights.getSiteInsightMetrics(
                apisession,
                site_id=str(site_id),
                metric=str(metric),
                start=str(start),
                end=str(end),
                duration=str(duration),
                interval=str(interval),
                limit=limit,
                page=page,
            )
            await process_response(response)
            data = response.data
        case "client":
            response = mistapi.api.v1.sites.insights.getSiteInsightMetricsForClient(
                apisession,
                site_id=str(site_id),
                client_mac=str(mac),
                metric=str(metric),
                start=str(start),
                end=str(end),
                duration=str(duration),
                interval=str(interval),
                limit=limit,
                page=page,
            )
            await process_response(response)
            data = response.data
        case "ap":
            response = mistapi.api.v1.sites.insights.getSiteInsightMetricsForDevice(
                apisession,
                site_id=str(site_id),
                device_mac=str(mac),
                metric=str(metric),
                start=str(start),
                end=str(end),
                duration=str(duration),
                interval=str(interval),
                limit=limit,
                page=page,
            )
            await process_response(response)
            data = response.data
        case "gateway":
            response = mistapi.api.v1.sites.insights.getSiteInsightMetricsForGateway(
                apisession,
                site_id=str(site_id),
                device_id=str(device_id),
                metric=str(metric),
                start=str(start),
                end=str(end),
                duration=str(duration),
                interval=str(interval),
                limit=limit,
                page=page,
            )
            await process_response(response)
            data = response.data
        case "mxedge":
            response = mistapi.api.v1.sites.insights.getSiteInsightMetricsForMxEdge(
                apisession,
                site_id=str(site_id),
                device_mac=str(mac),
                metric=str(metric),
                start=str(start),
                end=str(end),
                duration=str(duration),
                interval=str(interval),
                limit=limit,
                page=page,
            )
            await process_response(response)
            data = response.data
        case "switch":
            response = mistapi.api.v1.sites.insights.getSiteInsightMetricsForSwitch(
                apisession,
                site_id=str(site_id),
                device_mac=str(mac),
                metric=str(metric),
                start=str(start),
                end=str(end),
                duration=str(duration),
                interval=str(interval),
                limit=limit,
                page=page,
            )
            await process_response(response)
            data = response.data

        case _:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Object_type]}",
                }
            )

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
