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
        fn=getOrgJuniperDevicesCommand,
        name="getOrgJuniperDevicesCommand",
        description="""Get Org Juniper Devices commandJuniper devices can be managed/adopted by Mist. Currently outbound-ssh + netconf is used.A few lines of CLI commands are generated per-Org, allowing the Juniper devices to phone home to Mist.""",
        tags={"Orgs Devices"},
        annotations={
            "title": "getOrgJuniperDevicesCommand",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True
        }
    )

def remove_tool():
    mcp.remove_tool("getOrgJuniperDevicesCommand")

async def getOrgJuniperDevicesCommand(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    site_id: Annotated[Optional[str], Field(description="""Site_id would be used for proxy config check of the site and automatic site assignment""")] | None = None,
) -> dict:
    """Get Org Juniper Devices commandJuniper devices can be managed/adopted by Mist. Currently outbound-ssh + netconf is used.A few lines of CLI commands are generated per-Org, allowing the Juniper devices to phone home to Mist."""

    response = mistapi.api.v1.orgs.ocdevices.getOrgJuniperDevicesCommand(
            apisession,
            org_id=str(org_id),
            site_id=site_id,
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
