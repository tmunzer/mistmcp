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


class Device_type(Enum):
    AP = "ap"
    SWITCH = "switch"
    GATEWAY = "gateway"


@mcp.tool(
    name="getOrgInventory",
    description="""Retrieve the inventory of devices for a specified organization and optionally filter by site. This tool provides a consolidated view of all devices within an organization, allowing users to easily access and manage their network inventory.""",
    tags={"devices"},
    annotations={
        "title": "getOrgInventory",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getOrgInventory(
    org_id: Annotated[
        UUID, Field(description="""ID of the organization to filter inventory by.""")
    ],
    site_id: Annotated[
        Optional[UUID | None],
        Field(
            description="""ID of the site to filter inventory by. Optional, if not provided inventory for all sites will be listed."""
        ),
    ] = None,
    serial: Annotated[
        Optional[str | None],
        Field(
            description="""Serial number of the device to filter inventory by. Optional, if not provided all devices will be listed."""
        ),
    ] = None,
    model: Annotated[
        Optional[str | None],
        Field(
            description="""Model of the device to filter inventory by. Optional, if not provided all devices will be listed."""
        ),
    ] = None,
    mac: Annotated[
        Optional[str | None],
        Field(
            description="""MAC address of the device to filter inventory by. Optional, if not provided all devices will be listed."""
        ),
    ] = None,
    vc: Annotated[
        Optional[bool | None],
        Field(description="""To display Virtual Chassis members"""),
    ] = None,
    device_type: Annotated[
        Optional[Device_type | None],
        Field(
            description="""Type of the device to filter inventory by. Optional, if not provided all devices will be listed."""
        ),
    ] = None,
    limit: Annotated[
        Optional[int | None],
        Field(
            description="""Maximum number of devices to retrieve. If not specified, the API will return up to 100 devices (maximum allowed is 1000)."""
        ),
    ] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """Retrieve the inventory of devices for a specified organization and optionally filter by site. This tool provides a consolidated view of all devices within an organization, allowing users to easily access and manage their network inventory."""

    logger.debug("Tool getOrgInventory called")

    apisession, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.orgs.inventory.getOrgInventory(
        apisession,
        org_id=str(org_id),
        serial=serial if serial else None,
        model=model if model else None,
        type=device_type.value if device_type else None,
        mac=mac if mac else None,
        site_id=str(site_id) if site_id else None,
        vc=vc if vc else None,
        limit=limit if limit else None,
    )
    await process_response(response)
    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
