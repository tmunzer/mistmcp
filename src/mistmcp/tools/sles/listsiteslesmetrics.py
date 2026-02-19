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
from typing import Annotated
from uuid import UUID
from enum import Enum


class Scope(Enum):
    AP = "ap"
    CLIENT = "client"
    GATEWAY = "gateway"
    SITE = "site"
    SWITCH = "switch"


@mcp.tool(
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
    ctx: Context | None = None,
) -> dict | list | str:
    """List the metrics for the given scope"""

    logger.debug("Tool listSiteSlesMetrics called")

    apisession, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.sites.sle.listSiteSlesMetrics(
        apisession,
        site_id=str(site_id),
        scope=scope.value,
        scope_id=scope_id if scope_id else None,
    )
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
