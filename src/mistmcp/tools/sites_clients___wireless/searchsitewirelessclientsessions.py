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


class Band(Enum):
    B24 = "24"
    B5 = "5"
    B6 = "6"
    NONE = None


@mcp.tool(
    enabled=True,
    name="searchSiteWirelessClientSessions",
    description="""Search Client Sessions""",
    tags={"Sites Clients - Wireless"},
    annotations={
        "title": "searchSiteWirelessClientSessions",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchSiteWirelessClientSessions(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    ap: Annotated[Optional[str], Field(description="""AP MAC""")] = None,
    band: Annotated[Band, Field(description="""802.11 Band""")] = Band.NONE,
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
    wlan_id: Annotated[Optional[str], Field(description="""WLAN_id""")] = None,
    psk_id: Annotated[Optional[str], Field(description="""PSK ID""")] = None,
    psk_name: Annotated[Optional[str], Field(description="""PSK Name""")] = None,
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
) -> dict:
    """Search Client Sessions"""

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
        if not apitoken.startswith("Bearer "):
            raise ClientError("X-Authorization header must start with 'Bearer ' prefix")
    else:
        apitoken = config.mist_apitoken
        cloud = config.mist_host

    apisession = mistapi.APISession(
        host=cloud,
        apitoken=apitoken,
    )

    response = mistapi.api.v1.sites.clients.searchSiteWirelessClientSessions(
        apisession,
        site_id=str(site_id),
        ap=ap,
        band=band.value,
        client_family=client_family,
        client_manufacture=client_manufacture,
        client_model=client_model,
        client_username=client_username,
        client_os=client_os,
        ssid=ssid,
        wlan_id=wlan_id,
        psk_id=psk_id,
        psk_name=psk_name,
        limit=limit,
        start=start,
        end=end,
        duration=duration,
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
