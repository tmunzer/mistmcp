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


mcp = get_mcp()

if not mcp:
    raise RuntimeError(
        "MCP instance not found. Make sure to initialize the MCP server before defining tools."
    )


@mcp.tool(
    enabled=True,
    name="getOrgMxEdgeStats",
    description="""Get Org MxEdge Details Stats""",
    tags={"orgs_stats"},
    annotations={
        "title": "getOrgMxEdgeStats",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getOrgMxEdgeStats(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    mxedge_id: Annotated[UUID, Field(description="""ID of the Mist Mxedge""")],
    for_site: Optional[bool | None] = None,
) -> dict | list:
    """Get Org MxEdge Details Stats"""

    apisession = get_apisession()
    data = {}

    response = mistapi.api.v1.orgs.stats.getOrgMxEdgeStats(
        apisession,
        org_id=str(org_id),
        mxedge_id=str(mxedge_id),
        for_site=for_site if for_site else None,
    )
    await process_response(response)

    data = response.data

    return data
