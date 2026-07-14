"""Insight-metric and RRM facade tool."""

from enum import Enum
from typing import Annotated
from uuid import UUID

import mistapi
from fastmcp.exceptions import ToolError
from fastmcp.tools import ToolResult
from pydantic import Field

from mistmcp.logger import logger
from mistmcp.request_processor import get_apisession
from mistmcp.response_formatter import format_response
from mistmcp.response_processor import handle_network_error, process_response
from mistmcp.server import mcp
from mistmcp.tools._facade import arguments, internal_tool, run_internal_tool


class SiteInsightType(Enum):
    METRIC = "metric"
    RRM = "rrm"


class Object_type(Enum):
    SITE = "site"
    CLIENT = "client"
    AP = "ap"
    GATEWAY = "gateway"
    MXEDGE = "mxedge"
    SWITCH = "switch"


async def get_insight_metrics(
    site_id: Annotated[UUID, Field(description="Site ID")],
    object_type: Annotated[
        Object_type, Field(description="Type of object to retrieve metrics for")
    ],
    metric: Annotated[
        str,
        Field(
            description="Name of the metric to retrieve. Use `mist_describe(subject=constant, name=insight_metrics)` to see available metrics"
        ),
    ],
    mac: Annotated[
        str,
        Field(
            description="MAC address of the client or device to retrieve metrics for. Required if object_type is 'client', 'ap', 'mxedge' or 'switch'",
            default=None,
        ),
    ],
    device_id: Annotated[
        UUID,
        Field(
            description="ID of the gateway device to retrieve metrics for. Required if object_type is 'gateway'",
            default=None,
        ),
    ],
    start: Annotated[
        int, Field(description="Start of time range (epoch seconds)", default=None)
    ],
    end: Annotated[
        int, Field(description="End of time range (epoch seconds)", default=None)
    ],
    duration: Annotated[
        str, Field(description="Time range duration (e.g. 1d, 1h, 10m)", default=None)
    ],
    interval: Annotated[
        str, Field(description="Aggregation interval (e.g. 1h, 1d)", default=None)
    ],
    page: Annotated[int, Field(description="Page number for pagination", default=None)],
    limit: Annotated[
        int, Field(description="Max number of results per page", default=20)
    ] = 20,
) -> dict | list | str:
    """Get insight metrics for a given object"""
    logger.debug("Tool get_insight_metrics called")
    logger.debug(
        "Input Parameters: site_id: %s, object_type: %s, metric: %s, mac: %s, device_id: %s, start: %s, end: %s, duration: %s, interval: %s, page: %s, limit: %s",
        site_id,
        object_type,
        metric,
        mac,
        device_id,
        start,
        end,
        duration,
        interval,
        page,
        limit,
    )
    apisession, response_format = await get_apisession()
    try:
        match object_type.value:
            case "site":
                response = mistapi.api.v1.sites.insights.getSiteInsightMetrics(
                    apisession,
                    site_id=str(site_id),
                    metrics=str(metric),
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    duration=str(duration) if duration else None,
                    interval=str(interval) if interval else None,
                    limit=limit,
                    page=page,
                )
                await process_response(response)
            case "client":
                response = mistapi.api.v1.sites.insights.getSiteInsightMetricsForClient(
                    apisession,
                    site_id=str(site_id),
                    client_mac=str(mac),
                    metrics=str(metric),
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    duration=str(duration) if duration else None,
                    interval=str(interval) if interval else None,
                    limit=limit,
                    page=page,
                )
                await process_response(response)
            case "ap":
                response = mistapi.api.v1.sites.insights.getSiteInsightMetricsForDevice(
                    apisession,
                    site_id=str(site_id),
                    device_mac=str(mac),
                    metric=str(metric),
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    duration=str(duration) if duration else None,
                    interval=str(interval) if interval else None,
                    limit=limit,
                    page=page,
                )
                await process_response(response)
            case "gateway":
                response = (
                    mistapi.api.v1.sites.insights.getSiteInsightMetricsForGateway(
                        apisession,
                        site_id=str(site_id),
                        device_id=str(device_id),
                        metrics=str(metric),
                        start=str(start) if start else None,
                        end=str(end) if end else None,
                        duration=str(duration) if duration else None,
                        interval=str(interval) if interval else None,
                        limit=limit,
                        page=page,
                    )
                )
                await process_response(response)
            case "mxedge":
                response = mistapi.api.v1.sites.insights.getSiteInsightMetricsForMxEdge(
                    apisession,
                    site_id=str(site_id),
                    device_mac=str(mac),
                    metric=str(metric),
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    duration=str(duration) if duration else None,
                    interval=str(interval) if interval else None,
                    limit=limit,
                    page=page,
                )
                await process_response(response)
            case "switch":
                response = mistapi.api.v1.sites.insights.getSiteInsightMetricsForSwitch(
                    apisession,
                    site_id=str(site_id),
                    device_mac=str(mac),
                    metric=str(metric),
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    duration=str(duration) if duration else None,
                    interval=str(interval) if interval else None,
                    limit=limit,
                    page=page,
                )
                await process_response(response)
            case _:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Object_type]}",
                    }
                )
    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)
    return format_response(response, response_format)


