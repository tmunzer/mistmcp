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

from mistmcp.elicitation.elicitation_handler import config_elicitation_handler
from mistmcp.server import mcp

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


class Object_type(Enum):
    DEVICES = "devices"
    EVPN_TOPOLOGIES = "evpn_topologies"
    PSKS = "psks"
    WEBHOOKS = "webhooks"
    WLANS = "wlans"
    WXRULES = "wxrules"
    WXTAGS = "wxtags"


@mcp.tool(
    name="updateSiteConfigurationObjects",
    description="""Update or create configuration object for a specified site. IMPORTANT:To ensure that you are not missing any required attributes when updating the configuration object when updating the object, make sure to :* first retrieve the current configuration object using the tools `getSiteConfigurationObjects` to retrieve the object defined at the site level or `getSiteConfiguration` to retrieve the full site configuration including all configuration objects defined at the org level and assigned to the site* modify the desired attributes * use this tool to update the configuration object with the modified attributesYou can also use the `getObjectsSchema` tool to get discover the attributes of the configuration object and which of them are required. When creating a new configuration object, make sure to include all required attributes in the payload.""",
    tags={"write"},
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
        dict,
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
    ctx: Context | None = None,
) -> dict | list | str:
    """Update or create configuration object for a specified site. IMPORTANT:To ensure that you are not missing any required attributes when updating the configuration object when updating the object, make sure to :* first retrieve the current configuration object using the tools `getSiteConfigurationObjects` to retrieve the object defined at the site level or `getSiteConfiguration` to retrieve the full site configuration including all configuration objects defined at the org level and assigned to the site* modify the desired attributes * use this tool to update the configuration object with the modified attributesYou can also use the `getObjectsSchema` tool to get discover the attributes of the configuration object and which of them are required. When creating a new configuration object, make sure to include all required attributes in the payload."""

    apisession, response_format = get_apisession()
    data = {}

    object_action = "create"
    object_status = "a new"
    if object_id:
        object_action = "update"
        object_status = "an existing"

    try:
        elicitation_response = await config_elicitation_handler(
            message=f"""The LLM wants to {object_action} {object_status} {object_type.value}. Do you accept to trigger the API call?""",
            context=ctx,
        )
    except Exception as exc:
        raise ToolError(
            {
                "status_code": 400,
                "message": (
                    "AI App does not support elicitation. You cannot use it to "
                    "modify configuration objects. Please use the Mist API "
                    "directly or use an AI App with elicitation support to "
                    "modify configuration objects."
                ),
            }
        ) from exc

    if elicitation_response.action == "decline":
        return {"message": "Action declined by user."}
    elif elicitation_response.action == "cancel":
        return {"message": "Action canceled by user."}

    match object_type.value:
        case "devices":
            response = mistapi.api.v1.sites.devices.updateSiteDevice(
                apisession, site_id=str(site_id), device_id=str(object_id), body=payload
            )
            await process_response(response)
            data = response.data
        case "evpn_topologies":
            if object_id:
                response = mistapi.api.v1.sites.evpn_topologies.updateSiteEvpnTopology(
                    apisession,
                    site_id=str(site_id),
                    evpn_topology_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.sites.evpn_topologies.createSiteEvpnTopology(
                    apisession, site_id=str(site_id), body=payload
                )
                await process_response(response)
                data = response.data
        case "psks":
            if object_id:
                response = mistapi.api.v1.sites.psks.updateSitePsk(
                    apisession,
                    site_id=str(site_id),
                    psk_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.sites.psks.createSitePsk(
                    apisession, site_id=str(site_id), body=payload
                )
                await process_response(response)
                data = response.data
        case "webhooks":
            if object_id:
                response = mistapi.api.v1.sites.webhooks.updateSiteWebhook(
                    apisession,
                    site_id=str(site_id),
                    webhook_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.sites.webhooks.createSiteWebhook(
                    apisession, site_id=str(site_id), body=payload
                )
                await process_response(response)
                data = response.data
        case "wlans":
            if object_id:
                response = mistapi.api.v1.sites.wlans.updateSiteWlan(
                    apisession,
                    site_id=str(site_id),
                    wlan_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.sites.wlans.createSiteWlan(
                    apisession, site_id=str(site_id), body=payload
                )
                await process_response(response)
                data = response.data
        case "wxrules":
            if object_id:
                response = mistapi.api.v1.sites.wxrules.updateSiteWxRule(
                    apisession,
                    site_id=str(site_id),
                    wxrule_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.sites.wxrules.createSiteWxRule(
                    apisession, site_id=str(site_id), body=payload
                )
                await process_response(response)
                data = response.data
        case "wxtags":
            if object_id:
                response = mistapi.api.v1.sites.wxtags.updateSiteWxTag(
                    apisession,
                    site_id=str(site_id),
                    wxtag_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.sites.wxtags.createSiteWxTag(
                    apisession, site_id=str(site_id), body=payload
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
