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
from fastmcp.server.dependencies import get_context, get_http_request
from fastmcp.exceptions import ToolError, ClientError, NotFoundError
from starlette.requests import Request
from mistmcp.config import config
from mistmcp.server_factory import mcp_instance
# from mistmcp.server_factory import mcp

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


mcp = mcp_instance.get()


class Type(Enum):
    HONEYPOT = "honeypot"
    LAN = "lan"
    OTHERS = "others"
    SPOOF = "spoof"
    NONE = None


@mcp.tool(
    enabled=False,
    name="listSiteRogueAPs",
    description="""Get List of Site Rogue/Neighbor APs""",
    tags={"Sites Rogues"},
    annotations={
        "title": "listSiteRogueAPs",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def listSiteRogueAPs(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    type: Type = Type.NONE,
    limit: Annotated[int, Field(default=100)] = 100,
    start: Annotated[
        Optional[int],
        Field(
            description="""Start datetime, can be epoch or relative time like -1d, -1w; -1d if not specified"""
        ),
    ] = None,
    end: Annotated[
        Optional[int],
        Field(
            description="""End datetime, can be epoch or relative time like -1d, -2h; now if not specified"""
        ),
    ] = None,
    duration: Annotated[
        str, Field(description="""Duration like 7d, 2w""", default="1d")
    ] = "1d",
    interval: Annotated[
        Optional[str],
        Field(
            description="""Aggregation works by giving a time range plus interval (e.g. 1d, 1h, 10m) where aggregation function would be applied to."""
        ),
    ] = None,
    rogue_bssid: Annotated[
        Optional[str],
        Field(
            description="""BSSID of the rogue AP to filter stats by. Optional, if not provided all rogue APs will be listed."""
        ),
    ] = None,
) -> dict:
    """Get List of Site Rogue/Neighbor APs"""

    ctx = get_context()
    if config.transport_mode == "http":
        try:
            request: Request = get_http_request()
            cloud = request.query_params.get("cloud", None)
            apitoken = request.headers.get("X-Authorization", None)
        except NotFoundError as exc:
            raise ClientError(
                "HTTP request context not found. Are you using HTTP transport?"
            ) from exc
        if not cloud or not apitoken:
            raise ClientError(
                "Missing required parameters: 'cloud' and 'X-Authorization' header"
            )
    else:
        apitoken = config.mist_apitoken
        cloud = config.mist_host

    apisession = mistapi.APISession(
        host=cloud,
        apitoken=apitoken,
    )

    if rogue_bssid:
        response = mistapi.api.v1.sites.rogues.getSiteRogueAP(
            apisession, site_id=str(site_id), rogue_bssid=rogue_bssid
        )
    else:
        response = mistapi.api.v1.sites.insights.listSiteRogueAPs(
            apisession,
            site_id=str(site_id),
            type=type.value,
            limit=limit,
            start=start,
            end=end,
            duration=duration,
            interval=interval,
        )

    if response.status_code != 200:
        api_error = {"status_code": response.status_code, "message": ""}
        if response.data:
            await ctx.error(
                f"Got HTTP{response.status_code} with details {response.data}"
            )
            api_error["message"] = json.dumps(response.data)
        elif response.status_code == 400:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps(
                "Bad Request. The API endpoint exists but its syntax/payload is incorrect, detail may be given"
            )
        elif response.status_code == 401:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps("Unauthorized")
        elif response.status_code == 403:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps("Unauthorized")
        elif response.status_code == 401:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps("Permission Denied")
        elif response.status_code == 404:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps(
                "Not found. The API endpoint doesn’t exist or resource doesn’t exist"
            )
        elif response.status_code == 429:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps(
                "Too Many Request. The API Token used for the request reached the 5000 API Calls per hour threshold"
            )
        raise ToolError(api_error)

    return response.data
