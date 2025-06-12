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


class Distinct(Enum):
    AP = "ap"
    DEVICE = "device"
    HOSTNAME = "hostname"
    IP = "ip"
    MODEL = "model"
    OS = "os"
    SSID = "ssid"
    VLAN = "vlan"


class Band(Enum):
    B24 = "24"
    B5 = "5"
    B6 = "6"
    NONE = None


def add_tool() -> None:
    mcp.add_tool(
        fn=countOrgWirelessClientsSessions,
        name="countOrgWirelessClientsSessions",
        description="""Count by Distinct Attributes of Org Wireless Clients Sessions""",
        tags={"Orgs Clients - Wireless"},
        annotations={
            "title": "countOrgWirelessClientsSessions",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True,
        },
    )


def remove_tool() -> None:
    mcp.remove_tool("countOrgWirelessClientsSessions")


async def countOrgWirelessClientsSessions(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    distinct: Distinct = Distinct.DEVICE,
    ap: Annotated[Optional[str], Field(description="""AP MAC""")] | None = None,
    band: Annotated[Band, Field(description="""802.11 Band""")] = Band.NONE,
    client_family: Annotated[
        Optional[str], Field(description="""E.g. 'Mac', 'iPhone', 'Apple watch'""")
    ]
    | None = None,
    client_manufacture: Annotated[Optional[str], Field(description="""E.g. 'Apple'""")]
    | None = None,
    client_model: Annotated[Optional[str], Field(description="""E.g. '8+', 'XS'""")]
    | None = None,
    client_os: Annotated[
        Optional[str], Field(description="""E.g. 'Mojave', 'Windows 10', 'Linux'""")
    ]
    | None = None,
    ssid: Annotated[Optional[str], Field(description="""SSID""")] | None = None,
    wlan_id: Annotated[Optional[str], Field(description="""WLAN_id""")] | None = None,
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
) -> dict:
    """Count by Distinct Attributes of Org Wireless Clients Sessions"""

    response = mistapi.api.v1.orgs.clients.countOrgWirelessClientsSessions(
        apisession,
        org_id=str(org_id),
        distinct=distinct.value,
        ap=ap,
        band=band.value,
        client_family=client_family,
        client_manufacture=client_manufacture,
        client_model=client_model,
        client_os=client_os,
        ssid=ssid,
        wlan_id=wlan_id,
        start=start,
        end=end,
        duration=duration,
        limit=limit,
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
