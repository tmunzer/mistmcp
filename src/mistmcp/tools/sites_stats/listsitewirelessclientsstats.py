"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""
import json
import mistapi
from fastmcp.exceptions import ToolError
from mistmcp.request_processor import get_apisession
from mistmcp.response_processor import process_response
from mistmcp.server import get_mcp

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID



mcp = get_mcp()

if not mcp:
    raise RuntimeError(
        "MCP instance not found. Make sure to initialize the MCP server before defining tools."
    )





@mcp.tool(
    enabled=True,
    name = "listSiteWirelessClientsStats",
    description = """Get List of Site All Clients Stats Details""",
    tags = {"sites_stats"},
    annotations = {
        "title": "listSiteWirelessClientsStats",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def listSiteWirelessClientsStats(
    
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    wired: Optional[bool | None] = None,
    limit: Optional[int | None] = None,
    start: Annotated[Optional[str | None], Field(description="""Start time (epoch timestamp in seconds, or relative string like '-1d', '-1w')""")] = None,
    end: Annotated[Optional[str | None], Field(description="""End time (epoch timestamp in seconds, or relative string like '-1d', '-2h', 'now')""")] = None,
    duration: Annotated[Optional[str | None], Field(description="""Duration like 7d, 2w""")] = None,
    client_mac: Annotated[Optional[str | None], Field(description="""MAC address of the client to filter stats by. Optional, if not provided all clients will be listed.""")] = None,
) -> dict|list:
    """Get List of Site All Clients Stats Details"""

    apisession = get_apisession()
    data = {}
    
    
    if client_mac:
        response = mistapi.api.v1.sites.stats.getSiteWirelessClientStats(apisession, site_id=str(site_id), client_mac=client_mac)
        await process_response(response)
    else:
        response = mistapi.api.v1.sites.stats.listSiteWirelessClientsStats(
            apisession,
            site_id=str(site_id),
            wired=wired if wired else None,
            limit=limit if limit else None,
            start=start if start else None,
            end=end if end else None,
            duration=duration if duration else None,
    )
        await process_response(response)
        
    data = response.data


    return data
