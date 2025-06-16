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
from fastmcp.exceptions import ToolError
from starlette.requests import Request
from mistmcp.server_factory import mcp_instance

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
    enabled=True,
    name="troubleshootOrg",
    description="""Troubleshoot sites, devices, clients, and wired clients for maximum of last 7 days from current time. See search APIs for device information:- [search Device](/#operations/searchOrgDevices)- [search Wireless Client](/#operations/searchOrgWirelessClients)- [search Wired Client](/#operations/searchOrgWiredClients)- [search Wan Client](/#operations/searchOrgWanClients)**NOTE**: requires Marvis subscription license""",
    tags={"Orgs Marvis"},
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
    ] = None,
    site_id: Annotated[
        Optional[UUID], Field(description="""**required** when troubleshooting site""")
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
    type: Annotated[
        Type,
        Field(
            description="""When troubleshooting site, type of network to troubleshoot"""
        ),
    ] = Type.NONE,
) -> dict:
    """Troubleshoot sites, devices, clients, and wired clients for maximum of last 7 days from current time. See search APIs for device information:- [search Device](/#operations/searchOrgDevices)- [search Wireless Client](/#operations/searchOrgWirelessClients)- [search Wired Client](/#operations/searchOrgWiredClients)- [search Wan Client](/#operations/searchOrgWanClients)**NOTE**: requires Marvis subscription license"""

    ctx = get_context()
    request: Request = get_http_request()
    cloud = request.query_params.get("cloud", None)
    apitoken = request.headers.get("X-Authorization", None)
    apisession = mistapi.APISession(
        host=cloud,
        apitoken=apitoken,
    )

    response = mistapi.api.v1.orgs.troubleshoot.troubleshootOrg(
        apisession,
        org_id=str(org_id),
        mac=mac,
        site_id=str(site_id),
        start=start,
        end=end,
        type=type.value,
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
