"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import mistapi
from fastmcp import Context
from fastmcp.exceptions import ToolError
from mistmcp.request_processor import get_apisession
from mistmcp.response_processor import process_response, handle_network_error
from mistmcp.response_formatter import format_response
from mistmcp.server import mcp
from mistmcp.logger import logger

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID


@mcp.tool(
    name="mist_get_org_sle",
    description="""Get Org SLEs (all/worst sites, Mx Edges, ...). Use the `mist_get_insight_metrics` tool to get the list of available SLE metrics""",
    tags={"sles"},
    annotations={
        "title": "Get org sle",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def get_org_sle(
    org_id: Annotated[UUID, Field(description="""Organization ID""")],
    metric: Annotated[
        str,
        Field(
            description="""Metric to look at. Use the `mist_get_insight_metrics` tool to get the list of available SLE metrics"""
        ),
    ],
    sle: Annotated[
        Optional[str],
        Field(
            description="""Type of SLE data to retrieve for the organization sites. Use the `mist_get_insight_metrics` tool to get the list of available SLE metrics"""
        ),
    ],
    start: Annotated[
        Optional[int], Field(description="""Start of time range (epoch seconds)""")
    ],
    end: Annotated[
        Optional[int], Field(description="""End of time range (epoch seconds)""")
    ],
    limit: Annotated[
        int, Field(description="""Max number of results per page""", default=20)
    ] = 20,
) -> dict | list | str:
    """Get Org SLEs (all/worst sites, Mx Edges, ...). Use the `mist_get_insight_metrics` tool to get the list of available SLE metrics"""

    logger.debug("Tool get_org_sle called")

    apisession, response_format = await get_apisession()

    try:
        response = mistapi.api.v1.orgs.insights.getOrgSle(
            apisession,
            org_id=str(org_id),
            metric=str(metric),
            sle=str(sle) if sle else None,
            start=str(start) if start else None,
            end=str(end) if end else None,
            limit=limit,
        )
        await process_response(response)
    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
