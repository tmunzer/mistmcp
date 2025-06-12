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


class Device_type(Enum):
    ALL = "all"
    AP = "ap"
    GATEWAY = "gateway"
    SWITCH = "switch"


def add_tool() -> None:
    mcp.add_tool(
        fn=searchOrgDeviceEvents,
        name="searchOrgDeviceEvents",
        description="""Search Org Devices Events""",
        tags={"Orgs Devices"},
        annotations={
            "title": "searchOrgDeviceEvents",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True,
        },
    )


def remove_tool() -> None:
    mcp.remove_tool("searchOrgDeviceEvents")


async def searchOrgDeviceEvents(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    mac: Annotated[Optional[str], Field(description="""Device mac""")] | None = None,
    model: Annotated[Optional[str], Field(description="""Device model""")]
    | None = None,
    device_type: Device_type = Device_type.AP,
    text: Annotated[Optional[str], Field(description="""Event message""")]
    | None = None,
    timestamp: Annotated[Optional[str], Field(description="""Event time""")]
    | None = None,
    type: Annotated[
        Optional[str], Field(description="""See `listDeviceEventsDefinitions`""")
    ]
    | None = None,
    last_by: Annotated[
        Optional[str],
        Field(description="""Return last/recent event for passed in field"""),
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
    """Search Org Devices Events"""

    response = mistapi.api.v1.orgs.devices.searchOrgDeviceEvents(
        apisession,
        org_id=str(org_id),
        mac=mac,
        model=model,
        device_type=device_type.value,
        text=text,
        timestamp=timestamp,
        type=type,
        last_by=last_by,
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
