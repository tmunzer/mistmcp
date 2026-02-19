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
from fastmcp.server.dependencies import get_context

from mistmcp.elicitation.elicitation_handler import config_elicitation_handler
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
    ALARMTEMPLATES = "alarmtemplates"
    WLANS = "wlans"
    SITEGROUPS = "sitegroups"
    AVPROFILES = "avprofiles"
    DEVICEPROFILES = "deviceprofiles"
    GATEWAYTEMPLATES = "gatewaytemplates"
    IDPPROFILES = "idpprofiles"
    AAMWPROFILES = "aamwprofiles"
    NACTAGS = "nactags"
    NACRULES = "nacrules"
    NETWORKTEMPLATES = "networktemplates"
    NETWORKS = "networks"
    PSKS = "psks"
    RFTEMPLATES = "rftemplates"
    SERVICES = "services"
    SERVICEPOLICIES = "servicepolicies"
    SITETEMPLATES = "sitetemplates"
    VPNS = "vpns"
    WEBHOOKS = "webhooks"
    WLANTEMPLATES = "wlantemplates"
    WXRULES = "wxrules"
    WXTAGS = "wxtags"


@mcp.tool(
    enabled=True,
    name="updateOrgConfigurationObjects",
    description="""Update or create configuration object for a specified org. When updating the object, make sure to first retrieve the current configuration object using the `getOrgConfigurationObjects` tool, modify the desired attributes and then use this tool to update the configuration object with the modified attributes. This is required to ensure that you are not missing any required attributes when updating the configuration object.""",
    tags={"configuration"},
    annotations={
        "title": "updateOrgConfigurationObjects",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def updateOrgConfigurationObjects(
    org_id: Annotated[
        UUID,
        Field(
            description="""ID of the organization or site to update configuration objects for."""
        ),
    ],
    object_type: Annotated[
        Object_type, Field(description="""Type of configuration object to update.""")
    ],
    payload: Annotated[
        dict,
        Field(
            description="""JSON payload of the configuration object to update or create. When updating an existing object, make sure to include all required attributes in the payload. It is recommended to first retrieve the current configuration object using the `getOrgConfigurationObjects` tool and use the retrieved object as a base for the payload, modifying only the desired attributes."""
        ),
    ],
    object_id: Annotated[
        Optional[UUID | None],
        Field(
            description="""ID of the specific configuration object to update. Optional, if not provided, a new configuration object will be created with the provided payload."""
        ),
    ] = None,
) -> dict | list | str:
    """Update or create configuration object for a specified org. When updating the object, make sure to first retrieve the current configuration object using the `getOrgConfigurationObjects` tool, modify the desired attributes and then use this tool to update the configuration object with the modified attributes. This is required to ensure that you are not missing any required attributes when updating the configuration object."""

    apisession, disable_elicitation, response_format = get_apisession()
    data = {}

    if not disable_elicitation:
        object_action = "create"
        object_status = "a new"
        if object_id:
            object_action = "update"
            object_status = "an existing"

        try:
            elicitation_response = await config_elicitation_handler(
                message=f"""The LLM wants to {object_action} {object_status} {object_type.value}. Do you accept to trigger the API call?""",
                context=get_context(),
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
        case "alarmtemplates":
            if object_id:
                response = mistapi.api.v1.orgs.alarmtemplates.updateOrgAlarmTemplate(
                    apisession,
                    org_id=str(org_id),
                    alarmtemplate_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.alarmtemplates.createOrgAlarmTemplate(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
        case "wlans":
            if object_id:
                response = mistapi.api.v1.orgs.wlans.updateOrgWlan(
                    apisession, org_id=str(org_id), wlan_id=str(object_id), body=payload
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.wlans.createOrgWlan(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
        case "sitegroups":
            if object_id:
                response = mistapi.api.v1.orgs.sitegroups.updateOrgSiteGroup(
                    apisession,
                    org_id=str(org_id),
                    sitegroup_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.sitegroups.createOrgSiteGroup(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
        case "avprofiles":
            if object_id:
                response = mistapi.api.v1.orgs.avprofiles.updateOrgAntivirusProfile(
                    apisession,
                    org_id=str(org_id),
                    avprofile_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.avprofiles.createOrgAntivirusProfile(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
        case "deviceprofiles":
            if object_id:
                response = mistapi.api.v1.orgs.deviceprofiles.updateOrgDeviceProfile(
                    apisession,
                    org_id=str(org_id),
                    deviceprofile_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.deviceprofiles.createOrgDeviceProfile(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
        case "gatewaytemplates":
            if object_id:
                response = (
                    mistapi.api.v1.orgs.gatewaytemplates.updateOrgGatewayTemplate(
                        apisession,
                        org_id=str(org_id),
                        gatewaytemplate_id=str(object_id),
                        body=payload,
                    )
                )
                await process_response(response)
                data = response.data
            else:
                response = (
                    mistapi.api.v1.orgs.gatewaytemplates.createOrgGatewayTemplate(
                        apisession, org_id=str(org_id), body=payload
                    )
                )
                await process_response(response)
                data = response.data
        case "idpprofiles":
            if object_id:
                response = mistapi.api.v1.orgs.idpprofiles.updateOrgIdpProfile(
                    apisession,
                    org_id=str(org_id),
                    idpprofile_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.idpprofiles.createOrgIdpProfile(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
        case "aamwprofiles":
            if object_id:
                response = mistapi.api.v1.orgs.aamwprofiles.updateOrgAAMWProfile(
                    apisession,
                    org_id=str(org_id),
                    aamwprofile_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.aamwprofiles.createOrgAAMWProfile(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
        case "nactags":
            if object_id:
                response = mistapi.api.v1.orgs.nactags.updateOrgNacTag(
                    apisession,
                    org_id=str(org_id),
                    nactag_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.nactags.createOrgNacTag(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
        case "nacrules":
            if object_id:
                response = mistapi.api.v1.orgs.nacrules.updateOrgNacRule(
                    apisession,
                    org_id=str(org_id),
                    nacrule_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.nacrules.createOrgNacRule(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
        case "networktemplates":
            if object_id:
                response = (
                    mistapi.api.v1.orgs.networktemplates.updateOrgNetworkTemplate(
                        apisession,
                        org_id=str(org_id),
                        networktemplate_id=str(object_id),
                        body=payload,
                    )
                )
                await process_response(response)
                data = response.data
            else:
                response = (
                    mistapi.api.v1.orgs.networktemplates.createOrgNetworkTemplate(
                        apisession, org_id=str(org_id), body=payload
                    )
                )
                await process_response(response)
                data = response.data
        case "networks":
            if object_id:
                response = mistapi.api.v1.orgs.networks.updateOrgNetwork(
                    apisession,
                    org_id=str(org_id),
                    network_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.networks.createOrgNetwork(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
        case "psks":
            if object_id:
                response = mistapi.api.v1.orgs.psks.updateOrgPsk(
                    apisession, org_id=str(org_id), psk_id=str(object_id), body=payload
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.psks.createOrgPsk(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
        case "rftemplates":
            if object_id:
                response = mistapi.api.v1.orgs.rftemplates.updateOrgRfTemplate(
                    apisession,
                    org_id=str(org_id),
                    rftemplate_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.rftemplates.createOrgRfTemplate(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
        case "services":
            if object_id:
                response = mistapi.api.v1.orgs.services.updateOrgService(
                    apisession,
                    org_id=str(org_id),
                    service_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.services.createOrgService(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
        case "servicepolicies":
            if object_id:
                response = mistapi.api.v1.orgs.servicepolicies.updateOrgServicePolicy(
                    apisession,
                    org_id=str(org_id),
                    servicepolicy_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.servicepolicies.createOrgServicePolicy(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
        case "sitetemplates":
            if object_id:
                response = mistapi.api.v1.orgs.sitetemplates.updateOrgSiteTemplate(
                    apisession,
                    org_id=str(org_id),
                    sitetemplate_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.sitetemplates.createOrgSiteTemplate(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
        case "vpns":
            if object_id:
                response = mistapi.api.v1.orgs.vpns.updateOrgVpn(
                    apisession, org_id=str(org_id), vpn_id=str(object_id), body=payload
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.vpns.createOrgVpn(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
        case "webhooks":
            if object_id:
                response = mistapi.api.v1.orgs.webhooks.updateOrgWebhook(
                    apisession,
                    org_id=str(org_id),
                    webhook_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.webhooks.createOrgWebhook(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
        case "wlantemplates":
            if object_id:
                response = mistapi.api.v1.orgs.templates.updateOrgTemplate(
                    apisession,
                    org_id=str(org_id),
                    template_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.templates.createOrgTemplate(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
        case "wxrules":
            if object_id:
                response = mistapi.api.v1.orgs.wxrules.updateOrgWxRule(
                    apisession,
                    org_id=str(org_id),
                    wxrule_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.wxrules.createOrgWxRule(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
        case "wxtags":
            if object_id:
                response = mistapi.api.v1.orgs.wxtags.updateOrgWxTag(
                    apisession,
                    org_id=str(org_id),
                    wxtag_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.wxtags.createOrgWxTag(
                    apisession, org_id=str(org_id), body=payload
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
