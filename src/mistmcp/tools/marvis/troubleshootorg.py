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


class Type(Enum):
    WAN = "wan"
    WIRED = "wired"
    WIRELESS = "wireless"
    NONE = None


@mcp.tool(
    name="troubleshootOrg",
    description="""Troubleshoot sites, devices, clients, and wired clients for maximum of last 7 days from current time. See search APIs for device information:- [search Device](/#operations/searchOrgDevices)- [search Wireless Client](/#operations/searchOrgWirelessClients)- [search Wired Client](/#operations/searchOrgWiredClients)- [search Wan Client](/#operations/searchOrgWanClients)**NOTE**: requires Marvis subscription license""",
    tags={"marvis"},
    annotations={
        "title": "troubleshootOrg",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def troubleshootOrg(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    mac: Annotated[
        Optional[str | None],
        Field(description="""**required** when troubleshooting device or a client"""),
    ] = None,
    site_id: Annotated[
        Optional[UUID | None],
        Field(description="""**required** when troubleshooting site"""),
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
    type: Annotated[
        Optional[Type | None],
        Field(
            description="""When troubleshooting site, type of network to troubleshoot"""
        ),
    ] = Type.NONE,
    ctx: Context | None = None,
) -> dict | list | str:
    """Troubleshoot sites, devices, clients, and wired clients for maximum of last 7 days from current time. See search APIs for device information:- [search Device](/#operations/searchOrgDevices)- [search Wireless Client](/#operations/searchOrgWirelessClients)- [search Wired Client](/#operations/searchOrgWiredClients)- [search Wan Client](/#operations/searchOrgWanClients)**NOTE**: requires Marvis subscription license"""

    logger.debug("Tool troubleshootOrg called")

    apisession, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.orgs.troubleshoot.troubleshootOrg(
        apisession,
        org_id=str(org_id),
        mac=mac if mac else None,
        site_id=str(site_id) if site_id else None,
        start=start if start else None,
        end=end if end else None,
        type=type.value if type else None,
    )
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
