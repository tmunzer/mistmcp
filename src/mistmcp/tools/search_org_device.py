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
from enum import Enum


class Device_type(Enum):
    AP = "ap"
    SWITCH = "switch"
    GATEWAY = "gateway"


class Status(Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


@mcp.tool(
    name="mist_search_org_device",
    description="""Search a network device in the Organization Inventory. This tool provides a consolidated view of all devices within an organization, even those not assigned to any site. This can be used to quickly search for a device across the whole organization. It allows filtering by various attributes such as serial number, model, MAC address, firmware version, device type, and connection status. This tool is useful for quickly finding specific devices or getting an overview of the organization's inventory without needing to query each site separately.""",
    tags={"devices"},
    annotations={
        "title": "Search org device",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def search_org_device(
    org_id: Annotated[UUID, Field(description="""Organization ID""")],
    site_id: Annotated[Optional[UUID], Field(description="""Site ID""")],
    serial: Annotated[
        Optional[str],
        Field(description="""Serial number of the device to filter inventory by"""),
    ],
    model: Annotated[
        Optional[str],
        Field(description="""Model of the device to filter inventory by"""),
    ],
    mac: Annotated[
        Optional[str],
        Field(description="""MAC address of the device to filter inventory by"""),
    ],
    version: Annotated[
        Optional[str],
        Field(description="""Firmware version of the device to filter inventory by"""),
    ],
    vc_mac: Annotated[
        Optional[str],
        Field(
            description="""MAC address of the virtual chassis (switch stack) to filter inventory by"""
        ),
    ],
    device_type: Annotated[
        Optional[Device_type],
        Field(description="""Type of the device to filter inventory by"""),
    ],
    status: Annotated[
        Optional[Status],
        Field(description="""Connection status of the device to filter inventory by"""),
    ],
    text: Annotated[
        Optional[str],
        Field(
            description="""Text to search for in device attributes (name, serial, MAC). Use the wildcard `*` for partial matches (e.g. `AP*` to match all devices with names starting with 'AP')"""
        ),
    ],
    limit: Annotated[
        int, Field(description="""Max number of results per page""", default=20)
    ] = 20,
) -> dict | list | str:
    """Search a network device in the Organization Inventory. This tool provides a consolidated view of all devices within an organization, even those not assigned to any site. This can be used to quickly search for a device across the whole organization. It allows filtering by various attributes such as serial number, model, MAC address, firmware version, device type, and connection status. This tool is useful for quickly finding specific devices or getting an overview of the organization's inventory without needing to query each site separately."""

    logger.debug("Tool search_org_device called")

    apisession, response_format = await get_apisession()

    try:
        response = mistapi.api.v1.orgs.inventory.searchOrgInventory(
            apisession,
            org_id=str(org_id),
            serial=serial if serial else None,
            model=model if model else None,
            type=device_type.value if device_type else None,
            mac=mac if mac else None,
            site_id=str(site_id) if site_id else None,
            vc_mac=vc_mac if vc_mac else None,
            version=version if version else None,
            text=text if text else None,
            status=status.value if status else None,
            limit=limit,
        )
        await process_response(response)
    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
