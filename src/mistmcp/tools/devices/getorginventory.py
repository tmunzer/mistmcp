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
    SWITCH = "switch"
    GATEWAY = "gateway"


@mcp.tool(
    name="getOrgInventory",
    description="""Retrieve the inventory of devices. This tool provides a consolidated view of all devices within an organization, allowing users to easily access and manage their network inventory""",
    tags={"devices"},
    annotations={
        "title": "getOrgInventory",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getOrgInventory(
    org_id: Annotated[UUID, Field(description="""Organization ID""")],
    site_id: Annotated[Optional[UUID | None], Field(description="""Site ID""")] = None,
    serial: Annotated[
        Optional[str | None],
        Field(description="""Serial number of the device to filter inventory by"""),
    ] = None,
    model: Annotated[
        Optional[str | None],
        Field(description="""Model of the device to filter inventory by"""),
    ] = None,
    mac: Annotated[
        Optional[str | None],
        Field(description="""MAC address of the device to filter inventory by"""),
    ] = None,
    vc: Annotated[
        Optional[bool | None],
        Field(description="""To display Virtual Chassis members"""),
    ] = None,
    device_type: Annotated[
        Optional[Device_type | None],
        Field(description="""Type of the device to filter inventory by"""),
    ] = None,
    limit: Annotated[
        int, Field(description="""Max number of results per page""", default=10)
    ] = 10,
    ctx: Context | None = None,
) -> dict | list | str:
    """Retrieve the inventory of devices. This tool provides a consolidated view of all devices within an organization, allowing users to easily access and manage their network inventory"""

    logger.debug("Tool getOrgInventory called")

    apisession, response_format = get_apisession()

    response = mistapi.api.v1.orgs.inventory.getOrgInventory(
        apisession,
        org_id=str(org_id),
        serial=serial if serial else None,
        model=model if model else None,
        type=device_type.value if device_type else None,
        mac=mac if mac else None,
        site_id=str(site_id) if site_id else None,
        vc=vc if vc else None,
        limit=limit,
    )
    await process_response(response)

    return format_response(response, response_format)
