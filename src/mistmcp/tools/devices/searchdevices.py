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
from enum import Enum
from uuid import UUID


class Scope(Enum):
    LIST = "list"


class Device_type(Enum):
    AP = "ap"
    SWITCH = "switch"
    GATEWAY = "gateway"


@mcp.tool(
    name="searchDevices",
    description="""This tool can be used to search for devices in an organization or site. You can filter the search by device type, device name, or MAC address using the `device_type`, `name`, and `mac` parameters, respectivelyIMPORTANT: this tool only returns devices that are currently connected to Mist""",
    tags={"devices"},
    annotations={
        "title": "searchDevices",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchDevices(
    scope: Annotated[
        Scope,
        Field(
            description="""Whether to search for devices in the entire organization or a specific site. If `site` is selected, the `site_id` parameter is required"""
        ),
    ],
    org_id: Annotated[UUID, Field(description="""Organization ID""")],
    site_id: Annotated[Optional[UUID | None], Field(description="""Site ID""")] = None,
    device_type: Annotated[
        Optional[Device_type | None],
        Field(description="""Type of device to search for"""),
    ] = None,
    hostname: Annotated[
        Optional[str | None],
        Field(
            description="""Hostname of the device to search for. Supports partial matches"""
        ),
    ] = None,
    mac: Annotated[
        Optional[str | None],
        Field(description="""MAC address of the device to search for"""),
    ] = None,
    model: Annotated[
        Optional[str | None], Field(description="""Model of the device to search for""")
    ] = None,
    limit: Annotated[
        int, Field(description="""Max number of results per page""", default=10)
    ] = 10,
    ctx: Context | None = None,
) -> dict | list | str:
    """This tool can be used to search for devices in an organization or site. You can filter the search by device type, device name, or MAC address using the `device_type`, `name`, and `mac` parameters, respectivelyIMPORTANT: this tool only returns devices that are currently connected to Mist"""

    logger.debug("Tool searchDevices called")

    apisession, response_format = get_apisession()

    object_type = scope

    if object_type.value == "site":
        if not site_id:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`site_id` parameter is required when `object_type` is "site".',
                }
            )

    match object_type.value:
        case "list":
            if site_id:
                response = mistapi.api.v1.sites.devices.searchSiteDevices(
                    apisession,
                    site_id=str(site_id),
                    type=str(device_type) if device_type else None,
                    hostname=str(hostname) if hostname else None,
                    mac=str(mac) if mac else None,
                    model=str(model) if model else None,
                    limit=limit,
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.devices.searchOrgDevices(
                    apisession,
                    org_id=str(org_id),
                    type=str(device_type) if device_type else None,
                    hostname=str(hostname) if hostname else None,
                    mac=str(mac) if mac else None,
                    model=str(model) if model else None,
                    limit=limit,
                )
                await process_response(response)

        case _:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Scope]}",
                }
            )

    return format_response(response, response_format)
