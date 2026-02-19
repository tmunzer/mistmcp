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
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


mcp = get_mcp()

if not mcp:
    raise RuntimeError(
        "MCP instance not found. Make sure to initialize the MCP server before defining tools."
    )


class Type(Enum):
    AP = "ap"
    GATEWAY = "gateway"
    SWITCH = "switch"
    NONE = None


@mcp.tool(
    enabled=True,
    name="getOrgInventory",
    description="""Get Org Inventory### VC (Virtual-Chassis) Management Starting with the April release, Virtual Chassis devices in Mist will now usea cloud-assigned virtual MAC address as the device ID, instead of the physicalMAC address of the FPC0 member.**Retrieving the device ID or Site ID of a Virtual Chassis:**1. Use this API call with the query parameters `vc=true` and `mac` set to the MAC address of the VC member.2. In the response, check the `vc_mac` and `mac` fields:    - If `vc_mac` is empty or not present, the device is not part of a Virtual Chassis.    The `device_id` and `site_id` will be available in the device information.    - If `vc_mac` differs from the `mac` field, the device is part of a Virtual Chassis    but is not the device used to generate the Virtual Chassis ID. Use the `vc_mac` value with the [Get Org Inventory](/#operations/getOrgInventory)    API call to retrieve the `device_id` and `site_id`.    - If `vc_mac` matches the `mac` field, the device is the device used to generate the Virtual Chassis ID and he `device_id` and `site_id` will be available    in the device information.      This is the case if the device is the Virtual Chassis "virtual device" (MAC starting with `020003`) or if the device is the Virtual Chassis FPC0 and the Virtual Chassis is still using the FPC0 MAC address to generate the device ID.""",
    tags={"devices"},
    annotations={
        "title": "getOrgInventory",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getOrgInventory(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    serial: Annotated[
        Optional[str | None], Field(description="""Device serial""")
    ] = None,
    model: Annotated[
        Optional[str | None], Field(description="""Device model""")
    ] = None,
    type: Optional[Type | None] = Type.NONE,
    mac: Annotated[Optional[str | None], Field(description="""MAC address""")] = None,
    site_id: Annotated[
        Optional[UUID | None],
        Field(description="""Site id if assigned, null if not assigned"""),
    ] = None,
    vc_mac: Annotated[
        Optional[str | None], Field(description="""Virtual Chassis MAC Address""")
    ] = None,
    vc: Annotated[
        Optional[bool | None],
        Field(description="""To display Virtual Chassis members"""),
    ] = None,
    unassigned: Annotated[
        Optional[bool | None], Field(description="""To display Unassigned devices""")
    ] = None,
    modified_after: Annotated[
        Optional[int | None],
        Field(description="""Filter on inventory last modified time, in epoch"""),
    ] = None,
    limit: Optional[int | None] = None,
    page: Annotated[Optional[int | None], Field(ge=1)] = None,
) -> dict | list | str:
    """Get Org Inventory### VC (Virtual-Chassis) Management Starting with the April release, Virtual Chassis devices in Mist will now usea cloud-assigned virtual MAC address as the device ID, instead of the physicalMAC address of the FPC0 member.**Retrieving the device ID or Site ID of a Virtual Chassis:**1. Use this API call with the query parameters `vc=true` and `mac` set to the MAC address of the VC member.2. In the response, check the `vc_mac` and `mac` fields:    - If `vc_mac` is empty or not present, the device is not part of a Virtual Chassis.    The `device_id` and `site_id` will be available in the device information.    - If `vc_mac` differs from the `mac` field, the device is part of a Virtual Chassis    but is not the device used to generate the Virtual Chassis ID. Use the `vc_mac` value with the [Get Org Inventory](/#operations/getOrgInventory)    API call to retrieve the `device_id` and `site_id`.    - If `vc_mac` matches the `mac` field, the device is the device used to generate the Virtual Chassis ID and he `device_id` and `site_id` will be available    in the device information.      This is the case if the device is the Virtual Chassis "virtual device" (MAC starting with `020003`) or if the device is the Virtual Chassis FPC0 and the Virtual Chassis is still using the FPC0 MAC address to generate the device ID."""

    apisession, _, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.orgs.inventory.getOrgInventory(
        apisession,
        org_id=str(org_id),
        serial=serial if serial else None,
        model=model if model else None,
        type=type.value if type else None,
        mac=mac if mac else None,
        site_id=str(site_id) if site_id else None,
        vc_mac=vc_mac if vc_mac else None,
        vc=vc if vc else None,
        unassigned=unassigned if unassigned else None,
        modified_after=modified_after if modified_after else None,
        limit=limit if limit else None,
        page=page if page else None,
    )
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
