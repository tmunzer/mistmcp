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

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


mcp = mcp_instance.get()


class Type(Enum):
    ALL = "all"
    AP = "ap"
    GATEWAY = "gateway"
    SWITCH = "switch"


class Status(Enum):
    ALL = "all"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


@mcp.tool(
    enabled=True,
    name="listOrgDevicesStats",
    description="""Get List of Org Devices statsThis API renders some high-level device stats, pagination is assumed and returned in response header (as the response is an array)""",
    tags={"orgs_stats"},
    annotations={
        "title": "listOrgDevicesStats",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def listOrgDevicesStats(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    type: Type = Type.AP,
    status: Status = Status.ALL,
    site_id: Annotated[
        Optional[str], Field(description="""ID of the Mist Site""")
    ] = None,
    mac: Optional[str] = None,
    evpntopo_id: Annotated[
        Optional[str], Field(description="""EVPN Topology ID""")
    ] = None,
    evpn_unused: Annotated[
        Optional[str],
        Field(
            description="""If `evpn_unused`==`true`, find EVPN eligible switches which don’t belong to any EVPN Topology yet"""
        ),
    ] = None,
    fields: Annotated[
        Optional[str],
        Field(
            description="""List of additional fields requests, comma separated, or `fields=*` for all of them"""
        ),
    ] = None,
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
    limit: Annotated[int, Field(default=100)] = 100,
    page: Annotated[int, Field(ge=1, default=1)] = 1,
) -> dict:
    """Get List of Org Devices statsThis API renders some high-level device stats, pagination is assumed and returned in response header (as the response is an array)"""

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

    response = mistapi.api.v1.orgs.stats.listOrgDevicesStats(
        apisession,
        org_id=str(org_id),
        type=type.value,
        status=status.value,
        site_id=site_id,
        mac=mac,
        evpntopo_id=evpntopo_id,
        evpn_unused=evpn_unused,
        fields=fields,
        start=start,
        end=end,
        duration=duration,
        limit=limit,
        page=page,
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
