""" "
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


def add_tool() -> None:
    mcp.add_tool(
        fn=searchSiteWanUsage,
        name="searchSiteWanUsage",
        description="""Search Site WAN Usages""",
        tags={"Sites WAN Usages"},
        annotations={
            "title": "searchSiteWanUsage",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True,
        },
    )


def remove_tool() -> None:
    mcp.remove_tool("searchSiteWanUsage")


async def searchSiteWanUsage(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    mac: Annotated[Optional[str], Field(description="""MAC address""")] | None = None,
    peer_mac: Annotated[Optional[str], Field(description="""Peer MAC address""")]
    | None = None,
    port_id: Annotated[Optional[str], Field(description="""Port ID for the device""")]
    | None = None,
    peer_port_id: Annotated[
        Optional[str], Field(description="""Peer Port ID for the device""")
    ]
    | None = None,
    policy: Annotated[Optional[str], Field(description="""Policy for the wan path""")]
    | None = None,
    tenant: Annotated[
        Optional[str],
        Field(description="""Tenant network in which the packet is sent"""),
    ]
    | None = None,
    path_type: Annotated[Optional[str], Field(description="""path_type of the port""")]
    | None = None,
    start: Annotated[
        Optional[int],
        Field(
            description="""Start datetime, can be epoch or relative time like -1d, -1w; -1d if not specified"""
        ),
    ]
    | None = None,
    end: Annotated[
        Optional[int],
        Field(
            description="""End datetime, can be epoch or relative time like -1d, -2h; now if not specified"""
        ),
    ]
    | None = None,
    duration: Annotated[
        str, Field(description="""Duration like 7d, 2w""", default="1d")
    ] = "1d",
    limit: Annotated[int, Field(default=100)] = 100,
    page: Annotated[int, Field(ge=1, default=1)] = 1,
) -> dict:
    """Search Site WAN Usages"""

    response = mistapi.api.v1.sites.wan_usages.searchSiteWanUsage(
        apisession,
        site_id=str(site_id),
        mac=mac,
        peer_mac=peer_mac,
        port_id=port_id,
        peer_port_id=peer_port_id,
        policy=policy,
        tenant=tenant,
        path_type=path_type,
        start=start,
        end=end,
        duration=duration,
        limit=limit,
        page=page,
    )

    ctx = get_context()

    if response.status_code != 200:
        error = {"status_code": response.status_code, "message": ""}
        if response.data:
            await ctx.error(
                f"Got HTTP{response.status_code} with details {response.data}"
            )
            error["message"] = json.dumps(response.data)
        elif response.status_code == 400:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] = json.dumps(
                "Bad Request. The API endpoint exists but its syntax/payload is incorrect, detail may be given"
            )
        elif response.status_code == 401:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] = json.dumps("Unauthorized")
        elif response.status_code == 403:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] = json.dumps("Unauthorized")
        elif response.status_code == 401:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] = json.dumps("Permission Denied")
        elif response.status_code == 404:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] = json.dumps(
                "Not found. The API endpoint doesn’t exist or resource doesn’t exist"
            )
        elif response.status_code == 429:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] = json.dumps(
                "Too Many Request. The API Token used for the request reached the 5000 API Calls per hour threshold"
            )
        raise ToolError(error)

    return response.data
