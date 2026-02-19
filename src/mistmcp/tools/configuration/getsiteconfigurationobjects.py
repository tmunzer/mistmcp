"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import json
import mistapi
from fastmcp import Context
from fastmcp.exceptions import ToolError
from mistmcp.request_processor import get_apisession
from mistmcp.response_processor import process_response
from mistmcp.server import get_mcp

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


mcp = get_mcp()

if not mcp:
    raise RuntimeError(
        "MCP instance not found. Make sure to initialize the MCP server before defining tools."
    )


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
    name="getSiteConfigurationObjects",
    description="""Retrieve configuration objects from a specified site. Use the tool `getSiteConfiguration` to retrieve the full site configuration including all configuration objects defined at the org level and assigned to the site""",
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
        Optional[UUID | None],
        Field(
            description="""ID of the specific configuration object to retrieve. Optional, if not provided all objects of the specified type will be returned."""
        ),
    ] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """Retrieve configuration objects from a specified site. Use the tool `getSiteConfiguration` to retrieve the full site configuration including all configuration objects defined at the org level and assigned to the site"""

    apisession, response_format = get_apisession()
    data = {}

    match object_type.value:
        case "devices":
            if object_id:
                response = mistapi.api.v1.sites.devices.getSiteDevice(
                    apisession, site_id=str(site_id), device_id=str(object_id)
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.sites.devices.listSiteDevices(
                    apisession, site_id=str(site_id), limit=1000
                )
                await process_response(response)
                data = response.data
        case "evpn_topologies":
            if object_id:
                response = mistapi.api.v1.sites.evpn_topologies.getSiteEvpnTopology(
                    apisession, site_id=str(site_id), evpn_topology_id=str(object_id)
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.sites.evpn_topologies.listSiteEvpnTopologies(
                    apisession, site_id=str(site_id), limit=1000
                )
                await process_response(response)
                data = {
                    item.get("name"): item.get("id")
                    for item in response.data
                    if item.get("name")
                }
        case "maps":
            if object_id:
                response = mistapi.api.v1.sites.maps.getSiteMap(
                    apisession, site_id=str(site_id), map_id=str(object_id)
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.sites.maps.listSiteMaps(
                    apisession, site_id=str(site_id), limit=1000
                )
                await process_response(response)
                data = {
                    item.get("name"): item.get("id")
                    for item in response.data
                    if item.get("name")
                }
        case "mxedges":
            if object_id:
                response = mistapi.api.v1.sites.mxedges.getSiteMxEdge(
                    apisession, site_id=str(site_id), mxedge_id=str(object_id)
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.sites.mxedges.listSiteMxEdges(
                    apisession, site_id=str(site_id), limit=1000
                )
                await process_response(response)
                data = response.data
        case "psks":
            if object_id:
                response = mistapi.api.v1.sites.psks.getSitePsk(
                    apisession, site_id=str(site_id), psk_id=str(object_id)
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.sites.psks.listSitePsks(
                    apisession, site_id=str(site_id), limit=1000
                )
                await process_response(response)
                data = response.data
        case "webhooks":
            if object_id:
                response = mistapi.api.v1.sites.webhooks.getSiteWebhook(
                    apisession, site_id=str(site_id), webhook_id=str(object_id)
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.sites.webhooks.listSiteWebhooks(
                    apisession, site_id=str(site_id), limit=1000
                )
                await process_response(response)
                data = {
                    item.get("name"): item.get("id")
                    for item in response.data
                    if item.get("name")
                }
        case "wlans":
            if object_id:
                response = mistapi.api.v1.sites.wlans.getSiteWlan(
                    apisession, site_id=str(site_id), wlan_id=str(object_id)
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.sites.wlans.listSiteWlans(
                    apisession, site_id=str(site_id), limit=1000
                )
                await process_response(response)
                data = {
                    item.get("ssid"): item.get("id")
                    for item in response.data
                    if item.get("ssid")
                }
        case "wxrules":
            if object_id:
                response = mistapi.api.v1.sites.wxrules.getSiteWxRule(
                    apisession, site_id=str(site_id), wxrule_id=str(object_id)
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.sites.wxrules.listSiteWxRules(
                    apisession, site_id=str(site_id), limit=1000
                )
                await process_response(response)
                data = response.data
        case "wxtags":
            if object_id:
                response = mistapi.api.v1.sites.wxtags.getSiteWxTag(
                    apisession, site_id=str(site_id), wxtag_id=str(object_id)
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.sites.wxtags.listSiteWxTags(
                    apisession, site_id=str(site_id), limit=1000
                )
                await process_response(response)
                data = response.data

        case _:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Object_type]}",
                }
            )

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
