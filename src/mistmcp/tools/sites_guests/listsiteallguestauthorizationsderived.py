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
        fn=listSiteAllGuestAuthorizationsDerived,
        name="listSiteAllGuestAuthorizationsDerived",
        description="""Get List of Site Guest Authorizations""",
        tags={"Sites Guests"},
        annotations={
            "title": "listSiteAllGuestAuthorizationsDerived",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True
        }
    )

def remove_tool():
    mcp.remove_tool("listSiteAllGuestAuthorizationsDerived")

async def listSiteAllGuestAuthorizationsDerived(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    wlan_id: Annotated[Optional[str], Field(description="""UUID of single or multiple (Comma separated) WLAN under Site `site_id` (to filter by WLAN)""")] | None = None,
    cross_site: Annotated[Optional[bool], Field(description="""Whether to get org level guests, default is false i.e get site level guests""")] | None = None,
) -> dict:
    """Get List of Site Guest Authorizations"""

    response = mistapi.api.v1.sites.guests.listSiteAllGuestAuthorizationsDerived(
            apisession,
            site_id=str(site_id),
            wlan_id=wlan_id,
            cross_site=cross_site,
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
