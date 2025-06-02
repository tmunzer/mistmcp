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




class Distinct(Enum):
    AP = "ap"
    APP = "app"
    CATEGORY = "category"
    DEVICE_MAC = "device_mac"
    PORT_ID = "port_id"
    SERVICE = "service"
    SRC_IP = "src_ip"
    SSID = "ssid"
    WCID = "wcid"
    WLAN_ID_APP = "wlan_id app"
    NONE = None


def add_tool():
    mcp.add_tool(
        fn=countSiteApps,
        name="countSiteApps",
        description="""Count by Distinct Attributes of Applications""",
        tags={"Sites Stats - Apps"},
        annotations={
            "title": "countSiteApps",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True
        }
    )

def remove_tool():
    mcp.remove_tool("countSiteApps")

async def countSiteApps(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    distinct: Annotated[Distinct, Field(description="""Default for wireless devices is `ap`. Default for wired devices is `device_mac`""")] = Distinct.NONE,
    device_mac: Annotated[Optional[str], Field(description="""MAC of the device""")] | None = None,
    app: Annotated[Optional[str], Field(description="""Application name""")] | None = None,
    wired: Annotated[Optional[str], Field(description="""If a device is wired or wireless. Default is False.""")] | None = None,
    limit: Annotated[int, Field(default=100)] = 100,
) -> dict:
    """Count by Distinct Attributes of Applications"""

    response = mistapi.api.v1.sites.stats.countSiteApps(
            apisession,
            site_id=str(site_id),
            distinct=distinct.value,
            device_mac=device_mac,
            app=app,
            wired=wired,
            limit=limit,
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
