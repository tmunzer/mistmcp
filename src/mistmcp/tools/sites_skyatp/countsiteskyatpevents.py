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
    DEVICE_MAC = "device_mac"
    MAC = "mac"
    THREAT_LEVEL = "threat_level"
    TYPE = "type"


def add_tool():
    mcp.add_tool(
        fn=countSiteSkyatpEvents,
        name="countSiteSkyatpEvents",
        description="""Count by Distinct Attributes of Skyatp Events (WIP)""",
        tags={"Sites Skyatp"},
        annotations={
            "title": "countSiteSkyatpEvents",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True
        }
    )

def remove_tool():
    mcp.remove_tool("countSiteSkyatpEvents")

async def countSiteSkyatpEvents(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    distinct: Distinct = Distinct.TYPE,
    type: Annotated[Optional[str], Field(description="""Event type, e.g. cc, fs, mw""")] | None = None,
    mac: Annotated[Optional[str], Field(description="""Client MAC""")] | None = None,
    device_mac: Annotated[Optional[str], Field(description="""Device MAC""")] | None = None,
    threat_level: Annotated[Optional[int], Field(description="""Threat level""")] | None = None,
    ip_address: Optional[str] | None = None,
    start: Annotated[Optional[int], Field(description="""Start datetime, can be epoch or relative time like -1d, -1w; -1d if not specified""")] | None = None,
    end: Annotated[Optional[int], Field(description="""End datetime, can be epoch or relative time like -1d, -2h; now if not specified""")] | None = None,
    duration: Annotated[str, Field(description="""Duration like 7d, 2w""",default="1d")] = "1d",
    limit: Annotated[int, Field(default=100)] = 100,
) -> dict:
    """Count by Distinct Attributes of Skyatp Events (WIP)"""

    response = mistapi.api.v1.sites.skyatp.countSiteSkyatpEvents(
            apisession,
            site_id=str(site_id),
            distinct=distinct.value,
            type=type,
            mac=mac,
            device_mac=device_mac,
            threat_level=threat_level,
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
