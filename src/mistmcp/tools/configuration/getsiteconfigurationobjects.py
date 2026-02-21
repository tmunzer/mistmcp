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
from mistmcp.response_formatter import format_response
from mistmcp.server import mcp
from mistmcp.logger import logger

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


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
    description="""Retrieve configuration objects from a specified site. Use the tool `getSiteConfigurationDerived` to retrieve the full site configuration including all configuration objects defined at the org level and assigned to the site""",
    tags={"configuration"},
    annotations={
        "title": "getSiteConfigurationObjects",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getSiteConfigurationObjects(
    site_id: Annotated[UUID, Field(description="""Site ID""")],
    object_type: Annotated[
        Object_type, Field(description="""Type of configuration object to retrieve""")
    ],
    object_id: Annotated[
        Optional[UUID | None],
        Field(description="""ID of the specific configuration object to retrieve"""),
    ] = None,
    limit: Annotated[
        int, Field(description="""Max number of results per page""", default=10)
    ] = 10,
    ctx: Context | None = None,
) -> dict | list | str:
    """Retrieve configuration objects from a specified site. Use the tool `getSiteConfigurationDerived` to retrieve the full site configuration including all configuration objects defined at the org level and assigned to the site"""

    logger.debug("Tool getSiteConfigurationObjects called")

    apisession, response_format = get_apisession()

    match object_type.value:
        case "devices":
            if object_id:
                response = mistapi.api.v1.sites.devices.getSiteDevice(
                    apisession, site_id=str(site_id), device_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.sites.devices.listSiteDevices(
                    apisession, site_id=str(site_id), limit=limit
                )
                await process_response(response)
        case "evpn_topologies":
            if object_id:
                response = mistapi.api.v1.sites.evpn_topologies.getSiteEvpnTopology(
                    apisession, site_id=str(site_id), evpn_topology_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.sites.evpn_topologies.listSiteEvpnTopologies(
                    apisession, site_id=str(site_id), limit=limit
                )
                await process_response(response)
                data = {
                    item.get("name"): item.get("id")
                    for item in response.data
                    if item.get("name")
                }
                response.data = data
        case "maps":
            if object_id:
                response = mistapi.api.v1.sites.maps.getSiteMap(
                    apisession, site_id=str(site_id), map_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.sites.maps.listSiteMaps(
                    apisession, site_id=str(site_id), limit=limit
                )
                await process_response(response)
                data = {
                    item.get("name"): item.get("id")
                    for item in response.data
                    if item.get("name")
                }
                response.data = data
        case "mxedges":
            if object_id:
                response = mistapi.api.v1.sites.mxedges.getSiteMxEdge(
                    apisession, site_id=str(site_id), mxedge_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.sites.mxedges.listSiteMxEdges(
                    apisession, site_id=str(site_id), limit=limit
                )
                await process_response(response)
        case "psks":
            if object_id:
                response = mistapi.api.v1.sites.psks.getSitePsk(
                    apisession, site_id=str(site_id), psk_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.sites.psks.listSitePsks(
                    apisession, site_id=str(site_id), limit=limit
                )
                await process_response(response)
        case "webhooks":
            if object_id:
                response = mistapi.api.v1.sites.webhooks.getSiteWebhook(
                    apisession, site_id=str(site_id), webhook_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.sites.webhooks.listSiteWebhooks(
                    apisession, site_id=str(site_id), limit=limit
                )
                await process_response(response)
                data = {
                    item.get("name"): item.get("id")
                    for item in response.data
                    if item.get("name")
                }
                response.data = data
        case "wlans":
            if object_id:
                response = mistapi.api.v1.sites.wlans.getSiteWlan(
                    apisession, site_id=str(site_id), wlan_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.sites.wlans.listSiteWlans(
                    apisession, site_id=str(site_id), limit=limit
                )
                await process_response(response)
                data = {
                    item.get("ssid"): item.get("id")
                    for item in response.data
                    if item.get("ssid")
                }
                response.data = data
        case "wxrules":
            if object_id:
                response = mistapi.api.v1.sites.wxrules.getSiteWxRule(
                    apisession, site_id=str(site_id), wxrule_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.sites.wxrules.listSiteWxRules(
                    apisession, site_id=str(site_id), limit=limit
                )
                await process_response(response)
        case "wxtags":
            if object_id:
                response = mistapi.api.v1.sites.wxtags.getSiteWxTag(
                    apisession, site_id=str(site_id), wxtag_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.sites.wxtags.listSiteWxTags(
                    apisession, site_id=str(site_id), limit=limit
                )
                await process_response(response)

        case _:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Object_type]}",
                }
            )

    return format_response(response, response_format)
