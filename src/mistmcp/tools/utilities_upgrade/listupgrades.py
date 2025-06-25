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

# from mistmcp.server_factory import mcp_instance
from mistmcp.server_factory import mcp

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


# mcp = mcp_instance.get()


class Device_type(Enum):
    AP = "ap"
    SWITCH = "switch"
    SRX = "srx"
    MXEDGE = "mxedge"
    SSR = "ssr"


@mcp.tool(
    enabled=True,
    name="listUpgrades",
    description="""List all available upgrades for the organization.""",
    tags={"utilities_upgrade"},
    annotations={
        "title": "listUpgrades",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def listUpgrades(
    org_id: Annotated[
        UUID, Field(description="""ID of the organization to list upgrades for.""")
    ],
    device_type: Annotated[
        Device_type,
        Field(
            description="""Type of device to filter upgrades by. Optional, if not provided all upgrades will be listed."""
        ),
    ],
    upgrade_id: Annotated[
        Optional[UUID],
        Field(
            description="""ID of the specific upgrade to retrieve. Optional, if not provided all upgrades will be listed."""
        ),
    ] = None,
) -> dict:
    """List all available upgrades for the organization."""

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

    object_type = device_type
    match object_type.value:
        case "ap":
            if upgrade_id:
                response = mistapi.api.v1.orgs.devices.getOrgDeviceUpgrade(
                    apisession, org_id=str(org_id), upgrade_id=str(upgrade_id)
                )
            else:
                response = mistapi.api.v1.orgs.devices.listOrgDeviceUpgrades(
                    apisession, org_id=str(org_id)
                )
        case "switch":
            if upgrade_id:
                response = mistapi.api.v1.orgs.devices.getOrgDeviceUpgrade(
                    apisession, org_id=str(org_id), upgrade_id=str(upgrade_id)
                )
            else:
                response = mistapi.api.v1.orgs.devices.listOrgDeviceUpgrades(
                    apisession, org_id=str(org_id)
                )
        case "srx":
            if upgrade_id:
                response = mistapi.api.v1.orgs.devices.getOrgDeviceUpgrade(
                    apisession, org_id=str(org_id), upgrade_id=str(upgrade_id)
                )
            else:
                response = mistapi.api.v1.orgs.devices.listOrgDeviceUpgrades(
                    apisession, org_id=str(org_id)
                )
        case "mxedge":
            if upgrade_id:
                response = mistapi.api.v1.orgs.mxedges.getOrgMxEdgeUpgrade(
                    apisession, org_id=str(org_id), upgrade_id=str(upgrade_id)
                )
            else:
                response = mistapi.api.v1.orgs.mxedges.listOrgMxEdgeUpgrades(
                    apisession, org_id=str(org_id)
                )
        case "ssr":
            if upgrade_id:
                response = mistapi.api.v1.orgs.ssr.getOrgSsrUpgrade(
                    apisession, org_id=str(org_id), upgrade_id=str(upgrade_id)
                )
            else:
                response = mistapi.api.v1.orgs.ssr.listOrgSsrUpgrades(
                    apisession, org_id=str(org_id)
                )

        case _:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Object_type]}",
                }
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
