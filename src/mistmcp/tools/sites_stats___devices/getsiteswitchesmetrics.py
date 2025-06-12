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
    ACTIVE_PORTS_SUMMARY = "active_ports_summary"
    NONE = None


class Scope(Enum):
    SITE = "site"
    SWITCH = "switch"
    NONE = None


def add_tool() -> None:
    mcp.add_tool(
        fn=getSiteSwitchesMetrics,
        name="getSiteSwitchesMetrics",
        description="""Get version compliance metrics for managed or monitored switches""",
        tags={"Sites Stats - Devices"},
        annotations={
            "title": "getSiteSwitchesMetrics",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True,
        },
    )


def remove_tool() -> None:
    mcp.remove_tool("getSiteSwitchesMetrics")


async def getSiteSwitchesMetrics(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    type: Type = Type.NONE,
    scope: Scope = Scope.NONE,
    switch_mac: Annotated[
        Optional[str],
        Field(
            description="""Switch mac, used only with metric `type`==`active_ports_summary`"""
        ),
    ]
    | None = None,
) -> dict:
    """Get version compliance metrics for managed or monitored switches"""

    response = mistapi.api.v1.sites.stats.getSiteSwitchesMetrics(
        apisession,
        site_id=str(site_id),
        type=type.value,
        scope=scope.value,
        switch_mac=switch_mac,
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
