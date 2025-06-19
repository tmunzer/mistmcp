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


class Distinct(Enum):
    AP = "ap"
    DEVICE = "device"
    HOSTNAME = "hostname"
    IP = "ip"
    MAC = "mac"
    MODEL = "model"
    OS = "os"
    SSID = "ssid"
    VLAN = "vlan"


@mcp.tool(
    enabled=True,
    name="countOrgWirelessClients",
    description="""Count by Distinct Attributes of Org Wireless Clients""",
    tags={"orgs_clients"},
    annotations={
        "title": "countOrgWirelessClients",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def countOrgWirelessClients(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    distinct: Distinct = Distinct.DEVICE,
    mac: Annotated[
        Optional[str], Field(description="""Partial / full MAC address""")
    ] = None,
    hostname: Annotated[
        Optional[str], Field(description="""Partial / full hostname""")
    ] = None,
    device: Annotated[
        Optional[str], Field(description="""Device type, e.g. Mac, Nvidia, iPhone""")
    ] = None,
    os: Annotated[
        Optional[str], Field(description="""OS, e.g. Sierra, Yosemite, Windows 10""")
    ] = None,
    model: Annotated[
        Optional[str],
        Field(description="""Model, e.g. 'MBP 15 late 2013', 6, 6s, '8+ GSM'"""),
    ] = None,
    ap: Annotated[
        Optional[str], Field(description="""AP mac where the client has connected to""")
    ] = None,
    vlan: Annotated[Optional[str], Field(description="""VLAN""")] = None,
    ssid: Annotated[Optional[str], Field(description="""SSID""")] = None,
    ip_address: Optional[str] = None,
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
    """Count by Distinct Attributes of Org Wireless Clients"""

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

    response = mistapi.api.v1.orgs.clients.countOrgWirelessClients(
        apisession,
        org_id=str(org_id),
        distinct=distinct.value,
        mac=mac,
        hostname=hostname,
        device=device,
        os=os,
        model=model,
        ap=ap,
        vlan=vlan,
        ssid=ssid,
        ip_address=ip_address,
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