class Rrm_info_type(Enum):
    CHANNEL_SCORES = "channel_scores"
    CURRENT_CHANNEL_PLANNING = "current_channel_planning"
    CURRENT_RRM_CONSIDERATIONS = "current_rrm_considerations"
    CURRENT_RRM_NEIGHBORS = "current_rrm_neighbors"
    EVENTS = "events"


class Band(Enum):
    B24 = "24"
    B5 = "5"
    B5_DEDICATED = "5_dedicated"
    B5_SELECTABLE = "5_selectable"
    B6 = "6"
    B6_DEDICATED = "6_dedicated"
    B6_SELECTABLE = "6_selectable"


async def get_site_rrm_info(
    site_id: Annotated[UUID, Field(description="Site ID")],
    rrm_info_type: Annotated[
        Rrm_info_type,
        Field(
            description="Type of RRM information to retrieve: current_channel_planning returns the current channel plan for the site; current_rrm_considerations returns per-AP RRM considerations (requires device_id and band); current_rrm_neighbors lists current RRM neighbor APs for a band (requires band); events lists RRM change events over a time range"
        ),
    ],
    device_id: Annotated[
        UUID,
        Field(
            description="ID of the AP to retrieve RRM considerations for. Required when rrm_info_type is current_rrm_considerations",
            default=None,
        ),
    ],
    band: Annotated[
        Band,
        Field(
            description="802.11 band. Required when rrm_info_type is current_rrm_considerations or current_rrm_neighbors",
            default=None,
        ),
    ],
    start: Annotated[
        int, Field(description="Start of time range (epoch seconds)", default=None)
    ],
    end: Annotated[
        int, Field(description="End of time range (epoch seconds)", default=None)
    ],
    duration: Annotated[
        str, Field(description="Time range duration (e.g. 1d, 1h, 10m)", default=None)
    ],
    limit: Annotated[
        int, Field(description="Max number of results per page", default=200)
    ] = 200,
    page: Annotated[
        int, Field(description="Page number for pagination", default=1)
    ] = 1,
) -> dict | list | str:
    """Retrieve Radio Resource Management (RRM) information for a site. Use current_channel_planning to get the current channel plan, current_rrm_considerations to get RRM considerations for a specific device and band, current_rrm_neighbors to list current RRM neighbor APs for a band, or events to list RRM change events over a time range."""
    logger.debug("Tool get_site_rrm_info called")
    logger.debug(
        "Input Parameters: site_id: %s, rrm_info_type: %s, device_id: %s, band: %s, start: %s, end: %s, duration: %s, limit: %s, page: %s",
        site_id,
        rrm_info_type,
        device_id,
        band,
        start,
        end,
        duration,
        limit,
        page,
    )
    apisession, response_format = await get_apisession()
    try:
        object_type = rrm_info_type
        if object_type.value == "current_rrm_considerations":
            if not device_id:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": '`device_id` parameter is required when `rrm_info_type` is "current_rrm_considerations".',
                    }
                )
        if object_type.value == "current_rrm_considerations":
            if not band:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": '`band` parameter is required when `rrm_info_type` is "current_rrm_considerations".',
                    }
                )
        if object_type.value == "current_rrm_neighbors":
            if not band:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": '`band` parameter is required when `rrm_info_type` is "current_rrm_neighbors".',
                    }
                )
        if object_type.value == "channel_scores":
            if not band:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": '`band` parameter is required when `rrm_info_type` is "channel_scores".',
                    }
                )
        if duration and rrm_info_type.value not in ["events"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`duration` parameter can only be used when `rrm_info_type` is "events".',
                }
            )
        if limit and rrm_info_type.value not in ["events"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`limit` parameter can only be used when `rrm_info_type` is "events".',
                }
            )
        if page and rrm_info_type.value not in ["events"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`page` parameter can only be used when `rrm_info_type` is "events".',
                }
            )
        match object_type.value:
            case "channel_scores":
                response = mistapi.api.v1.sites.rrm.getSiteChannelScores(
                    apisession,
                    site_id=str(site_id),
                    band=str(band.value),
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                )
                await process_response(response)
            case "current_channel_planning":
                response = mistapi.api.v1.sites.rrm.getSiteCurrentChannelPlanning(
                    apisession, site_id=str(site_id)
                )
                await process_response(response)
            case "current_rrm_considerations":
                response = mistapi.api.v1.sites.rrm.getSiteCurrentRrmConsiderations(
                    apisession,
                    site_id=str(site_id),
                    device_id=str(device_id),
                    band=str(band.value),
                )
                await process_response(response)
            case "current_rrm_neighbors":
                response = mistapi.api.v1.sites.rrm.listSiteCurrentRrmNeighbors(
                    apisession, site_id=str(site_id), band=str(band.value)
                )
                await process_response(response)
            case "events":
                response = mistapi.api.v1.sites.rrm.listSiteRrmEvents(
                    apisession,
                    site_id=str(site_id),
                    band=band.value if band else None,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    duration=duration if duration else None,
                    limit=limit,
                    page=page,
                )
                await process_response(response)
            case _:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Rrm_info_type]}",
                    }
                )
    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)
    return format_response(response, response_format)


