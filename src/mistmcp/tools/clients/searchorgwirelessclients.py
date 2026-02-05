"""
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


mcp = mcp_instance.get()


@mcp.tool(
    enabled=False,
    name="searchOrgWirelessClients",
    description="""Search Org Wireless Clients""",
    tags={"clients"},
    annotations={
        "title": "searchOrgWirelessClients",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchOrgWirelessClients(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    site_id: Annotated[Optional[UUID | None], Field(description="""Site ID""")] = None,
    mac: Annotated[
        Optional[str | None], Field(description="""Partial / full MAC address""")
    ] = None,
    ip: Optional[str | None] = None,
    hostname: Annotated[
        Optional[str | None], Field(description="""Partial / full hostname""")
    ] = None,
    band: Annotated[
        Optional[str | None], Field(description="""Radio band. enum: `24`, `5`, `6`""")
    ] = None,
    device: Annotated[
        Optional[str | None],
        Field(description="""Device type, e.g. Mac, Nvidia, iPhone"""),
    ] = None,
    os: Annotated[
        Optional[str | None],
        Field(
            description="""Only available for clients running the Marvis Client app, os, e.g. Sierra, Yosemite, Windows 10"""
        ),
    ] = None,
    model: Annotated[
        Optional[str | None],
        Field(
            description="""Only available for clients running the Marvis Client app, model, e.g. 'MBP 15 late 2013', 6, 6s, '8+ GSM'"""
        ),
    ] = None,
    ap: Annotated[
        Optional[str | None],
        Field(description="""AP mac where the client has connected to"""),
    ] = None,
    psk_id: Annotated[Optional[str | None], Field(description="""PSK ID""")] = None,
    psk_name: Annotated[
        Optional[str | None],
        Field(
            description="""Only available for clients using PPSK authentication, the Name of the PSK"""
        ),
    ] = None,
    username: Annotated[
        Optional[str | None],
        Field(
            description="""Only available for clients using 802.1X authentication, partial / full username"""
        ),
    ] = None,
    vlan: Annotated[Optional[str | None], Field(description="""VLAN""")] = None,
    ssid: Annotated[Optional[str | None], Field(description="""SSID""")] = None,
    text: Annotated[
        Optional[str | None],
        Field(
            description="""Partial / full MAC address, hostname, username, psk_name or ip"""
        ),
    ] = None,
    limit: Optional[int | None] = None,
    start: Annotated[
        Optional[str | None],
        Field(
            description="""Start time (epoch timestamp in seconds, or relative string like '-1d', '-1w')"""
        ),
    ] = None,
    end: Annotated[
        Optional[str | None],
        Field(
            description="""End time (epoch timestamp in seconds, or relative string like '-1d', '-2h', 'now')"""
        ),
    ] = None,
    duration: Annotated[
        Optional[str | None], Field(description="""Duration like 7d, 2w""")
    ] = None,
    sort: Annotated[
        Optional[str | None],
        Field(
            description="""On which field the list should be sorted, -prefix represents DESC order"""
        ),
    ] = None,
    search_after: Annotated[
        Optional[str | None],
        Field(
            description="""Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed."""
        ),
    ] = None,
) -> dict | list:
    """Search Org Wireless Clients"""

    ctx = get_context()
    if config.transport_mode == "http":
        try:
            apitoken = ""
            request: Request = get_http_request()
            cloud = (
                request.query_params.get("cloud", None)
                .replace("https://", "")
                .replace("http://", "")
            )
            if request.headers.get("Authorization", None):
                apitoken = request.headers.get("Authorization", "").replace(
                    "Bearer ", ""
                )
            else:
                apitoken = request.headers.get("X-Authorization", "").replace(
                    "Bearer ", ""
                )
        except NotFoundError as exc:
            raise ClientError(
                "HTTP request context not found. Are you using HTTP transport?"
            ) from exc
        if not cloud or not apitoken:
            raise ClientError(
                "Missing required parameters: 'cloud' and 'Authorization' or 'X-Authorization' header"
            )
    else:
        apitoken = config.mist_apitoken
        cloud = config.mist_host

    if not apitoken:
        raise ClientError(
            "Missing required parameter: 'Authorization' or 'X-Authorization' header or mist_apitoken in config"
        )
    if not cloud:
        raise ClientError(
            "Missing required parameter: 'cloud' query parameter or mist_host in config"
        )

    apisession = mistapi.APISession(
        host=cloud,
        apitoken=apitoken,
    )

    response = mistapi.api.v1.orgs.clients.searchOrgWirelessClients(
        apisession,
        org_id=str(org_id),
        site_id=str(site_id) if site_id else None,
        mac=mac if mac else None,
        ip=ip if ip else None,
        hostname=hostname if hostname else None,
        band=band if band else None,
        device=device if device else None,
        os=os if os else None,
        model=model if model else None,
        ap=ap if ap else None,
        psk_id=psk_id if psk_id else None,
        psk_name=psk_name if psk_name else None,
        username=username if username else None,
        vlan=vlan if vlan else None,
        ssid=ssid if ssid else None,
        text=text if text else None,
        limit=limit if limit else None,
        start=start if start else None,
        end=end if end else None,
        duration=duration if duration else None,
        sort=sort if sort else None,
        search_after=search_after if search_after else None,
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
                "Not found. The API endpoint doesn't exist or resource doesn't exist"
            )
        elif response.status_code == 429:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps(
                "Too Many Request. The API Token used for the request reached the 5000 API Calls per hour threshold"
            )
        raise ToolError(api_error)

    return response.data
