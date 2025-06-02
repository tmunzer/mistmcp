""""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""
import json
import mistapi
from fastmcp.server.dependencies import get_context
from fastmcp.exceptions import ToolError
from mistmcp.__server import mcp
from mistmcp.__mistapi import apisession
from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum




class Type(Enum):
    AP = "ap"
    GATEWAY = "gateway"
    SWITCH = "switch"
    NONE = None


def add_tool():
    mcp.add_tool(
        fn=getOrgInventory,
        name="getOrgInventory",
        description="""Get Org Inventory### VC (Virtual-Chassis) Management Starting with the April release, Virtual Chassis devices in Mist will now usea cloud-assigned virtual MAC address as the device ID, instead of the physicalMAC address of the FPC0 member.**Retrieving the device ID or Site ID of a Virtual Chassis:**1. Use this API call with the query parameters `vc=true` and `mac` set to the MAC address of the VC member.2. In the response, check the `vc_mac` and `mac` fields:    - If `vc_mac` is empty or not present, the device is not part of a Virtual Chassis.    The `device_id` and `site_id` will be available in the device information.    - If `vc_mac` differs from the `mac` field, the device is part of a Virtual Chassis    but is not the device used to generate the Virtual Chassis ID. Use the `vc_mac` value with the [Get Org Inventory]($e/Orgs%20Inventory/getOrgInventory)    API call to retrieve the `device_id` and `site_id`.    - If `vc_mac` matches the `mac` field, the device is the device used to generate the Virtual Chassis ID and he `device_id` and `site_id` will be available    in the device information.      This is the case if the device is the Virtual Chassis "virtual device" (MAC starting with `020003`) or if the device is the Virtual Chassis FPC0 and the Virtual Chassis is still using the FPC0 MAC address to generate the device ID.""",
        tags={"Orgs Inventory"},
        annotations={
            "title": "getOrgInventory",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True
        }
    )

def remove_tool():
    mcp.remove_tool("getOrgInventory")

async def getOrgInventory(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    serial: Annotated[Optional[str], Field(description="""Device serial""")] | None = None,
    model: Annotated[Optional[str], Field(description="""Device model""")] | None = None,
    type: Type = Type.NONE,
    mac: Annotated[Optional[str], Field(description="""MAC address""")] | None = None,
    site_id: Annotated[Optional[str], Field(description="""Site id if assigned, null if not assigned""")] | None = None,
    vc_mac: Annotated[Optional[str], Field(description="""Virtual Chassis MAC Address""")] | None = None,
    vc: Annotated[Optional[bool], Field(description="""To display Virtual Chassis members""")] | None = None,
    unassigned: Annotated[bool, Field(description="""To display Unassigned devices""",default=True)] = True,
    modified_after: Annotated[Optional[int], Field(description="""Filter on inventory last modified time, in epoch""")] | None = None,
    limit: Annotated[int, Field(default=100)] = 100,
    page: Annotated[int, Field(ge=1,default=1)] = 1,
) -> dict:
    """Get Org Inventory### VC (Virtual-Chassis) Management Starting with the April release, Virtual Chassis devices in Mist will now usea cloud-assigned virtual MAC address as the device ID, instead of the physicalMAC address of the FPC0 member.**Retrieving the device ID or Site ID of a Virtual Chassis:**1. Use this API call with the query parameters `vc=true` and `mac` set to the MAC address of the VC member.2. In the response, check the `vc_mac` and `mac` fields:    - If `vc_mac` is empty or not present, the device is not part of a Virtual Chassis.    The `device_id` and `site_id` will be available in the device information.    - If `vc_mac` differs from the `mac` field, the device is part of a Virtual Chassis    but is not the device used to generate the Virtual Chassis ID. Use the `vc_mac` value with the [Get Org Inventory]($e/Orgs%20Inventory/getOrgInventory)    API call to retrieve the `device_id` and `site_id`.    - If `vc_mac` matches the `mac` field, the device is the device used to generate the Virtual Chassis ID and he `device_id` and `site_id` will be available    in the device information.      This is the case if the device is the Virtual Chassis "virtual device" (MAC starting with `020003`) or if the device is the Virtual Chassis FPC0 and the Virtual Chassis is still using the FPC0 MAC address to generate the device ID."""

    response = mistapi.api.v1.orgs.inventory.getOrgInventory(
            apisession,
            org_id=str(org_id),
            serial=serial,
            model=model,
            type=type.value,
            mac=mac,
            site_id=site_id,
            vc_mac=vc_mac,
            vc=vc,
            unassigned=unassigned,
            modified_after=modified_after,
            limit=limit,
            page=page,
    )
    
    
    ctx = get_context()
    
    if response.status_code != 200:
        error = {
            "status_code": response.status_code,
            "message": ""
        }
        if response.data:
            await ctx.error(f"Got HTTP{response.status_code} with details {response.data}")
            error["message"] =json.dumps(response.data)
        elif response.status_code == 400:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] =json.dumps("Bad Request. The API endpoint exists but its syntax/payload is incorrect, detail may be given")
        elif response.status_code == 401:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] =json.dumps("Unauthorized")
        elif response.status_code == 403:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] =json.dumps("Unauthorized")
        elif response.status_code == 401:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] =json.dumps("Permission Denied")
        elif response.status_code == 404:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] =json.dumps("Not found. The API endpoint doesn’t exist or resource doesn’t exist")
        elif response.status_code == 429:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] =json.dumps("Too Many Request. The API Token used for the request reached the 5000 API Calls per hour threshold")
        raise ToolError(error)
            
    return response.data
