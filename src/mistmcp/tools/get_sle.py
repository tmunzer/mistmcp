"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import mistapi
from fastmcp.exceptions import ToolError
from mistmcp.request_processor import get_apisession
from mistmcp.response_processor import process_response, handle_network_error
from mistmcp.response_formatter import format_response
from mistmcp.server import mcp
from mistmcp.logger import logger

from pydantic import Field
from typing import Annotated
from uuid import UUID
from enum import Enum


class SleScope(Enum):
    ORG = "org"
    ORG_SITES = "org_sites"
    SITE = "site"
    SITE_METRICS = "site_metrics"
    SITE_CLASSIFIERS = "site_classifiers"


class OrgSitesSle(Enum):
    WIFI = "wifi"
    WIRED = "wired"
    WAN = "wan"


class SiteSleScope(Enum):
    CLIENT = "client"
    AP = "ap"
    GATEWAY = "gateway"
    MXEDGE = "mxedge"
    SWITCH = "switch"
    SITE = "site"


class ObjectType(Enum):
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
    name="mist_get_sle",
    description="""Get SLE (Service Level Expectation) data at different scopes.
Use `sle_scope=org` with `org_id` and `metric` to get org-level SLE rollups such as all sites, worst sites, and Mx Edges. The optional `sle` parameter narrows the org query to a specific SLE name.
Use `sle_scope=org_sites` with `org_id` and `sle=wifi|wired|wan` to get per-site SLE summaries for an organization.
Use `sle_scope=site_metrics` with `site_id`, `scope`, and `scope_id` to discover metric names for one site-level object or scope.
Use `sle_scope=site_classifiers` with `site_id`, `scope`, `scope_id`, and `metric` to list classifier names for a site-level metric.
Use `sle_scope=site` with `site_id`, `scope`, `scope_id`, `metric`, and `object_type` to get detailed site-level SLE data such as summaries, trends, impacted objects, histograms, thresholds, or classifier trends.
For site-level SLE queries, call `sle_scope=site_metrics` first when you do not already know the metric name.""",
    tags={"sles"},
    annotations={
        "title": "Get SLE",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def get_sle(
    sle_scope: Annotated[
        SleScope,
        Field(
            description="""Scope of the SLE query. `org`: org-level SLEs; `org_sites`: SLE summary for all sites in the org; `site`: detailed site-level SLE data; `site_metrics`: list available SLE metrics for a site scope; `site_classifiers`: list classifiers for a specific metric"""
        ),
    ],
    org_id: Annotated[
        UUID,
        Field(
            description="""Organization ID. Required when sle_scope is `org` or `org_sites`""",
            default=None,
        ),
    ],
    site_id: Annotated[
        UUID,
        Field(
            description="""Site ID. Required when sle_scope is `site`, `site_metrics`, or `site_classifiers`""",
            default=None,
        ),
    ],
    metric: Annotated[
        str,
        Field(
            description="""SLE metric name. Required when sle_scope is `org`, `site`, or `site_classifiers`. For site-level queries, use `sle_scope=site_metrics` to discover metric names for the selected `scope` and `scope_id`. For org-level queries, use `mist_get_insight_metrics` or `mist_get_constants` with `object_type=insight_metrics` to discover available values""",
            default=None,
        ),
    ],
    sle: Annotated[
        str,
        Field(
            description="""SLE type. When sle_scope is `org`: SLE name to filter on (use `mist_get_insight_metrics` to discover available values). When sle_scope is `org_sites`: must be `wifi`, `wired`, or `wan`""",
            default=None,
        ),
    ],
    scope: Annotated[
        SiteSleScope,
        Field(
            description="""Site SLE scope. Required when sle_scope is `site`, `site_metrics`, or `site_classifiers`. For `sle_scope=site`, can be `client`, `ap`, `gateway`, `mxedge`, `switch`, or `site`. For `sle_scope=site_metrics` or `site_classifiers`, can be `client`, `ap`, `gateway`, `switch`, or `site`""",
            default=None,
        ),
    ],
    scope_id: Annotated[
        str,
        Field(
            description="""ID of the scoped object. Required when sle_scope is `site`, `site_metrics`, or `site_classifiers`. Use `site_id` if `scope=site`; `device_id` if `scope=ap`, `switch`, `gateway`, or `mxedge`; `MAC address` if `scope=client`""",
            default=None,
        ),
    ],
    object_type: Annotated[
        ObjectType,
        Field(
            description="""Type of SLE data to retrieve. Required when sle_scope is `site`""",
            default=None,
        ),
    ],
    start: Annotated[
        int, Field(description="""Start of time range (epoch seconds)""", default=None)
    ],
    end: Annotated[
        int, Field(description="""End of time range (epoch seconds)""", default=None)
    ],
    classifier: Annotated[
        str,
        Field(
            description="""Classifier name. Required when sle_scope is `site` and object_type is `classifier_summary_trend`""",
            default=None,
        ),
    ],
    duration: Annotated[
        str,
        Field(
            description="""Time range duration (e.g. 1d, 1h, 10m). Only used when sle_scope is `site`""",
            default=None,
        ),
    ],
    limit: Annotated[
        int,
        Field(
            description="""Max number of results per page. Only used when sle_scope is `org_sites`""",
            default=20,
        ),
    ] = 20,
) -> dict | list | str:
    """Get SLE data at org, org_sites, site, site_metrics, or site_classifiers scope."""

    logger.debug("Tool get_sle called")
    logger.debug(
        "Input Parameters: sle_scope: %s, org_id: %s, site_id: %s, metric: %s, sle: %s, scope: %s, scope_id: %s, object_type: %s, start: %s, end: %s, limit: %s, classifier: %s, duration: %s",
        sle_scope,
        org_id,
        site_id,
        metric,
        sle,
        scope,
        scope_id,
        object_type,
        start,
        end,
        limit,
        classifier,
        duration,
    )

    apisession, response_format = await get_apisession()

    try:
        match sle_scope:
            case SleScope.ORG:
                if not org_id:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": "`org_id` is required when `sle_scope` is `org`.",
                        }
                    )
                if not metric:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": "`metric` is required when `sle_scope` is `org`.",
                        }
                    )
                response = mistapi.api.v1.orgs.insights.getOrgSle(
                    apisession,
                    org_id=str(org_id),
                    metric=str(metric),
                    sle=str(sle) if sle else None,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                )
                await process_response(response)

            case SleScope.ORG_SITES:
                if not org_id:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": "`org_id` is required when `sle_scope` is `org_sites`.",
                        }
                    )
                if not sle:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": "`sle` is required when `sle_scope` is `org_sites`. Must be `wifi`, `wired`, or `wan`.",
                        }
                    )
                sle_value = sle
                valid_sle_values = [e.value for e in OrgSitesSle]
                if sle_value not in valid_sle_values:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": f"Invalid `sle` value: {sle_value}. Must be one of: {valid_sle_values}",
                        }
                    )
                response = mistapi.api.v1.orgs.insights.getOrgSitesSle(
                    apisession,
                    org_id=str(org_id),
                    sle=sle_value,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    limit=limit,
                )
                await process_response(response)

            case SleScope.SITE:
                if not site_id:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": "`site_id` is required when `sle_scope` is `site`.",
                        }
                    )
                if not scope:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": "`scope` is required when `sle_scope` is `site`.",
                        }
                    )
                if not scope_id:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": "`scope_id` is required when `sle_scope` is `site`.",
                        }
                    )
                if not metric:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": "`metric` is required when `sle_scope` is `site`.",
                        }
                    )
                if not object_type:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": "`object_type` is required when `sle_scope` is `site`.",
                        }
                    )

                if object_type == ObjectType.CLASSIFIER_SUMMARY_TREND:
                    if not classifier:
                        raise ToolError(
                            {
                                "status_code": 400,
                                "message": "`classifier` parameter is required when `object_type` is `classifier_summary_trend`.",
                            }
                        )

                match object_type:
                    case ObjectType.IMPACT_SUMMARY:
                        response = mistapi.api.v1.sites.sle.getSiteSleImpactSummary(
                            apisession,
                            site_id=str(site_id),
                            scope=scope.value,
                            scope_id=scope_id,
                            metric=metric,
                            start=str(start) if start else None,
                            end=str(end) if end else None,
                            duration=duration if duration else None,
                        )
                    case ObjectType.SUMMARY_TREND:
                        response = mistapi.api.v1.sites.sle.getSiteSleSummaryTrend(
                            apisession,
                            site_id=str(site_id),
                            scope=scope.value,
                            scope_id=scope_id,
                            metric=metric,
                            start=str(start) if start else None,
                            end=str(end) if end else None,
                            duration=duration if duration else None,
                        )
                    case ObjectType.IMPACTED_APPLICATIONS:
                        response = (
                            mistapi.api.v1.sites.sle.listSiteSleImpactedApplications(
                                apisession,
                                site_id=str(site_id),
                                scope=scope.value,
                                scope_id=scope_id,
                                metric=metric,
                                start=str(start) if start else None,
                                end=str(end) if end else None,
                                duration=duration if duration else None,
                            )
                        )
                    case ObjectType.IMPACTED_APS:
                        response = mistapi.api.v1.sites.sle.listSiteSleImpactedAps(
                            apisession,
                            site_id=str(site_id),
                            scope=scope.value,
                            scope_id=scope_id,
                            metric=metric,
                            start=str(start) if start else None,
                            end=str(end) if end else None,
                            duration=duration if duration else None,
                        )
                    case ObjectType.IMPACTED_GATEWAYS:
                        response = mistapi.api.v1.sites.sle.listSiteSleImpactedGateways(
                            apisession,
                            site_id=str(site_id),
                            scope=scope.value,
                            scope_id=scope_id,
                            metric=metric,
                            start=str(start) if start else None,
                            end=str(end) if end else None,
                            duration=duration if duration else None,
                        )
                    case ObjectType.IMPACTED_INTERFACES:
                        response = (
                            mistapi.api.v1.sites.sle.listSiteSleImpactedInterfaces(
                                apisession,
                                site_id=str(site_id),
                                scope=scope.value,
                                scope_id=scope_id,
                                metric=metric,
                                start=str(start) if start else None,
                                end=str(end) if end else None,
                                duration=duration if duration else None,
                            )
                        )
                    case ObjectType.IMPACTED_SWITCHES:
                        response = mistapi.api.v1.sites.sle.listSiteSleImpactedSwitches(
                            apisession,
                            site_id=str(site_id),
                            scope=scope.value,
                            scope_id=scope_id,
                            metric=metric,
                            start=str(start) if start else None,
                            end=str(end) if end else None,
                            duration=duration if duration else None,
                        )
                    case ObjectType.IMPACTED_WIRELESS_CLIENTS:
                        response = (
                            mistapi.api.v1.sites.sle.listSiteSleImpactedWirelessClients(
                                apisession,
                                site_id=str(site_id),
                                scope=scope.value,
                                scope_id=scope_id,
                                metric=metric,
                                start=str(start) if start else None,
                                end=str(end) if end else None,
                                duration=duration if duration else None,
                            )
                        )
                    case ObjectType.IMPACTED_WIRED_CLIENTS:
                        response = (
                            mistapi.api.v1.sites.sle.listSiteSleImpactedWiredClients(
                                apisession,
                                site_id=str(site_id),
                                scope=scope.value,
                                scope_id=scope_id,
                                metric=metric,
                                start=str(start) if start else None,
                                end=str(end) if end else None,
                                duration=duration if duration else None,
                            )
                        )
                    case ObjectType.IMPACTED_CHASSIS:
                        response = mistapi.api.v1.sites.sle.listSiteSleImpactedChassis(
                            apisession,
                            site_id=str(site_id),
                            scope=scope.value,
                            scope_id=scope_id,
                            metric=metric,
                            start=str(start) if start else None,
                            end=str(end) if end else None,
                            duration=duration if duration else None,
                        )
                    case ObjectType.HISTOGRAM:
                        response = mistapi.api.v1.sites.sle.getSiteSleHistogram(
                            apisession,
                            site_id=str(site_id),
                            scope=scope.value,
                            scope_id=scope_id,
                            metric=metric,
                            start=str(start) if start else None,
                            end=str(end) if end else None,
                            duration=duration if duration else None,
                        )
                    case ObjectType.CLASSIFIER_SUMMARY_TREND:
                        response = (
                            mistapi.api.v1.sites.sle.getSiteSleClassifierSummaryTrend(
                                apisession,
                                site_id=str(site_id),
                                scope=scope.value,
                                scope_id=scope_id,
                                metric=metric,
                                classifier=classifier,
                                start=str(start) if start else None,
                                end=str(end) if end else None,
                                duration=duration if duration else None,
                            )
                        )
                    case ObjectType.THRESHOLD:
                        response = mistapi.api.v1.sites.sle.getSiteSleThreshold(
                            apisession,
                            site_id=str(site_id),
                            scope=scope.value,
                            scope_id=scope_id,
                            metric=metric,
                        )
                    case _:
                        raise ToolError(
                            {
                                "status_code": 400,
                                "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in ObjectType]}",
                            }
                        )
                await process_response(response)

            case SleScope.SITE_METRICS:
                if not site_id:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": "`site_id` is required when `sle_scope` is `site_metrics`.",
                        }
                    )
                if not scope:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": "`scope` is required when `sle_scope` is `site_metrics`.",
                        }
                    )
                if scope == SiteSleScope.MXEDGE:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": "`scope=mxedge` is not supported when `sle_scope` is `site_metrics`. Use `ap`, `client`, `gateway`, `switch`, or `site`.",
                        }
                    )
                if not scope_id:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": "`scope_id` is required when `sle_scope` is `site_metrics`.",
                        }
                    )
                response = mistapi.api.v1.sites.sle.listSiteSlesMetrics(
                    apisession,
                    site_id=str(site_id),
                    scope=scope.value,
                    scope_id=scope_id,
                )
                await process_response(response)

            case SleScope.SITE_CLASSIFIERS:
                if not site_id:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": "`site_id` is required when `sle_scope` is `site_classifiers`.",
                        }
                    )
                if not scope:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": "`scope` is required when `sle_scope` is `site_classifiers`.",
                        }
                    )
                if scope == SiteSleScope.MXEDGE:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": "`scope=mxedge` is not supported when `sle_scope` is `site_classifiers`. Use `ap`, `client`, `gateway`, `switch`, or `site`.",
                        }
                    )
                if not scope_id:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": "`scope_id` is required when `sle_scope` is `site_classifiers`.",
                        }
                    )
                if not metric:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": "`metric` is required when `sle_scope` is `site_classifiers`. Use `sle_scope=site_metrics` first to discover available metric names.",
                        }
                    )
                response = mistapi.api.v1.sites.sle.listSiteSleMetricClassifiers(
                    apisession,
                    site_id=str(site_id),
                    scope=scope.value,
                    scope_id=scope_id,
                    metric=metric,
                )
                await process_response(response)

            case _:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": f"Invalid sle_scope: {sle_scope.value}. Valid values are: {[e.value for e in SleScope]}",
                    }
                )

    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
