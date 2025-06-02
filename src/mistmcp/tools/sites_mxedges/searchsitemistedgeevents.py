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
        fn=searchSiteMistEdgeEvents,
        name="searchSiteMistEdgeEvents",
        description="""Search Site Mist Edge Events""",
        tags={"Sites MxEdges"},
        annotations={
            "title": "searchSiteMistEdgeEvents",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True
        }
    )

def remove_tool():
    mcp.remove_tool("searchSiteMistEdgeEvents")

async def searchSiteMistEdgeEvents(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    mxedge_id: Annotated[Optional[str], Field(description="""Mist edge id""")] | None = None,
    mxcluster_id: Annotated[Optional[str], Field(description="""Mist edge cluster id""")] | None = None,
    type: Annotated[Optional[str], Field(description="""See `listDeviceEventsDefinitions`""")] | None = None,
    service: Annotated[Optional[str], Field(description="""Service running on mist edge(mxagent, tunterm etc)""")] | None = None,
    component: Annotated[Optional[str], Field(description="""Component like PS1, PS2""")] | None = None,
    start: Annotated[Optional[int], Field(description="""Start datetime, can be epoch or relative time like -1d, -1w; -1d if not specified""")] | None = None,
    end: Annotated[Optional[int], Field(description="""End datetime, can be epoch or relative time like -1d, -2h; now if not specified""")] | None = None,
    duration: Annotated[str, Field(description="""Duration like 7d, 2w""",default="1d")] = "1d",
    limit: Annotated[int, Field(default=100)] = 100,
) -> dict:
    """Search Site Mist Edge Events"""

    response = mistapi.api.v1.sites.mxedges.searchSiteMistEdgeEvents(
            apisession,
            site_id=str(site_id),
            mxedge_id=mxedge_id,
            mxcluster_id=mxcluster_id,
            type=type,
            service=service,
            component=component,
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
