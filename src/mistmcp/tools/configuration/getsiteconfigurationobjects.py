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


class Object_type(Enum):
    DEVICES = "devices"
    EVPN_TOPOLOGIES = "evpn_topologies"
    MAPS = "maps"
    MXEDGES = "mxedges"
    PSKS = "psks"
    WEBHOOKS = "webhooks"
    WLANS = "wlans"
    WXRULES = "wxrules"
    WXTAGS = "wxtags"


@mcp.tool(
    enabled=True,
    name="getSiteConfigurationObjects",
    description="""Retrieve configuration objects from a specified site. The "_derived" tools are used to retrieve derived configuration objects that are generated from the org level objects with jinja2 variables resolved with the site variables.""",
    tags={"configuration"},
    annotations={
        "title": "getSiteConfigurationObjects",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getSiteConfigurationObjects(
    site_id: Annotated[
        UUID,
        Field(description="""ID of the site to retrieve configuration objects from."""),
    ],
    object_type: Annotated[
        Object_type, Field(description="""Type of configuration object to retrieve.""")
    ],
    object_id: Annotated[
        Optional[UUID],
        Field(
            description="""ID of the specific configuration object to retrieve. Optional, if not provided all objects of the specified type will be returned."""
        ),
    ] = None,
) -> dict:
    """Retrieve configuration objects from a specified site. The "_derived" tools are used to retrieve derived configuration objects that are generated from the org level objects with jinja2 variables resolved with the site variables."""

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

    match object_type.value:
        case "devices":
            if object_id:
                response = mistapi.api.v1.sites.devices.getSiteDevice(
                    apisession, site_id=str(site_id), device_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.sites.devices.listSiteDevices(
                    apisession, site_id=str(site_id)
                )
        case "evpn_topologies":
            if object_id:
                response = mistapi.api.v1.sites.evpn_topologies.getSiteEvpnTopology(
                    apisession, site_id=str(site_id), evpn_topology_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.sites.evpn_topologies.listSiteEvpnTopologies(
                    apisession, site_id=str(site_id)
                )
        case "maps":
            if object_id:
                response = mistapi.api.v1.sites.maps.getSiteMap(
                    apisession, site_id=str(site_id), map_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.sites.maps.listSiteMaps(
                    apisession, site_id=str(site_id)
                )
        case "mxedges":
            if object_id:
                response = mistapi.api.v1.sites.mxedges.getSiteMxEdge(
                    apisession, site_id=str(site_id), mxedge_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.sites.mxedges.listSiteMxEdges(
                    apisession, site_id=str(site_id)
                )
        case "psks":
            if object_id:
                response = mistapi.api.v1.sites.psks.getSitePsk(
                    apisession, site_id=str(site_id), psk_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.sites.psks.listSitePsks(
                    apisession, site_id=str(site_id)
                )
        case "webhooks":
            if object_id:
                response = mistapi.api.v1.sites.webhooks.getSiteWebhook(
                    apisession, site_id=str(site_id), webhook_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.sites.webhooks.listSiteWebhooks(
                    apisession, site_id=str(site_id)
                )
        case "wlans":
            if object_id:
                response = mistapi.api.v1.sites.wlans.getSiteWlan(
                    apisession, site_id=str(site_id), wlan_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.sites.wlans.listSiteWlans(
                    apisession, site_id=str(site_id)
                )
        case "wxrules":
            if object_id:
                response = mistapi.api.v1.sites.wxrules.getSiteWxRule(
                    apisession, site_id=str(site_id), wxrule_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.sites.wxrules.listSiteWxRules(
                    apisession, site_id=str(site_id)
                )
        case "wxtags":
            if object_id:
                response = mistapi.api.v1.sites.wxtags.getSiteWxTag(
                    apisession, site_id=str(site_id), wxtag_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.sites.wxtags.listSiteWxTags(
                    apisession, site_id=str(site_id)
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
