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
from typing import Annotated
from uuid import UUID
from enum import Enum


mcp = mcp_instance.get()


class Distinct(Enum):
    AP = "ap"
    AUTH_ALGO = "auth_algo"
    ENCRYPT_ALGO = "encrypt_algo"
    IKE_VERSION = "ike_version"
    IP = "ip"
    LAST_EVENT = "last_event"
    MAC = "mac"
    MXCLUSTER_ID = "mxcluster_id"
    MXEDGE_ID = "mxedge_id"
    NODE = "node"
    PEER_HOST = "peer_host"
    PEER_IP = "peer_ip"
    PEER_MXEDGE_ID = "peer_mxedge_id"
    PROTOCOL = "protocol"
    REMOTE_IP = "remote_ip"
    REMOTE_PORT = "remote_port"
    SITE_ID = "site_id"
    STATE = "state"
    TUNNEL_NAME = "tunnel_name"
    UP = "up"
    WXTUNNEL_ID = "wxtunnel_id"


class Type(Enum):
    WAN = "wan"
    WXTUNNEL = "wxtunnel"


@mcp.tool(
    enabled=True,
    name="countOrgTunnelsStats",
    description="""Count by Distinct Attributes of Mist Tunnels Stats""",
    tags={"Orgs Stats - Tunnels"},
    annotations={
        "title": "countOrgTunnelsStats",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def countOrgTunnelsStats(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    distinct: Annotated[
        Distinct,
        Field(
            description="""- If `type`==`wxtunnel`: wxtunnel_id / ap / remote_ip / remote_port / state / mxedge_id / mxcluster_id / site_id / peer_mxedge_id; default is wxtunnel_id  - If `type`==`wan`: mac / site_id / node / peer_ip / peer_host/ ip / tunnel_name / protocol / auth_algo / encrypt_algo / ike_version / last_event / up"""
        ),
    ] = Distinct.WXTUNNEL_ID,
    type: Type = Type.WXTUNNEL,
    limit: Annotated[int, Field(default=100)] = 100,
) -> dict:
    """Count by Distinct Attributes of Mist Tunnels Stats"""

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

    response = mistapi.api.v1.orgs.stats.countOrgTunnelsStats(
        apisession,
        org_id=str(org_id),
        distinct=distinct.value,
        type=type.value,
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
