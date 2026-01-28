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


class Band(Enum):
    B24 = "24"
    B5 = "5"
    B6 = "6"
    NONE = None


@mcp.tool(
    enabled=False,
    name="searchOrgWirelessClientSessions",
    description="""Search Org Wireless Clients Sessions""",
    tags={"clients"},
    annotations={
        "title": "searchOrgWirelessClientSessions",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchOrgWirelessClientSessions(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    ap: Annotated[Optional[str], Field(description="""AP MAC""")] = None,
    band: Annotated[Optional[Band], Field(description="""802.11 Band""")] = Band.NONE,
    client_family: Annotated[
        Optional[str], Field(description="""E.g. 'Mac', 'iPhone', 'Apple watch'""")
    ] = None,
    client_manufacture: Annotated[
        Optional[str], Field(description="""E.g. 'Apple'""")
    ] = None,
    client_model: Annotated[
        Optional[str], Field(description="""E.g. '8+', 'XS'""")
    ] = None,
    client_username: Annotated[Optional[str], Field(description="""Username""")] = None,
    client_os: Annotated[
        Optional[str], Field(description="""E.g. 'Mojave', 'Windows 10', 'Linux'""")
    ] = None,
    ssid: Annotated[Optional[str], Field(description="""SSID""")] = None,
    wlan_id: Annotated[Optional[UUID], Field(description="""WLAN_id""")] = None,
    psk_id: Annotated[Optional[str], Field(description="""PSK ID""")] = None,
    psk_name: Annotated[Optional[str], Field(description="""PSK Name""")] = None,
    limit: Optional[int] = None,
    start: Annotated[
        Optional[str],
        Field(
            description="""Start time (epoch timestamp in seconds, or relative string like '-1d', '-1w')"""
        ),
    ] = None,
    end: Annotated[
        Optional[str],
        Field(
            description="""End time (epoch timestamp in seconds, or relative string like '-1d', '-2h', 'now')"""
        ),
    ] = None,
    duration: Annotated[
        Optional[str], Field(description="""Duration like 7d, 2w""")
    ] = None,
    sort: Annotated[
        Optional[str],
        Field(
            description="""On which field the list should be sorted, -prefix represents DESC order"""
        ),
    ] = None,
    search_after: Annotated[
        Optional[str],
        Field(
            description="""Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed."""
        ),
    ] = None,
) -> dict | list:
    """Search Org Wireless Clients Sessions"""

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

    if not apitoken:
        raise ClientError(
            "Missing required parameter: 'X-Authorization' header or mist_apitoken in config"
        )
    if not cloud:
        raise ClientError(
            "Missing required parameter: 'cloud' query parameter or mist_host in config"
        )

    apisession = mistapi.APISession(
        host=cloud,
        apitoken=apitoken,
    )

    response = mistapi.api.v1.orgs.clients.searchOrgWirelessClientSessions(
        apisession,
        org_id=str(org_id),
        ap=ap,
        band=band.value if band else None,
        client_family=client_family,
        client_manufacture=client_manufacture,
        client_model=client_model,
        client_username=client_username,
        client_os=client_os,
        ssid=ssid,
        wlan_id=str(wlan_id) if wlan_id else None,
        psk_id=psk_id,
        psk_name=psk_name,
        limit=limit,
        start=start,
        end=end,
        duration=duration,
        sort=sort,
        search_after=search_after,
    )

    if response.status_code != 200:
        api_error = {"status_code": response.status_code, "message": ""}
        if response.data:
            # await ctx.error(f"Got HTTP{response.status_code} with details {response.data}")
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
