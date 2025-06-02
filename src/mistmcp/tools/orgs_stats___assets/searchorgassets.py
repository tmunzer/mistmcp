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





def add_tool():
    mcp.add_tool(
        fn=searchOrgAssets,
        name="searchOrgAssets",
        description="""Search for Org Assets""",
        tags={"Orgs Stats - Assets"},
        annotations={
            "title": "searchOrgAssets",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True
        }
    )

def remove_tool():
    mcp.remove_tool("searchOrgAssets")

async def searchOrgAssets(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    site_id: Annotated[Optional[str], Field(description="""ID of the Mist Site""")] | None = None,
    mac: Optional[str] | None = None,
    device_name: Optional[str] | None = None,
    name: Optional[str] | None = None,
    map_id: Annotated[Optional[str], Field(description="""ID of the Mist Map""")] | None = None,
    ibeacon_uuid: Optional[str] | None = None,
    ibeacon_major: Optional[str] | None = None,
    ibeacon_minor: Optional[str] | None = None,
    eddystone_uid_namespace: Optional[str] | None = None,
    eddystone_uid_instance: Optional[str] | None = None,
    eddystone_url: Optional[str] | None = None,
    ap_mac: Optional[str] | None = None,
    beam: Optional[int] | None = None,
    rssi: Optional[int] | None = None,
    limit: Annotated[int, Field(default=100)] = 100,
    start: Annotated[Optional[int], Field(description="""Start datetime, can be epoch or relative time like -1d, -1w; -1d if not specified""")] | None = None,
    end: Annotated[Optional[int], Field(description="""End datetime, can be epoch or relative time like -1d, -2h; now if not specified""")] | None = None,
    duration: Annotated[str, Field(description="""Duration like 7d, 2w""",default="1d")] = "1d",
) -> dict:
    """Search for Org Assets"""

    response = mistapi.api.v1.orgs.stats.searchOrgAssets(
            apisession,
            org_id=str(org_id),
            site_id=site_id,
            mac=mac,
            device_name=device_name,
            name=name,
            map_id=map_id,
            ibeacon_uuid=ibeacon_uuid,
            ibeacon_major=ibeacon_major,
            ibeacon_minor=ibeacon_minor,
            eddystone_uid_namespace=eddystone_uid_namespace,
            eddystone_uid_instance=eddystone_uid_instance,
            eddystone_url=eddystone_url,
            ap_mac=ap_mac,
            beam=beam,
            rssi=rssi,
            limit=limit,
            start=start,
            end=end,
            duration=duration,
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
