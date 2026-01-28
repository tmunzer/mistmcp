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
    WAN = "wan"
    WIRED = "wired"
    WIRELESS = "wireless"
    NONE = None


@mcp.tool(
    enabled=False,
    name="troubleshootOrg",
    description="""Troubleshoot sites, devices, clients, and wired clients for maximum of last 7 days from current time. See search APIs for device information:- [search Device](/#operations/searchOrgDevices)- [search Wireless Client](/#operations/searchOrgWirelessClients)- [search Wired Client](/#operations/searchOrgWiredClients)- [search Wan Client](/#operations/searchOrgWanClients)**NOTE**: requires Marvis subscription license""",
    tags={"marvis"},
    annotations={
        "title": "troubleshootOrg",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def troubleshootOrg(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    mac: Annotated[
        Optional[str],
        Field(description="""**required** when troubleshooting device or a client"""),
    ],
    site_id: Annotated[
        Optional[UUID], Field(description="""**required** when troubleshooting site""")
    ],
    start: Annotated[
        Optional[str],
        Field(
            description="""Start time (epoch timestamp in seconds, or relative string like '-1d', '-1w')"""
        ),
    ],
    end: Annotated[
        Optional[str],
        Field(
            description="""End time (epoch timestamp in seconds, or relative string like '-1d', '-2h', 'now')"""
        ),
    ],
    type: Annotated[
        Optional[Type],
        Field(
            description="""When troubleshooting site, type of network to troubleshoot"""
        ),
    ],
) -> dict | list:
    """Troubleshoot sites, devices, clients, and wired clients for maximum of last 7 days from current time. See search APIs for device information:- [search Device](/#operations/searchOrgDevices)- [search Wireless Client](/#operations/searchOrgWirelessClients)- [search Wired Client](/#operations/searchOrgWiredClients)- [search Wan Client](/#operations/searchOrgWanClients)**NOTE**: requires Marvis subscription license"""

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

    response = mistapi.api.v1.orgs.troubleshoot.troubleshootOrg(
        apisession,
        org_id=str(org_id),
        mac=mac if mac else None,
        site_id=str(site_id) if site_id else None,
        start=start if start else None,
        end=end if end else None,
        type=type.value if type else None,
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
