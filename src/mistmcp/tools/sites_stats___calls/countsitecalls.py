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
    MAC = "mac"


def add_tool() -> None:
    mcp.add_tool(
        fn=countSiteCalls,
        name="countSiteCalls",
        description="""Count by Distinct Attributes of Calls""",
        tags={"Sites Stats - Calls"},
        annotations={
            "title": "countSiteCalls",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True,
        },
    )


def remove_tool() -> None:
    mcp.remove_tool("countSiteCalls")


async def countSiteCalls(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    distinct: Distinct = Distinct.MAC,
    rating: Annotated[
        Optional[int],
        Field(
            description="""Feedback rating (e.g. 'rating=1' or 'rating=1,2')""",
            ge=1,
            le=5,
        ),
    ]
    | None = None,
    app: Optional[str] | None = None,
    start: Optional[str] | None = None,
    end: Optional[str] | None = None,
    limit: Annotated[int, Field(default=100)] = 100,
) -> dict:
    """Count by Distinct Attributes of Calls"""

    response = mistapi.api.v1.sites.stats.countSiteCalls(
        apisession,
        site_id=str(site_id),
        distinct=distinct.value,
        rating=rating,
        app=app,
        start=start,
        end=end,
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
