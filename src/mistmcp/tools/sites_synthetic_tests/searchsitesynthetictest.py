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
    ARP = "arp"
    CURL = "curl"
    DHCP = "dhcp"
    DHCP6 = "dhcp6"
    DNS = "dns"
    LAN_CONNECTIVITY = "lan_connectivity"
    RADIUS = "radius"
    SPEEDTEST = "speedtest"
    NONE = None


class Protocol(Enum):
    PING = "ping"
    TRACEROUTE = "traceroute"
    NONE = None


@mcp.tool(
    enabled=True,
    name="searchSiteSyntheticTest",
    description="""Search Site Synthetic Testing""",
    tags={"Sites Synthetic Tests"},
    annotations={
        "title": "searchSiteSyntheticTest",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchSiteSyntheticTest(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    mac: Annotated[Optional[str], Field(description="""Device MAC Address""")] = None,
    port_id: Annotated[
        Optional[str],
        Field(description="""Port_id used to run the test (for SSR only)"""),
    ] = None,
    vlan_id: Annotated[Optional[str], Field(description="""VLAN ID""")] = None,
    by: Annotated[
        Optional[str], Field(description="""Entity who triggers the test""")
    ] = None,
    reason: Annotated[
        Optional[str], Field(description="""Test failure reason""")
    ] = None,
    type: Annotated[Type, Field(description="""Synthetic test type""")] = Type.NONE,
    protocol: Annotated[
        Protocol, Field(description="""Connectivity protocol""")
    ] = Protocol.NONE,
    tenant: Annotated[
        Optional[str],
        Field(description="""Tenant network in which lan_connectivity test was run"""),
    ] = None,
) -> dict:
    """Search Site Synthetic Testing"""

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

    response = mistapi.api.v1.sites.synthetic_test.searchSiteSyntheticTest(
        apisession,
        site_id=str(site_id),
        mac=mac,
        port_id=port_id,
        vlan_id=vlan_id,
        by=by,
        reason=reason,
        type=type.value,
        protocol=protocol.value,
        tenant=tenant,
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
