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


mcp = mcp_instance.get()


@mcp.tool(
    enabled=True,
    name="searchSiteServicePathEvents",
    description="""Search Service Path Events""",
    tags={"Sites Services"},
    annotations={
        "title": "searchSiteServicePathEvents",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchSiteServicePathEvents(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    type: Annotated[
        Optional[str], Field(description="""Event type, e.g. GW_SERVICE_PATH_DOWN""")
    ] = None,
    text: Annotated[
        Optional[str],
        Field(
            description="""Description of the event including the reason it is triggered"""
        ),
    ] = None,
    peer_port_id: Annotated[
        Optional[str], Field(description="""Port ID of the peer gateway""")
    ] = None,
    peer_mac: Annotated[
        Optional[str], Field(description="""MAC address of the peer gateway""")
    ] = None,
    vpn_name: Annotated[Optional[str], Field(description="""Peer name""")] = None,
    vpn_path: Annotated[Optional[str], Field(description="""Peer path name""")] = None,
    policy: Annotated[
        Optional[str],
        Field(description="""Service policy associated with that specific path"""),
    ] = None,
    port_id: Annotated[
        Optional[str], Field(description="""Network interface""")
    ] = None,
    model: Annotated[Optional[str], Field(description="""Device model""")] = None,
    version: Annotated[
        Optional[str], Field(description="""Device firmware version""")
    ] = None,
    timestamp: Annotated[
        Optional[float], Field(description="""Start time, in epoch""")
    ] = None,
    mac: Annotated[Optional[str], Field(description="""MAC address""")] = None,
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
) -> dict:
    """Search Service Path Events"""

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

    response = mistapi.api.v1.sites.services.searchSiteServicePathEvents(
        apisession,
        site_id=str(site_id),
        type=type,
        text=text,
        peer_port_id=peer_port_id,
        peer_mac=peer_mac,
        vpn_name=vpn_name,
        vpn_path=vpn_path,
        policy=policy,
        port_id=port_id,
        model=model,
        version=version,
        timestamp=timestamp,
        mac=mac,
        start=start,
        end=end,
        duration=duration,
        limit=limit,
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
