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
from typing import Annotated
from uuid import UUID
from enum import Enum


class Band(Enum):
    B24 = "24"
    B5 = "5"
    B6 = "6"


def add_tool() -> None:
    mcp.add_tool(
        fn=getSiteCurrentRrmConsiderations,
        name="getSiteCurrentRrmConsiderations",
        description="""Get Current RRM Considerations for an AP on a Specific Band""",
        tags={"Sites RRM"},
        annotations={
            "title": "getSiteCurrentRrmConsiderations",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True,
        },
    )


def remove_tool() -> None:
    mcp.remove_tool("getSiteCurrentRrmConsiderations")


async def getSiteCurrentRrmConsiderations(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    device_id: Annotated[UUID, Field(description="""ID of the Mist Device""")],
    band: Annotated[Band, Field(description="""802.11 Band""")],
) -> dict:
    """Get Current RRM Considerations for an AP on a Specific Band"""

    response = mistapi.api.v1.sites.rrm.getSiteCurrentRrmConsiderations(
        apisession,
        site_id=str(site_id),
        device_id=str(device_id),
        band=band.value,
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
