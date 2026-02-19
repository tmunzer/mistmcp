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


class Type(Enum):
    ALL = "all"
    AP = "ap"
    GATEWAY = "gateway"
    SWITCH = "switch"


class Status(Enum):
    ALL = "all"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


@mcp.tool(
    name="listOrgDevicesStats",
    description="""Get List of Org Devices statsThis API renders some high-level device stats, pagination is assumed and returned in response header (as the response is an array)""",
    tags={"orgs_stats"},
    annotations={
        "title": "listOrgDevicesStats",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def listOrgDevicesStats(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    type: Optional[Type | None] = Type.AP,
    status: Optional[Status | None] = Status.ALL,
    site_id: Annotated[
        Optional[str | None], Field(description="""ID of the Mist Site""")
    ] = None,
    mac: Optional[str | None] = None,
    evpntopo_id: Annotated[
        Optional[str | None], Field(description="""EVPN Topology ID""")
    ] = None,
    evpn_unused: Annotated[
        Optional[str | None],
        Field(
            description="""If `evpn_unused`==`true`, find EVPN eligible switches which don’t belong to any EVPN Topology yet"""
        ),
    ] = None,
    fields: Annotated[
        Optional[str | None],
        Field(
            description="""List of additional fields requests, comma separated, or `fields=*` for all of them"""
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
    limit: Optional[int | None] = None,
    page: Annotated[Optional[int | None], Field(ge=1)] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """Get List of Org Devices statsThis API renders some high-level device stats, pagination is assumed and returned in response header (as the response is an array)"""

    apisession, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.orgs.stats.listOrgDevicesStats(
        apisession,
        org_id=str(org_id),
        type=type.value if type else Type.AP.value,
        status=status.value if status else Status.ALL.value,
        site_id=site_id if site_id else None,
        mac=mac if mac else None,
        evpntopo_id=evpntopo_id if evpntopo_id else None,
        evpn_unused=evpn_unused if evpn_unused else None,
        fields=fields if fields else None,
        start=start if start else None,
        end=end if end else None,
        duration=duration if duration else None,
        limit=limit if limit else None,
        page=page if page else None,
    )
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
