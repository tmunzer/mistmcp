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


class Scope(Enum):
    AP = "ap"
    CLIENT = "client"
    GATEWAY = "gateway"
    SITE = "site"
    SWITCH = "switch"


class Fields(Enum):
    AP = "ap"
    BAND = "band"
    CHASSIS = "chassis"
    CLIENT = "client"
    DEVICE_OS = "device_os"
    DEVICE_TYPE = "device_type"
    GATEWAY = "gateway"
    GATEWAY_ZONES = "gateway_zones"
    INTERFACE = "interface"
    MXEDGE = "mxedge"
    PEER_PATH = "peer_path"
    SERVER = "server"
    SWITCH = "switch"
    VLAN = "vlan"
    WLAN = "wlan"
    NONE = None


def add_tool() -> None:
    mcp.add_tool(
        fn=getSiteSleImpactSummary,
        name="getSiteSleImpactSummary",
        description="""Get impact summary counts optionally filtered by classifier and failure type * Wireless SLE Fields: `wlan`, `device_type`, `device_os` ,`band`, `ap`, `server`, `mxedge`* Wired SLE Fields: `switch`, `client`, `vlan`, `interface`, `chassis`* WAN SLE Fields: `gateway`, `client`, `interface`, `chassis`, `peer_path`, `gateway_zones`""",
        tags={"Sites SLEs"},
        annotations={
            "title": "getSiteSleImpactSummary",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True,
        },
    )


def remove_tool() -> None:
    mcp.remove_tool("getSiteSleImpactSummary")


async def getSiteSleImpactSummary(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    scope: Scope,
    scope_id: Annotated[
        str,
        Field(
            description="""* site_id if `scope`==`site` * device_id if `scope`==`ap`, `scope`==`switch` or `scope`==`gateway` * mac if `scope`==`client`"""
        ),
    ],
    metric: Annotated[str, Field(description="""values from listSiteSlesMetrics""")],
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
    fields: Fields = Fields.NONE,
    classifier: Optional[str] | None = None,
) -> dict:
    """Get impact summary counts optionally filtered by classifier and failure type * Wireless SLE Fields: `wlan`, `device_type`, `device_os` ,`band`, `ap`, `server`, `mxedge`* Wired SLE Fields: `switch`, `client`, `vlan`, `interface`, `chassis`* WAN SLE Fields: `gateway`, `client`, `interface`, `chassis`, `peer_path`, `gateway_zones`"""

    response = mistapi.api.v1.sites.sle.getSiteSleImpactSummary(
        apisession,
        site_id=str(site_id),
        scope=scope.value,
        scope_id=scope_id,
        metric=metric,
        start=start,
        end=end,
        duration=duration,
        fields=fields.value,
        classifier=classifier,
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
