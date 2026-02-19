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


class Device_type(Enum):
    ALL = "all"
    AP = "ap"
    GATEWAY = "gateway"
    SWITCH = "switch"


@mcp.tool(
    name="searchOrgDeviceEvents",
    description="""Search Org Devices Events""",
    tags={"devices"},
    annotations={
        "title": "searchOrgDeviceEvents",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchOrgDeviceEvents(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    mac: Annotated[Optional[str | None], Field(description="""Device mac""")] = None,
    model: Annotated[
        Optional[str | None], Field(description="""Device model""")
    ] = None,
    device_type: Optional[Device_type | None] = Device_type.AP,
    text: Annotated[
        Optional[str | None], Field(description="""Event message""")
    ] = None,
    timestamp: Annotated[
        Optional[str | None], Field(description="""Event time""")
    ] = None,
    type: Annotated[
        Optional[str | None],
        Field(
            description="""See [List Device Events Definitions](/#operations/listDeviceEventsDefinitions)"""
        ),
    ] = None,
    last_by: Annotated[
        Optional[str | None],
        Field(description="""Return last/recent event for passed in field"""),
    ] = None,
    includes: Annotated[
        Optional[str | None],
        Field(
            description="""Keyword to include events from additional indices (e.g. ext_tunnel for prisma events)"""
        ),
    ] = None,
    limit: Optional[int | None] = None,
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
    sort: Annotated[
        Optional[str | None],
        Field(
            description="""On which field the list should be sorted, -prefix represents DESC order"""
        ),
    ] = None,
    search_after: Annotated[
        Optional[str | None],
        Field(
            description="""Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed."""
        ),
    ] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """Search Org Devices Events"""

    apisession, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.orgs.devices.searchOrgDeviceEvents(
        apisession,
        org_id=str(org_id),
        mac=mac if mac else None,
        model=model if model else None,
        device_type=device_type.value if device_type else Device_type.AP.value,
        text=text if text else None,
        timestamp=timestamp if timestamp else None,
        type=type if type else None,
        last_by=last_by if last_by else None,
        includes=includes if includes else None,
        limit=limit if limit else None,
        start=start if start else None,
        end=end if end else None,
        duration=duration if duration else None,
        sort=sort if sort else None,
        search_after=search_after if search_after else None,
    )
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
