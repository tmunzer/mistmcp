""" "
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import json
import mistapi
from fastmcp.server.dependencies import get_context, get_http_request
from fastmcp.exceptions import ToolError, ClientError, NotFoundError
from starlette.requests import Request
from mistmcp.config import config
from mistmcp.server_factory import mcp_instance
# from mistmcp.server_factory import mcp

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


mcp = mcp_instance.get()


class Object_type(Enum):
    SITE = "site"
    CLIENT = "client"
    AP = "ap"
    GATEWAY = "gateway"
    MXEDGE = "mxedge"
    SWITCH = "switch"


@mcp.tool(
    enabled=False,
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
        Optional[str],
        Field(
            description="""MAC address of the client or device to retrieve metrics for. Required if object_type is 'client', 'ap', 'mxedge' or 'switch'."""
        ),
    ],
    device_id: Annotated[
        Optional[UUID],
        Field(
            description="""ID of the gateway device to retrieve metrics for. Required if object_type is 'gateway'."""
        ),
    ],
    start: Annotated[
        Optional[str],
        Field(
            description="""Start time (epoch timestamp in seconds, or relative string like '-1d', '-1w')"""
        ),
    ],
    end: Annotated[
        Optional[str],
        Field(
            description="""End time (epoch timestamp in seconds, or relative string like '-1d', '-2h', 'now')"""
        ),
    ],
    duration: Annotated[Optional[str], Field(description="""Duration like 7d, 2w""")],
    interval: Annotated[
        Optional[str],
        Field(
            description="""Aggregation works by giving a time range plus interval (e.g. 1d, 1h, 10m) where aggregation function would be applied to."""
        ),
    ],
    page: Annotated[Optional[int], Field(description="""Page number""")],
    limit: Annotated[
        Optional[int], Field(description="""Number of records per page""")
    ],
) -> dict | list:
    """Get insight metrics for a given object"""

    ctx = get_context()
    if config.transport_mode == "http":
        try:
            request: Request = get_http_request()
            cloud = request.query_params.get("cloud", None)
            apitoken = request.headers.get("X-Authorization", None)
        except NotFoundError as exc:
            raise ClientError(
                "HTTP request context not found. Are you using HTTP transport?"
            ) from exc
        if not cloud or not apitoken:
            raise ClientError(
                "Missing required parameters: 'cloud' and 'X-Authorization' header"
            )
    else:
        apitoken = config.mist_apitoken
        cloud = config.mist_host

    if not apitoken:
        raise ClientError(
            "Missing required parameter: 'X-Authorization' header or mist_apitoken in config"
        )
    if not cloud:
        raise ClientError(
            "Missing required parameter: 'cloud' query parameter or mist_host in config"
        )

    apisession = mistapi.APISession(
        host=cloud,
        apitoken=apitoken,
    )

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

        case _:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Object_type]}",
                }
            )

    if response.status_code != 200:
        api_error = {"status_code": response.status_code, "message": ""}
        if response.data:
            # await ctx.error(f"Got HTTP{response.status_code} with details {response.data}")
            api_error["message"] = json.dumps(response.data)
        elif response.status_code == 400:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps(
                "Bad Request. The API endpoint exists but its syntax/payload is incorrect, detail may be given"
            )
        elif response.status_code == 401:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps("Unauthorized")
        elif response.status_code == 403:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps("Unauthorized")
        elif response.status_code == 401:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps("Permission Denied")
        elif response.status_code == 404:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps(
                "Not found. The API endpoint doesn’t exist or resource doesn’t exist"
            )
        elif response.status_code == 429:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps(
                "Too Many Request. The API Token used for the request reached the 5000 API Calls per hour threshold"
            )
        raise ToolError(api_error)

    return response.data
