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
    AP = "ap"
    GATEWAY = "gateway"
    SWITCH = "switch"
    NONE = None


@mcp.tool(
    enabled=False,
    name="getOrgInventory",
    description="""Get Org Inventory### VC (Virtual-Chassis) Management Starting with the April release, Virtual Chassis devices in Mist will now usea cloud-assigned virtual MAC address as the device ID, instead of the physicalMAC address of the FPC0 member.**Retrieving the device ID or Site ID of a Virtual Chassis:**1. Use this API call with the query parameters `vc=true` and `mac` set to the MAC address of the VC member.2. In the response, check the `vc_mac` and `mac` fields:    - If `vc_mac` is empty or not present, the device is not part of a Virtual Chassis.    The `device_id` and `site_id` will be available in the device information.    - If `vc_mac` differs from the `mac` field, the device is part of a Virtual Chassis    but is not the device used to generate the Virtual Chassis ID. Use the `vc_mac` value with the [Get Org Inventory](/#operations/getOrgInventory)    API call to retrieve the `device_id` and `site_id`.    - If `vc_mac` matches the `mac` field, the device is the device used to generate the Virtual Chassis ID and he `device_id` and `site_id` will be available    in the device information.      This is the case if the device is the Virtual Chassis "virtual device" (MAC starting with `020003`) or if the device is the Virtual Chassis FPC0 and the Virtual Chassis is still using the FPC0 MAC address to generate the device ID.""",
    tags={"devices"},
    annotations={
        "title": "getOrgInventory",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getOrgInventory(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    serial: Annotated[Optional[str], Field(description="""Device serial""")] = None,
    model: Annotated[Optional[str], Field(description="""Device model""")] = None,
    type: Optional[Type] = Type.NONE,
    mac: Annotated[Optional[str], Field(description="""MAC address""")] = None,
    site_id: Annotated[
        Optional[UUID],
        Field(description="""Site id if assigned, null if not assigned"""),
    ] = None,
    vc_mac: Annotated[
        Optional[str], Field(description="""Virtual Chassis MAC Address""")
    ] = None,
    vc: Annotated[
        Optional[bool], Field(description="""To display Virtual Chassis members""")
    ] = None,
    unassigned: Annotated[
        bool, Field(description="""To display Unassigned devices""", default=True)
    ] = True,
    modified_after: Annotated[
        Optional[int],
        Field(description="""Filter on inventory last modified time, in epoch"""),
    ] = None,
    limit: Annotated[int, Field(default=100)] = 100,
    page: Annotated[int, Field(ge=1, default=1)] = 1,
) -> dict | list:
    """Get Org Inventory### VC (Virtual-Chassis) Management Starting with the April release, Virtual Chassis devices in Mist will now usea cloud-assigned virtual MAC address as the device ID, instead of the physicalMAC address of the FPC0 member.**Retrieving the device ID or Site ID of a Virtual Chassis:**1. Use this API call with the query parameters `vc=true` and `mac` set to the MAC address of the VC member.2. In the response, check the `vc_mac` and `mac` fields:    - If `vc_mac` is empty or not present, the device is not part of a Virtual Chassis.    The `device_id` and `site_id` will be available in the device information.    - If `vc_mac` differs from the `mac` field, the device is part of a Virtual Chassis    but is not the device used to generate the Virtual Chassis ID. Use the `vc_mac` value with the [Get Org Inventory](/#operations/getOrgInventory)    API call to retrieve the `device_id` and `site_id`.    - If `vc_mac` matches the `mac` field, the device is the device used to generate the Virtual Chassis ID and he `device_id` and `site_id` will be available    in the device information.      This is the case if the device is the Virtual Chassis "virtual device" (MAC starting with `020003`) or if the device is the Virtual Chassis FPC0 and the Virtual Chassis is still using the FPC0 MAC address to generate the device ID."""

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

    response = mistapi.api.v1.orgs.inventory.getOrgInventory(
        apisession,
        org_id=str(org_id),
        serial=serial,
        model=model,
        type=type.value if type else None,
        mac=mac,
        site_id=str(site_id) if site_id else None,
        vc_mac=vc_mac,
        vc=vc,
        unassigned=unassigned,
        modified_after=modified_after,
        limit=limit,
        page=page,
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
