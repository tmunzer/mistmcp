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
from enum import Enum



mcp = get_mcp()

if not mcp:
    raise RuntimeError(
        "MCP instance not found. Make sure to initialize the MCP server before defining tools."
    )



class Type(Enum):
    HONEYPOT = "honeypot"
    LAN = "lan"
    OTHERS = "others"
    SPOOF = "spoof"
    NONE = None



@mcp.tool(
    enabled=True,
    name = "listSiteRogueAPs",
    description = """Get List of Site Rogue/Neighbor APs""",
    tags = {"Sites Rogues"},
    annotations = {
        "title": "listSiteRogueAPs",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def listSiteRogueAPs(
    
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    type: Optional[Type | None] = Type.NONE,
    limit: Optional[int | None] = None,
    start: Annotated[Optional[str | None], Field(description="""Start time (epoch timestamp in seconds, or relative string like '-1d', '-1w')""")] = None,
    end: Annotated[Optional[str | None], Field(description="""End time (epoch timestamp in seconds, or relative string like '-1d', '-2h', 'now')""")] = None,
    duration: Annotated[Optional[str | None], Field(description="""Duration like 7d, 2w""")] = None,
    interval: Annotated[Optional[str | None], Field(description="""Aggregation works by giving a time range plus interval (e.g. 1d, 1h, 10m) where aggregation function would be applied to.""")] = None,
    rogue_bssid: Annotated[Optional[str | None], Field(description="""BSSID of the rogue AP to filter stats by. Optional, if not provided all rogue APs will be listed.""")] = None,
) -> dict|list:
    """Get List of Site Rogue/Neighbor APs"""

    apisession = get_apisession()
    data = {}
    
    
    if rogue_bssid:
        response = mistapi.api.v1.sites.rogues.getSiteRogueAP(apisession, site_id=str(site_id), rogue_bssid=rogue_bssid)
        await process_response(response)
    else:
        response = mistapi.api.v1.sites.insights.listSiteRogueAPs(
            apisession,
            site_id=str(site_id),
            type=type.value if type else None,
            limit=limit if limit else None,
            start=start if start else None,
            end=end if end else None,
            duration=duration if duration else None,
            interval=interval if interval else None,
    )
        await process_response(response)
        
    data = response.data


    return data
