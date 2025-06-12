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
from enum import Enum


class Type(Enum):
    WAN = "wan"
    WXTUNNEL = "wxtunnel"


def add_tool() -> None:
    mcp.add_tool(
        fn=searchOrgTunnelsStats,
        name="searchOrgTunnelsStats",
        description="""Search Org Tunnels Stats""",
        tags={"Orgs Stats - Tunnels"},
        annotations={
            "title": "searchOrgTunnelsStats",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True,
        },
    )


def remove_tool() -> None:
    mcp.remove_tool("searchOrgTunnelsStats")


async def searchOrgTunnelsStats(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    mxcluster_id: Annotated[
        Optional[str], Field(description="""If `type`==`wxtunnel`""")
    ]
    | None = None,
    site_id: Annotated[Optional[str], Field(description="""ID of the Mist Site""")]
    | None = None,
    wxtunnel_id: Annotated[
        Optional[str], Field(description="""If `type`==`wxtunnel`""")
    ]
    | None = None,
    ap: Annotated[Optional[str], Field(description="""If `type`==`wxtunnel`""")]
    | None = None,
    mac: Annotated[Optional[str], Field(description="""If `type`==`wan`""")]
    | None = None,
    node: Annotated[Optional[str], Field(description="""If `type`==`wan`""")]
    | None = None,
    peer_ip: Annotated[Optional[str], Field(description="""If `type`==`wan`""")]
    | None = None,
    peer_host: Annotated[Optional[str], Field(description="""If `type`==`wan`""")]
    | None = None,
    ip: Annotated[Optional[str], Field(description="""If `type`==`wan`""")]
    | None = None,
    tunnel_name: Annotated[Optional[str], Field(description="""If `type`==`wan`""")]
    | None = None,
    protocol: Annotated[Optional[str], Field(description="""If `type`==`wan`""")]
    | None = None,
    auth_algo: Annotated[Optional[str], Field(description="""If `type`==`wan`""")]
    | None = None,
    encrypt_algo: Annotated[Optional[str], Field(description="""If `type`==`wan`""")]
    | None = None,
    ike_version: Annotated[Optional[str], Field(description="""If `type`==`wan`""")]
    | None = None,
    up: Annotated[Optional[str], Field(description="""If `type`==`wan`""")]
    | None = None,
    type: Type = Type.WXTUNNEL,
    limit: Annotated[int, Field(default=100)] = 100,
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
) -> dict:
    """Search Org Tunnels Stats"""

    response = mistapi.api.v1.orgs.stats.searchOrgTunnelsStats(
        apisession,
        org_id=str(org_id),
        mxcluster_id=mxcluster_id,
        site_id=site_id,
        wxtunnel_id=wxtunnel_id,
        ap=ap,
        mac=mac,
        node=node,
        peer_ip=peer_ip,
        peer_host=peer_host,
        ip=ip,
        tunnel_name=tunnel_name,
        protocol=protocol,
        auth_algo=auth_algo,
        encrypt_algo=encrypt_algo,
        ike_version=ike_version,
        up=up,
        type=type.value,
        limit=limit,
        start=start,
        end=end,
        duration=duration,
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
