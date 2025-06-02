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


def add_tool():
    mcp.add_tool(
        fn=searchOrgInventory,
        name="searchOrgInventory",
        description="""Search in the Org Inventory""",
        tags={"Orgs Inventory"},
        annotations={
            "title": "searchOrgInventory",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True
        }
    )

def remove_tool():
    mcp.remove_tool("searchOrgInventory")

async def searchOrgInventory(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    type: Type = Type.AP,
    mac: Annotated[Optional[str], Field(description="""MAC address""")] | None = None,
    vc_mac: Annotated[Optional[str], Field(description="""Virtual Chassis MAC Address""")] | None = None,
    master_mac: Annotated[Optional[str], Field(description="""Master device mac for virtual mac cluster""")] | None = None,
    site_id: Annotated[Optional[str], Field(description="""Site id if assigned, null if not assigned""")] | None = None,
    serial: Annotated[Optional[str], Field(description="""Device serial""")] | None = None,
    master: Annotated[Optional[str], Field(description="""true / false""")] | None = None,
    sku: Annotated[Optional[str], Field(description="""Device sku""")] | None = None,
    version: Annotated[Optional[str], Field(description="""Device version""")] | None = None,
    status: Annotated[Optional[str], Field(description="""Device status""")] | None = None,
    text: Annotated[Optional[str], Field(description="""Wildcards for name, mac, serial""")] | None = None,
    limit: Annotated[int, Field(default=100)] = 100,
    page: Annotated[int, Field(ge=1,default=1)] = 1,
) -> dict:
    """Search in the Org Inventory"""

    response = mistapi.api.v1.orgs.inventory.searchOrgInventory(
            apisession,
            org_id=str(org_id),
            type=type.value,
            mac=mac,
            vc_mac=vc_mac,
            master_mac=master_mac,
            site_id=site_id,
            serial=serial,
            master=master,
            sku=sku,
            version=version,
            status=status,
            text=text,
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
