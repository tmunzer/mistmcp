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
        fn=searchOrgMxEdges,
        name="searchOrgMxEdges",
        description="""Search Org Mist Edges""",
        tags={"Orgs MxEdges"},
        annotations={
            "title": "searchOrgMxEdges",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True
        }
    )

def remove_tool():
    mcp.remove_tool("searchOrgMxEdges")

async def searchOrgMxEdges(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    mxedge_id: Annotated[Optional[str], Field(description="""Mist edge id""")] | None = None,
    site_id: Annotated[Optional[str], Field(description="""Mist edge site id""")] | None = None,
    mxcluster_id: Annotated[Optional[str], Field(description="""Mist edge cluster id""")] | None = None,
    model: Annotated[Optional[str], Field(description="""Model name""")] | None = None,
    distro: Annotated[Optional[str], Field(description="""Debian code name (buster, bullseye)""")] | None = None,
    tunterm_version: Annotated[Optional[str], Field(description="""tunterm version""")] | None = None,
    sort: Annotated[Optional[str], Field(description="""Sort options, -prefix represents DESC order, default is -last_seen""")] | None = None,
    stats: Annotated[Optional[bool], Field(description="""Whether to return device stats, default is false""")] | None = None,
    start: Annotated[Optional[int], Field(description="""Start datetime, can be epoch or relative time like -1d, -1w; -1d if not specified""")] | None = None,
    end: Annotated[Optional[int], Field(description="""End datetime, can be epoch or relative time like -1d, -2h; now if not specified""")] | None = None,
    duration: Annotated[str, Field(description="""Duration like 7d, 2w""",default="1d")] = "1d",
    limit: Annotated[int, Field(default=100)] = 100,
    page: Annotated[int, Field(ge=1,default=1)] = 1,
) -> dict:
    """Search Org Mist Edges"""

    response = mistapi.api.v1.orgs.mxedges.searchOrgMxEdges(
            apisession,
            org_id=str(org_id),
            mxedge_id=mxedge_id,
            site_id=site_id,
            mxcluster_id=mxcluster_id,
            model=model,
            distro=distro,
            tunterm_version=tunterm_version,
            sort=sort,
            stats=stats,
            start=start,
            end=end,
            duration=duration,
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
