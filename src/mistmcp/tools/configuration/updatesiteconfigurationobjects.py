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
    PSKS = "psks"
    WEBHOOKS = "webhooks"
    WLANS = "wlans"
    WXRULES = "wxrules"
    WXTAGS = "wxtags"


@mcp.tool(
    enabled=True,
    name="updateSiteConfigurationObjects",
    description="""Update or create configuration object for a specified site. When updating the object, make sure to first retrieve the current configuration object using the `getSiteConfigurationObjects` tool, modify the desired attributes and then use this tool to update the configuration object with the modified attributes. This is required to ensure that you are not missing any required attributes when updating the configuration object.""",
    tags={"configuration"},
    annotations={
        "title": "updateSiteConfigurationObjects",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def updateSiteConfigurationObjects(
    site_id: Annotated[
        UUID,
        Field(description="""ID of the site to update configuration objects for."""),
    ],
    object_type: Annotated[
        Object_type, Field(description="""Type of configuration object to update.""")
    ],
    payload: Annotated[
        None,
        Field(
            description="""JSON payload of the configuration object to update or create. When updating an existing object, make sure to include all required attributes in the payload. It is recommended to first retrieve the current configuration object using the `getSiteConfigurationObjects` tool and use the retrieved object as a base for the payload, modifying only the desired attributes."""
        ),
    ],
    object_id: Annotated[
        Optional[UUID | None],
        Field(
            description="""ID of the specific configuration object to update. Optional, if not provided, a new configuration object will be created with the provided payload."""
        ),
    ] = None,
) -> dict | list:
    """Update or create configuration object for a specified site. When updating the object, make sure to first retrieve the current configuration object using the `getSiteConfigurationObjects` tool, modify the desired attributes and then use this tool to update the configuration object with the modified attributes. This is required to ensure that you are not missing any required attributes when updating the configuration object."""

    apisession = get_apisession()
    data = {}

    match object_type.value:
        case "devices":
            response = mistapi.api.v1.sites.devices.updateSiteDevice(
                apisession, site_id=str(site_id), device_id=str(object_id), body=payload
            )
            await process_response(response)
            data = response.data
        case "evpn_topologies":
            if object_id:
                response = (
                    mistapi.api.v1.sites.evpn_topologies.updateSiteEvpnTopologies(
                        apisession,
                        site_id=str(site_id),
                        evpn_topology_id=str(object_id),
                        data=payload,
                    )
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.sites.evpn_topologies.createSiteEvpnTopology(
                    apisession, site_id=str(site_id), data=payload
                )
                await process_response(response)
                data = response.data
        case "psks":
            if object_id:
                response = mistapi.api.v1.sites.psks.updateSitePsk(
                    apisession,
                    site_id=str(site_id),
                    psk_id=str(object_id),
                    data=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.sites.psks.createSitePsk(
                    apisession, site_id=str(site_id), data=payload
                )
                await process_response(response)
                data = response.data
        case "webhooks":
            if object_id:
                response = mistapi.api.v1.sites.webhooks.updateSiteWebhook(
                    apisession,
                    site_id=str(site_id),
                    webhook_id=str(object_id),
                    data=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.sites.webhooks.createSiteWebhook(
                    apisession, site_id=str(site_id), data=payload
                )
                await process_response(response)
                data = response.data
        case "wlans":
            if object_id:
                response = mistapi.api.v1.sites.wlans.updateSiteWlan(
                    apisession,
                    site_id=str(site_id),
                    wlan_id=str(object_id),
                    data=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.sites.wlans.createSiteWlan(
                    apisession, site_id=str(site_id), data=payload
                )
                await process_response(response)
                data = response.data
        case "wxrules":
            if object_id:
                response = mistapi.api.v1.sites.wxrules.updateSiteWxRule(
                    apisession,
                    site_id=str(site_id),
                    wxrule_id=str(object_id),
                    data=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.sites.wxrules.createSiteWxRule(
                    apisession, site_id=str(site_id), data=payload
                )
                await process_response(response)
                data = response.data
        case "wxtags":
            if object_id:
                response = mistapi.api.v1.sites.wxtags.updateSiteWxTag(
                    apisession,
                    site_id=str(site_id),
                    wxtag_id=str(object_id),
                    data=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.sites.wxtags.createSiteWxTag(
                    apisession, site_id=str(site_id), data=payload
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

    return data
