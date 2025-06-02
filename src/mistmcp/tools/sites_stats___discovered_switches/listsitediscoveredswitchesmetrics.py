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
        fn=listSiteDiscoveredSwitchesMetrics,
        name="listSiteDiscoveredSwitchesMetrics",
        description="""Discovered switches related metrics, lists related switch system names & details if not compliant""",
        tags={"Sites Stats - Discovered Switches"},
        annotations={
            "title": "listSiteDiscoveredSwitchesMetrics",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True
        }
    )

def remove_tool():
    mcp.remove_tool("listSiteDiscoveredSwitchesMetrics")

async def listSiteDiscoveredSwitchesMetrics(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    threshold: Annotated[Optional[str], Field(description="""Configurable # ap per switch threshold, default 12""")] | None = None,
    system_name: Annotated[Optional[str], Field(description="""System name for switch level metrics, optional""")] | None = None,
) -> dict:
    """Discovered switches related metrics, lists related switch system names & details if not compliant"""

    response = mistapi.api.v1.sites.stats.listSiteDiscoveredSwitchesMetrics(
            apisession,
            site_id=str(site_id),
            threshold=threshold,
            system_name=system_name,
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
