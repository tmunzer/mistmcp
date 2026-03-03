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
from uuid import UUID
from enum import Enum


class Query_type(Enum):
    METRICS = "metrics"
    CLASSIFIERS = "classifiers"


class Scope(Enum):
    AP = "ap"
    CLIENT = "client"
    GATEWAY = "gateway"
    SITE = "site"
    SWITCH = "switch"


@mcp.tool(
    name="mist_list_site_sle_info",
    description="""List SLE metadata for a site scope. Use metrics to list available SLE metrics for a given scope, or classifiers to list the classifiers available for a specific metric.""",
    tags={"sles"},
    annotations={
        "title": "List site sle info",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def list_site_sle_info(
    site_id: Annotated[UUID, Field(description="""Site ID""")],
    query_type: Annotated[
        Query_type,
        Field(
            description="""Type of metadata to retrieve: metrics returns the list of available SLE metrics for the given scope; classifiers returns the list of classifiers for a specific metric (requires metric parameter)"""
        ),
    ],
    scope: Annotated[
        Scope,
        Field(
            description="""Scope of the SLE data: site, ap, client, gateway, or switch"""
        ),
    ],
    scope_id: Annotated[
        str,
        Field(
            description="""ID of the scoped object: site_id if scope==site; device_id if scope==ap, switch, or gateway; MAC address if scope==client"""
        ),
    ],
    metric: Annotated[
        Optional[str | None],
        Field(
            description="""SLE metric name to retrieve classifiers for. Required when query_type is classifiers. Use query_type=metrics first to discover available metric names"""
        ),
    ] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """List SLE metadata for a site scope. Use metrics to list available SLE metrics for a given scope, or classifiers to list the classifiers available for a specific metric."""

    logger.debug("Tool list_site_sle_info called")

    apisession, response_format = get_apisession()

    object_type = query_type

    if object_type.value == "classifiers":
        if not metric:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`metric` parameter is required when `object_type` is "classifiers".',
                }
            )

    match object_type.value:
        case "metrics":
            response = mistapi.api.v1.sites.sle.listSiteSlesMetrics(
                apisession, site_id=str(site_id), scope=scope.value, scope_id=scope_id
            )
            await process_response(response)
        case "classifiers":
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
                    "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Query_type]}",
                }
            )

    return format_response(response, response_format)
