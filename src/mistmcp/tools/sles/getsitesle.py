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
from uuid import UUID
from enum import Enum


class Scope(Enum):
    CLIENT = "client"
    AP = "ap"
    GATEWAY = "gateway"
    MXEDGE = "mxedge"
    SWITCH = "switch"
    SITE = "site"


class Object_type(Enum):
    SUMMARY = "summary"
    IMPACT_SUMMARY = "impact_summary"
    SUMMARY_TREND = "summary_trend"
    IMPACTED_APPLICATIONS = "impacted_applications"
    IMPACTED_APS = "impacted_aps"
    IMPACTED_GATEWAYS = "impacted_gateways"
    IMPACTED_INTERFACES = "impacted_interfaces"
    IMPACTED_SWITCHES = "impacted_switches"
    IMPACTED_WIRELESS_CLIENTS = "impacted_wireless_clients"
    IMPACTED_WIRED_CLIENTS = "impacted_wired_clients"
    IMPACTED_CHASSIS = "impacted_chassis"
    HISTOGRAM = "histogram"
    CLASSIFIER_SUMMARY_TREND = "classifier_summary_trend"
    THRESHOLD = "threshold"


@mcp.tool(
    name="getSiteSle",
    description="""Provides Information about the Service Level Expectations (SLEs) for a given site. The SLEs are derived from the insight metrics and can be used to monitor the network user experience of the site against the defined SLEs.""",
    tags={"sles"},
    annotations={
        "title": "getSiteSle",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getSiteSle(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    scope: Annotated[
        Scope,
        Field(
            description="""Scope of the SLEs to retrieve. Can be 'client', 'ap', 'gateway', 'mxedge', 'switch' or 'site'."""
        ),
    ],
    scope_id: Annotated[str, Field(description="""ID of the Mist Scope""")],
    metric: Annotated[
        str,
        Field(
            description="""Name of the metric to retrieve SLEs for. Use the tool `listSiteInsightMetrics` to see available metrics."""
        ),
    ],
    object_type: Annotated[
        Object_type, Field(description="""Type of object to retrieve metrics for.""")
    ],
    start: Annotated[
        Optional[str | None],
        Field(
            description="""Start time (epoch timestamp in seconds, or relative string like '-1d', '-1w', 'now')"""
        ),
    ] = None,
    end: Annotated[
        Optional[str | None],
        Field(
            description="""End time (epoch timestamp in seconds, or relative string like '-1d', '-2h', 'now')"""
        ),
    ] = None,
    classifier: Annotated[
        Optional[str | None],
        Field(
            description="""Classifier name. Required when object_type is 'classifier_summary_trend'."""
        ),
    ] = None,
    duration: Annotated[
        Optional[str | None], Field(description="""Duration like 7d, 2w""")
    ] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """Provides Information about the Service Level Expectations (SLEs) for a given site. The SLEs are derived from the insight metrics and can be used to monitor the network user experience of the site against the defined SLEs."""

    logger.debug("Tool getSiteSle called")

    apisession, response_format = get_apisession()
    data = {}

    object_type = object_type

    if object_type.value == "classifier_summary_trend":
        if not classifier:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`classifier` parameter is required when `object_type` is "classifier_summary_trend".',
                }
            )

    match object_type.value:
        case "summary":
            response = mistapi.api.v1.sites.sle.getSiteSleSummary(
                apisession,
                site_id=str(site_id),
                scope=scope.value,
                scope_id=scope_id,
                metric=metric,
                start=start if start else None,
                end=end if end else None,
                duration=duration if duration else None,
            )
            await process_response(response)
            data = response.data
        case "impact_summary":
            response = mistapi.api.v1.sites.sle.getSiteSleImpactSummary(
                apisession,
                site_id=str(site_id),
                scope=scope.value,
                scope_id=scope_id,
                metric=metric,
                start=start if start else None,
                end=end if end else None,
                duration=duration if duration else None,
            )
            await process_response(response)
            data = response.data
        case "summary_trend":
            response = mistapi.api.v1.sites.sle.getSiteSleSummaryTrend(
                apisession,
                site_id=str(site_id),
                scope=scope.value,
                scope_id=scope_id,
                metric=metric,
                start=start if start else None,
                end=end if end else None,
                duration=duration if duration else None,
            )
            await process_response(response)
            data = response.data
        case "impacted_applications":
            response = mistapi.api.v1.sites.sle.listSiteSleImpactedApplications(
                apisession,
                site_id=str(site_id),
                scope=scope.value,
                scope_id=scope_id,
                metric=metric,
                start=start if start else None,
                end=end if end else None,
                duration=duration if duration else None,
            )
            await process_response(response)
            data = response.data
        case "impacted_aps":
            response = mistapi.api.v1.sites.sle.listSiteSleImpactedAps(
                apisession,
                site_id=str(site_id),
                scope=scope.value,
                scope_id=scope_id,
                metric=metric,
                start=start if start else None,
                end=end if end else None,
                duration=duration if duration else None,
            )
            await process_response(response)
            data = response.data
        case "impacted_gateways":
            response = mistapi.api.v1.sites.sle.listSiteSleImpactedGateways(
                apisession,
                site_id=str(site_id),
                scope=scope.value,
                scope_id=scope_id,
                metric=metric,
                start=start if start else None,
                end=end if end else None,
                duration=duration if duration else None,
            )
            await process_response(response)
            data = response.data
        case "impacted_interfaces":
            response = mistapi.api.v1.sites.sle.listSiteSleImpactedInterfaces(
                apisession,
                site_id=str(site_id),
                scope=scope.value,
                scope_id=scope_id,
                metric=metric,
                start=start if start else None,
                end=end if end else None,
                duration=duration if duration else None,
            )
            await process_response(response)
            data = response.data
        case "impacted_switches":
            response = mistapi.api.v1.sites.sle.listSiteSleImpactedSwitches(
                apisession,
                site_id=str(site_id),
                scope=scope.value,
                scope_id=scope_id,
                metric=metric,
                start=start if start else None,
                end=end if end else None,
                duration=duration if duration else None,
            )
            await process_response(response)
            data = response.data
        case "impacted_wireless_clients":
            response = mistapi.api.v1.sites.sle.listSiteSleImpactedWirelessClients(
                apisession,
                site_id=str(site_id),
                scope=scope.value,
                scope_id=scope_id,
                metric=metric,
                start=start if start else None,
                end=end if end else None,
                duration=duration if duration else None,
            )
            await process_response(response)
            data = response.data
        case "impacted_wired_clients":
            response = mistapi.api.v1.sites.sle.listSiteSleImpactedWiredClients(
                apisession,
                site_id=str(site_id),
                scope=scope.value,
                scope_id=scope_id,
                metric=metric,
                start=start if start else None,
                end=end if end else None,
                duration=duration if duration else None,
            )
            await process_response(response)
            data = response.data
        case "impacted_chassis":
            response = mistapi.api.v1.sites.sle.listSiteSleImpactedChassis(
                apisession,
                site_id=str(site_id),
                scope=scope.value,
                scope_id=scope_id,
                metric=metric,
                start=start if start else None,
                end=end if end else None,
                duration=duration if duration else None,
            )
            await process_response(response)
            data = response.data
        case "histogram":
            response = mistapi.api.v1.sites.sle.getSiteSleHistogram(
                apisession,
                site_id=str(site_id),
                scope=scope.value,
                scope_id=scope_id,
                metric=metric,
                start=start if start else None,
                end=end if end else None,
                duration=duration if duration else None,
            )
            await process_response(response)
            data = response.data
        case "classifier_summary_trend":
            response = mistapi.api.v1.sites.sle.getSiteSleClassifierSummaryTrend(
                apisession,
                site_id=str(site_id),
                scope=scope.value,
                scope_id=scope_id,
                metric=metric,
                classifier=classifier,
                start=start if start else None,
                end=end if end else None,
                duration=duration if duration else None,
            )
            await process_response(response)
            data = response.data
        case "threshold":
            response = mistapi.api.v1.sites.sle.getSiteSleThreshold(
                apisession,
                site_id=str(site_id),
                scope=scope.value,
                scope_id=scope_id,
                metric=metric,
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
