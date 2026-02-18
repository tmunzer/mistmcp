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
from typing import Annotated
from uuid import UUID
from enum import Enum


mcp = get_mcp()

if not mcp:
    raise RuntimeError(
        "MCP instance not found. Make sure to initialize the MCP server before defining tools."
    )


class Scope(Enum):
    AP = "ap"
    CLIENT = "client"
    GATEWAY = "gateway"
    SITE = "site"
    SWITCH = "switch"


@mcp.tool(
    enabled=True,
    name="listSiteSlesMetrics",
    description="""List the metrics for the given scope""",
    tags={"sles"},
    annotations={
        "title": "listSiteSlesMetrics",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def listSiteSlesMetrics(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    scope: Scope,
    scope_id: Annotated[
        str,
        Field(
            description="""* site_id if `scope`==`site` * device_id if `scope`==`ap`, `scope`==`switch` or `scope`==`gateway` * mac if `scope`==`client`"""
        ),
    ],
) -> dict | list:
    """List the metrics for the given scope"""

    apisession = get_apisession()
    data = {}

    response = mistapi.api.v1.sites.sle.listSiteSlesMetrics(
        apisession,
        site_id=str(site_id),
        scope=scope.value,
        scope_id=scope_id if scope_id else None,
    )
    await process_response(response)

    data = response.data

    return data
