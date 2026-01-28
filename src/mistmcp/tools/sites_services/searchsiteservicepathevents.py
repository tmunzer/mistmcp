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


mcp = mcp_instance.get()


@mcp.tool(
    enabled=False,
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
        Optional[str | None],
        Field(description="""Event type, e.g. GW_SERVICE_PATH_DOWN"""),
    ] = None,
    text: Annotated[
        Optional[str | None],
        Field(
            description="""Description of the event including the reason it is triggered"""
        ),
    ] = None,
    peer_port_id: Annotated[
        Optional[str | None], Field(description="""Port ID of the peer gateway""")
    ] = None,
    peer_mac: Annotated[
        Optional[str | None], Field(description="""MAC address of the peer gateway""")
    ] = None,
    vpn_name: Annotated[
        Optional[str | None], Field(description="""Peer name""")
    ] = None,
    vpn_path: Annotated[
        Optional[str | None], Field(description="""Peer path name""")
    ] = None,
    policy: Annotated[
        Optional[str | None],
        Field(description="""Service policy associated with that specific path"""),
    ] = None,
    port_id: Annotated[
        Optional[str | None], Field(description="""Network interface""")
    ] = None,
    model: Annotated[
        Optional[str | None], Field(description="""Device model""")
    ] = None,
    version: Annotated[
        Optional[str | None], Field(description="""Device firmware version""")
    ] = None,
    timestamp: Annotated[
        Optional[float | None], Field(description="""Start time, in epoch""")
    ] = None,
    mac: Annotated[Optional[str | None], Field(description="""MAC address""")] = None,
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

    response = mistapi.api.v1.sites.services.searchSiteServicePathEvents(
        apisession,
        site_id=str(site_id),
        type=type if type else None,
        text=text if text else None,
        peer_port_id=peer_port_id if peer_port_id else None,
        peer_mac=peer_mac if peer_mac else None,
        vpn_name=vpn_name if vpn_name else None,
        vpn_path=vpn_path if vpn_path else None,
        policy=policy if policy else None,
        port_id=port_id if port_id else None,
        model=model if model else None,
        version=version if version else None,
        timestamp=timestamp if timestamp else None,
        mac=mac if mac else None,
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
                "Not found. The API endpoint doesn’t exist or resource doesn’t exist"
            )
        elif response.status_code == 429:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps(
                "Too Many Request. The API Token used for the request reached the 5000 API Calls per hour threshold"
            )
        raise ToolError(api_error)

    return response.data
