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


class Device_type(Enum):
    AP = "ap"
    GATEWAY = "gateway"
    SWITCH = "switch"
    MXEDGE = "mxedge"


@mcp.tool(
    name="searchSiteDeviceLastConfigs",
    description="""Search Device Last Configs""",
    tags={"devices"},
    annotations={
        "title": "searchSiteDeviceLastConfigs",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchSiteDeviceLastConfigs(
    site_id: Annotated[UUID, Field(description="""Site ID""")],
    cert_expiry_duration: Annotated[
        Optional[str | None],
        Field(
            description="""Duration for expiring cert queries (format: 2d/3h/172800 seconds)"""
        ),
    ] = None,
    device_type: Optional[Device_type | None] = Device_type.AP,
    mac: Optional[str | None] = None,
    version: Optional[str | None] = None,
    name: Optional[str | None] = None,
    limit: Annotated[
        int, Field(description="""Max number of results per page""", default=100)
    ] = 100,
    start: Annotated[
        Optional[str | None],
        Field(description="""Start of time range (epoch seconds)"""),
    ] = None,
    end: Annotated[
        Optional[str | None], Field(description="""End of time range (epoch seconds)""")
    ] = None,
    duration: Annotated[
        Optional[str | None],
        Field(description="""Time range duration (e.g. 1d, 1h, 10m)"""),
    ] = None,
    sort: Annotated[Optional[str | None], Field(description="""Sort field""")] = None,
    search_after: Annotated[
        Optional[str | None],
        Field(
            description="""Pagination cursor from '_next' URL of previous response"""
        ),
    ] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """Search Device Last Configs"""

    logger.debug("Tool searchSiteDeviceLastConfigs called")

    apisession, response_format = get_apisession()

    response = mistapi.api.v1.sites.devices.searchSiteDeviceLastConfigs(
        apisession,
        site_id=str(site_id),
        cert_expiry_duration=cert_expiry_duration if cert_expiry_duration else None,
        device_type=device_type.value if device_type else Device_type.AP.value,
        mac=mac if mac else None,
        version=version if version else None,
        name=name if name else None,
        limit=limit,
        start=start if start else None,
        end=end if end else None,
        duration=duration if duration else None,
        sort=sort if sort else None,
        search_after=search_after if search_after else None,
    )
    await process_response(response)

    return format_response(response, response_format)