InsightObjectType = Object_type
RrmInfoType = Rrm_info_type
RrmBand = Band

_GET_INSIGHT_METRICS = internal_tool(get_insight_metrics)
_GET_SITE_RRM_INFO = internal_tool(get_site_rrm_info)


@mcp.tool(
    name="mist_get_site_insights",
    description="""Get Mist insight metrics or Radio Resource Management information for a site.

Provide `site_id` for every insight type. For `insight_type=metric`, provide
`object_type` and `metric`. Site metrics need no
object identifier; client, AP, Mist Edge, and switch metrics require `mac`; gateway
metrics require `device_id`. Use `mist_describe(subject=constant,
name=insight_metrics)` to discover metric names. Time ranges accept start/end or a
relative `duration`, with optional `interval`, `page`, and `limit`.

For `insight_type=rrm`, provide `rrm_info_type`. `channel_scores` requires `band`;
`channel_scores` may also use `start` and `end`.
`current_channel_planning` needs no additional selector;
`current_rrm_considerations` requires `device_id` and `band`;
`current_rrm_neighbors` requires `band`; and `events` accepts band, time range,
duration, page, and limit. `duration`, `page`, and `limit` are event-only for RRM.
Paginated metric or RRM-event responses may return `next`.""",
    tags={"sites_insights"},
    annotations={
        "title": "Get site insights",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def get_site_insights(
    insight_type: Annotated[
        SiteInsightType, Field(description="Insight metric or RRM information.")
    ],
    site_id: Annotated[UUID, Field(description="Site ID.")],
    start: Annotated[
        int,
        Field(description="Start time in epoch seconds.", default=None),
    ] = None,
    end: Annotated[
        int, Field(description="End time in epoch seconds.", default=None)
    ] = None,
    duration: Annotated[
        str, Field(description="Relative time range such as 1h or 1d.", default=None)
    ] = None,
    object_type: Annotated[
        InsightObjectType,
        Field(
            description="Metric object type: site, client, ap, gateway, mxedge, or switch.",
            default=None,
        ),
    ] = None,
    metric: Annotated[
        str,
        Field(
            description="Insight metric name; discover values with mist_describe(subject=constant, name=insight_metrics).",
            default=None,
        ),
    ] = None,
    mac: Annotated[
        str,
        Field(
            description="Client or device MAC required by applicable metric types.",
            default=None,
        ),
    ] = None,
    device_id: Annotated[
        UUID,
        Field(
            description="Gateway ID for gateway metrics, or AP ID for RRM considerations.",
            default=None,
        ),
    ] = None,
    interval: Annotated[
        str,
        Field(
            description="Metric aggregation interval such as 10m, 1h, or 1d.",
            default=None,
        ),
    ] = None,
    rrm_info_type: Annotated[
        RrmInfoType,
        Field(description="RRM information to retrieve.", default=None),
    ] = None,
    band: Annotated[
        RrmBand,
        Field(
            description="RRM radio band, including selectable/dedicated variants.",
            default=None,
        ),
    ] = None,
    page: Annotated[
        int, Field(description="Page number when supported.", default=None)
    ] = None,
    limit: Annotated[
        int, Field(description="Maximum results per page.", default=None)
    ] = None,
) -> ToolResult:
    if insight_type is SiteInsightType.METRIC:
        if object_type is None or metric is None:
            raise ToolError(
                "object_type and metric are required for insight_type='metric'."
            )
        return await run_internal_tool(
            _GET_INSIGHT_METRICS,
            arguments(
                {
                    "site_id": site_id,
                    "object_type": object_type,
                    "metric": metric,
                    "mac": mac,
                    "device_id": device_id,
                    "start": start,
                    "end": end,
                    "duration": duration,
                    "interval": interval,
                    "page": page,
                    "limit": limit,
                }
            ),
        )
    if rrm_info_type is None:
        raise ToolError("rrm_info_type is required for insight_type='rrm'.")
    if rrm_info_type is not RrmInfoType.EVENTS:
        unsupported = [
            name
            for name, value in {
                "duration": duration,
                "limit": limit,
                "page": page,
            }.items()
            if value is not None
        ]
        if unsupported:
            raise ToolError(
                f"{', '.join(unsupported)} can only be used with rrm_info_type='events'."
            )
        # The generated handler defaults these event-only fields to non-zero values;
        # explicitly disable them for non-event RRM operations.
        limit = 0
        page = 0
    return await run_internal_tool(
        _GET_SITE_RRM_INFO,
        arguments(
            {
                "site_id": site_id,
                "rrm_info_type": rrm_info_type,
                "device_id": device_id,
                "band": band,
                "start": start,
                "end": end,
                "duration": duration,
                "page": page,
                "limit": limit,
            }
        ),
    )
