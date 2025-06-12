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
        fn=searchOrgWirelessClients,
        name="searchOrgWirelessClients",
        description="""Search Org Wireless Clients""",
        tags={"Orgs Clients - Wireless"},
        annotations={
            "title": "searchOrgWirelessClients",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True,
        },
    )


def remove_tool() -> None:
    mcp.remove_tool("searchOrgWirelessClients")


async def searchOrgWirelessClients(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    site_id: Annotated[Optional[str], Field(description="""Site ID""")] | None = None,
    mac: Annotated[Optional[str], Field(description="""Partial / full MAC address""")]
    | None = None,
    ip_address: Optional[str] | None = None,
    hostname: Annotated[Optional[str], Field(description="""Partial / full hostname""")]
    | None = None,
    band: Annotated[
        Optional[str], Field(description="""Radio band. enum: `24`, `5`, `6`""")
    ]
    | None = None,
    device: Annotated[
        Optional[str], Field(description="""Device type, e.g. Mac, Nvidia, iPhone""")
    ]
    | None = None,
    os: Annotated[
        Optional[str],
        Field(
            description="""Only available for clients running the Marvis Client app, os, e.g. Sierra, Yosemite, Windows 10"""
        ),
    ]
    | None = None,
    model: Annotated[
        Optional[str],
        Field(
            description="""Only available for clients running the Marvis Client app, model, e.g. 'MBP 15 late 2013', 6, 6s, '8+ GSM'"""
        ),
    ]
    | None = None,
    ap: Annotated[
        Optional[str], Field(description="""AP mac where the client has connected to""")
    ]
    | None = None,
    psk_id: Annotated[Optional[str], Field(description="""PSK ID""")] | None = None,
    psk_name: Annotated[
        Optional[str],
        Field(
            description="""Only available for clients using PPSK authentication, the Name of the PSK"""
        ),
    ]
    | None = None,
    username: Annotated[
        Optional[str],
        Field(
            description="""Only available for clients using 802.1X authentication, partial / full username"""
        ),
    ]
    | None = None,
    vlan: Annotated[Optional[str], Field(description="""VLAN""")] | None = None,
    ssid: Annotated[Optional[str], Field(description="""SSID""")] | None = None,
    text: Annotated[
        Optional[str],
        Field(
            description="""Partial / full MAC address, hostname, username, psk_name or ip"""
        ),
    ]
    | None = None,
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
    """Search Org Wireless Clients"""

    response = mistapi.api.v1.orgs.clients.searchOrgWirelessClients(
        apisession,
        org_id=str(org_id),
        site_id=site_id,
        mac=mac,
        ip_address=ip_address,
        hostname=hostname,
        band=band,
        device=device,
        os=os,
        model=model,
        ap=ap,
        psk_id=psk_id,
        psk_name=psk_name,
        username=username,
        vlan=vlan,
        ssid=ssid,
        text=text,
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
