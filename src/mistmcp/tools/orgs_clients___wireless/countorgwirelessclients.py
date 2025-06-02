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
    DEVICE = "device"
    HOSTNAME = "hostname"
    IP = "ip"
    MAC = "mac"
    MODEL = "model"
    OS = "os"
    SSID = "ssid"
    VLAN = "vlan"


def add_tool():
    mcp.add_tool(
        fn=countOrgWirelessClients,
        name="countOrgWirelessClients",
        description="""Count by Distinct Attributes of Org Wireless Clients""",
        tags={"Orgs Clients - Wireless"},
        annotations={
            "title": "countOrgWirelessClients",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True
        }
    )

def remove_tool():
    mcp.remove_tool("countOrgWirelessClients")

async def countOrgWirelessClients(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    distinct: Distinct = Distinct.DEVICE,
    mac: Annotated[Optional[str], Field(description="""Partial / full MAC address""")] | None = None,
    hostname: Annotated[Optional[str], Field(description="""Partial / full hostname""")] | None = None,
    device: Annotated[Optional[str], Field(description="""Device type, e.g. Mac, Nvidia, iPhone""")] | None = None,
    os: Annotated[Optional[str], Field(description="""OS, e.g. Sierra, Yosemite, Windows 10""")] | None = None,
    model: Annotated[Optional[str], Field(description="""Model, e.g. 'MBP 15 late 2013', 6, 6s, '8+ GSM'""")] | None = None,
    ap: Annotated[Optional[str], Field(description="""AP mac where the client has connected to""")] | None = None,
    vlan: Annotated[Optional[str], Field(description="""VLAN""")] | None = None,
    ssid: Annotated[Optional[str], Field(description="""SSID""")] | None = None,
    ip_address: Optional[str] | None = None,
    start: Annotated[Optional[int], Field(description="""Start datetime, can be epoch or relative time like -1d, -1w; -1d if not specified""")] | None = None,
    end: Annotated[Optional[int], Field(description="""End datetime, can be epoch or relative time like -1d, -2h; now if not specified""")] | None = None,
    duration: Annotated[str, Field(description="""Duration like 7d, 2w""",default="1d")] = "1d",
    limit: Annotated[int, Field(default=100)] = 100,
) -> dict:
    """Count by Distinct Attributes of Org Wireless Clients"""

    response = mistapi.api.v1.orgs.clients.countOrgWirelessClients(
            apisession,
            org_id=str(org_id),
            distinct=distinct.value,
            mac=mac,
            hostname=hostname,
            device=device,
            os=os,
            model=model,
            ap=ap,
            vlan=vlan,
            ssid=ssid,
            ip_address=ip_address,
            start=start,
            end=end,
            duration=duration,
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
