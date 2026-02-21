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

from mistmcp.elicitation_processor import config_elicitation_handler
from mistmcp.server import mcp
from mistmcp.logger import logger

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


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


class Action_type(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


@mcp.tool(
    name="changeOrgConfigurationObjects",
    description="""Update, create or delete configuration object for a specified org. IMPORTANT:To ensure that you are not missing any existing attributes when updating the configuration object, make sure to :1. retrieve the current configuration object using the tools `getOrgConfigurationObjects` to retrieve the object defined at the site level2. Modify the desired attributes 3. Use this tool to update the configuration object with the modified attributesWhen creating a new configuration object, make sure to use the `getObjectsSchema` tool to discover the attributes of the configuration object and which of them are required. When deleting a WLAN Template, make sure to delete all WLANs that are using the template before deleting it, otherwise the deletion will failWhen creating a WLAN, make sure to set the `template_id` attribute in the payload to the ID of an existing WLAN Template. If needed, create a new WLAN Template using this tool before creating the WLAN and use the ID of the newly created template in the WLAN payload""",
    tags={"write_delete"},
    annotations={
        "title": "changeOrgConfigurationObjects",
        "readOnlyHint": False,
        "destructiveHint": True,
        "openWorldHint": True,
    },
)
async def changeOrgConfigurationObjects(
    action_type: Annotated[
        Action_type,
        Field(
            description="Whether the action is creating a new object, updating an existing one, or deleting an existing one. When updating or deleting, the object_id parameter must be provided."
        ),
    ],
    org_id: Annotated[UUID, Field(description="""Organization ID""")],
    object_type: Annotated[
        Object_type,
        Field(
            description="""Type of configuration object to create, update, or delete"""
        ),
    ],
    payload: Annotated[
        dict,
        Field(
            description="""JSON payload of the configuration object to update or create. When updating an existing object, make sure to include all required attributes in the payload. It is recommended to first retrieve the current configuration object using the `getOrgConfigurationObjects` tool and use the retrieved object as a base for the payload, modifying only the desired attributes"""
        ),
    ],
    object_id: Annotated[
        Optional[UUID | None],
        Field(
            description="""ID of the specific configuration object to update. Required when action_type is 'update' or 'delete'"""
        ),
    ] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """Update, create or delete configuration object for a specified org. IMPORTANT:To ensure that you are not missing any existing attributes when updating the configuration object, make sure to :1. retrieve the current configuration object using the tools `getOrgConfigurationObjects` to retrieve the object defined at the site level2. Modify the desired attributes 3. Use this tool to update the configuration object with the modified attributesWhen creating a new configuration object, make sure to use the `getObjectsSchema` tool to discover the attributes of the configuration object and which of them are required. When deleting a WLAN Template, make sure to delete all WLANs that are using the template before deleting it, otherwise the deletion will failWhen creating a WLAN, make sure to set the `template_id` attribute in the payload to the ID of an existing WLAN Template. If needed, create a new WLAN Template using this tool before creating the WLAN and use the ID of the newly created template in the WLAN payload"""

    logger.debug("Tool changeOrgConfigurationObjects called")

    apisession, response_format = get_apisession()

    action_wording = "create a new"
    if action_type == Action_type.UPDATE:
        if not object_id:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": "object_id parameter is required when action_type is 'update'.",
                }
            )
        action_wording = "update an existing"
    elif action_type == Action_type.DELETE:
        if not object_id:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": "object_id parameter is required when action_type is 'delete'.",
                }
            )
        action_wording = "delete an existing"

    if ctx:
        try:
            elicitation_response = await config_elicitation_handler(
                message=f"""The LLM wants to {action_wording} {object_type.value}. Do you accept to trigger the API call?""",
                ctx=ctx,
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
            if action_type.value == "update":
                response = mistapi.api.v1.orgs.alarmtemplates.updateOrgAlarmTemplate(
                    apisession,
                    org_id=str(org_id),
                    alarmtemplate_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            elif action_type.value == "create":
                response = mistapi.api.v1.orgs.alarmtemplates.createOrgAlarmTemplate(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.alarmtemplates.deleteOrgAlarmTemplate(
                    apisession, org_id=str(org_id), alarmtemplate_id=str(object_id)
                )
                await process_response(response)
                data = response.data
        case "wlans":
            if action_type.value == "update":
                response = mistapi.api.v1.orgs.wlans.updateOrgWlan(
                    apisession, org_id=str(org_id), wlan_id=str(object_id), body=payload
                )
                await process_response(response)
                data = response.data
            elif action_type.value == "create":
                response = mistapi.api.v1.orgs.wlans.createOrgWlan(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.wlans.deleteOrgWlan(
                    apisession, org_id=str(org_id), wlan_id=str(object_id)
                )
                await process_response(response)
                data = response.data
        case "sitegroups":
            if action_type.value == "update":
                response = mistapi.api.v1.orgs.sitegroups.updateOrgSiteGroup(
                    apisession,
                    org_id=str(org_id),
                    sitegroup_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            elif action_type.value == "create":
                response = mistapi.api.v1.orgs.sitegroups.createOrgSiteGroup(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.sitegroups.deleteOrgSiteGroup(
                    apisession, org_id=str(org_id), sitegroup_id=str(object_id)
                )
                await process_response(response)
                data = response.data
        case "avprofiles":
            if action_type.value == "update":
                response = mistapi.api.v1.orgs.avprofiles.updateOrgAntivirusProfile(
                    apisession,
                    org_id=str(org_id),
                    avprofile_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            elif action_type.value == "create":
                response = mistapi.api.v1.orgs.avprofiles.createOrgAntivirusProfile(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.avprofiles.deleteOrgAntivirusProfile(
                    apisession, org_id=str(org_id), avprofile_id=str(object_id)
                )
                await process_response(response)
                data = response.data
        case "deviceprofiles":
            if action_type.value == "update":
                response = mistapi.api.v1.orgs.deviceprofiles.updateOrgDeviceProfile(
                    apisession,
                    org_id=str(org_id),
                    deviceprofile_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            elif action_type.value == "create":
                response = mistapi.api.v1.orgs.deviceprofiles.createOrgDeviceProfile(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.deviceprofiles.deleteOrgDeviceProfile(
                    apisession, org_id=str(org_id), deviceprofile_id=str(object_id)
                )
                await process_response(response)
                data = response.data
        case "gatewaytemplates":
            if action_type.value == "update":
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
            elif action_type.value == "create":
                response = (
                    mistapi.api.v1.orgs.gatewaytemplates.createOrgGatewayTemplate(
                        apisession, org_id=str(org_id), body=payload
                    )
                )
                await process_response(response)
                data = response.data
            else:
                response = (
                    mistapi.api.v1.orgs.gatewaytemplates.deleteOrgGatewayTemplate(
                        apisession,
                        org_id=str(org_id),
                        gatewaytemplate_id=str(object_id),
                    )
                )
                await process_response(response)
                data = response.data
        case "idpprofiles":
            if action_type.value == "update":
                response = mistapi.api.v1.orgs.idpprofiles.updateOrgIdpProfile(
                    apisession,
                    org_id=str(org_id),
                    idpprofile_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            elif action_type.value == "create":
                response = mistapi.api.v1.orgs.idpprofiles.createOrgIdpProfile(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.idpprofiles.deleteOrgIdpProfile(
                    apisession, org_id=str(org_id), idpprofile_id=str(object_id)
                )
                await process_response(response)
                data = response.data
        case "aamwprofiles":
            if action_type.value == "update":
                response = mistapi.api.v1.orgs.aamwprofiles.updateOrgAAMWProfile(
                    apisession,
                    org_id=str(org_id),
                    aamwprofile_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            elif action_type.value == "create":
                response = mistapi.api.v1.orgs.aamwprofiles.createOrgAAMWProfile(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.aamwprofiles.deleteOrgAAMWProfile(
                    apisession, org_id=str(org_id), aamwprofile_id=str(object_id)
                )
                await process_response(response)
                data = response.data
        case "nactags":
            if action_type.value == "update":
                response = mistapi.api.v1.orgs.nactags.updateOrgNacTag(
                    apisession,
                    org_id=str(org_id),
                    nactag_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            elif action_type.value == "create":
                response = mistapi.api.v1.orgs.nactags.createOrgNacTag(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.nactags.deleteOrgNacTag(
                    apisession, org_id=str(org_id), nactag_id=str(object_id)
                )
                await process_response(response)
                data = response.data
        case "nacrules":
            if action_type.value == "update":
                response = mistapi.api.v1.orgs.nacrules.updateOrgNacRule(
                    apisession,
                    org_id=str(org_id),
                    nacrule_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            elif action_type.value == "create":
                response = mistapi.api.v1.orgs.nacrules.createOrgNacRule(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.nacrules.deleteOrgNacRule(
                    apisession, org_id=str(org_id), nacrule_id=str(object_id)
                )
                await process_response(response)
                data = response.data
        case "networktemplates":
            if action_type.value == "update":
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
            elif action_type.value == "create":
                response = (
                    mistapi.api.v1.orgs.networktemplates.createOrgNetworkTemplate(
                        apisession, org_id=str(org_id), body=payload
                    )
                )
                await process_response(response)
                data = response.data
            else:
                response = (
                    mistapi.api.v1.orgs.networktemplates.deleteOrgNetworkTemplate(
                        apisession,
                        org_id=str(org_id),
                        networktemplate_id=str(object_id),
                    )
                )
                await process_response(response)
                data = response.data
        case "networks":
            if action_type.value == "update":
                response = mistapi.api.v1.orgs.networks.updateOrgNetwork(
                    apisession,
                    org_id=str(org_id),
                    network_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            elif action_type.value == "create":
                response = mistapi.api.v1.orgs.networks.createOrgNetwork(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.networks.deleteOrgNetwork(
                    apisession, org_id=str(org_id), network_id=str(object_id)
                )
                await process_response(response)
                data = response.data
        case "psks":
            if action_type.value == "update":
                response = mistapi.api.v1.orgs.psks.updateOrgPsk(
                    apisession, org_id=str(org_id), psk_id=str(object_id), body=payload
                )
                await process_response(response)
                data = response.data
            elif action_type.value == "create":
                response = mistapi.api.v1.orgs.psks.createOrgPsk(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.psks.deleteOrgPsk(
                    apisession, org_id=str(org_id), psk_id=str(object_id)
                )
                await process_response(response)
                data = response.data
        case "rftemplates":
            if action_type.value == "update":
                response = mistapi.api.v1.orgs.rftemplates.updateOrgRfTemplate(
                    apisession,
                    org_id=str(org_id),
                    rftemplate_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            elif action_type.value == "create":
                response = mistapi.api.v1.orgs.rftemplates.createOrgRfTemplate(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.rftemplates.deleteOrgRfTemplate(
                    apisession, org_id=str(org_id), rftemplate_id=str(object_id)
                )
                await process_response(response)
                data = response.data
        case "services":
            if action_type.value == "update":
                response = mistapi.api.v1.orgs.services.updateOrgService(
                    apisession,
                    org_id=str(org_id),
                    service_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            elif action_type.value == "create":
                response = mistapi.api.v1.orgs.services.createOrgService(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.services.deleteOrgService(
                    apisession, org_id=str(org_id), service_id=str(object_id)
                )
                await process_response(response)
                data = response.data
        case "servicepolicies":
            if action_type.value == "update":
                response = mistapi.api.v1.orgs.servicepolicies.updateOrgServicePolicy(
                    apisession,
                    org_id=str(org_id),
                    servicepolicy_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            elif action_type.value == "create":
                response = mistapi.api.v1.orgs.servicepolicies.createOrgServicePolicy(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.servicepolicies.deleteOrgServicePolicy(
                    apisession, org_id=str(org_id), servicepolicy_id=str(object_id)
                )
                await process_response(response)
                data = response.data
        case "sitetemplates":
            if action_type.value == "update":
                response = mistapi.api.v1.orgs.sitetemplates.updateOrgSiteTemplate(
                    apisession,
                    org_id=str(org_id),
                    sitetemplate_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            elif action_type.value == "create":
                response = mistapi.api.v1.orgs.sitetemplates.createOrgSiteTemplate(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.sitetemplates.deleteOrgSiteTemplate(
                    apisession, org_id=str(org_id), sitetemplate_id=str(object_id)
                )
                await process_response(response)
                data = response.data
        case "vpns":
            if action_type.value == "update":
                response = mistapi.api.v1.orgs.vpns.updateOrgVpn(
                    apisession, org_id=str(org_id), vpn_id=str(object_id), body=payload
                )
                await process_response(response)
                data = response.data
            elif action_type.value == "create":
                response = mistapi.api.v1.orgs.vpns.createOrgVpn(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.vpns.deleteOrgVpn(
                    apisession, org_id=str(org_id), vpn_id=str(object_id)
                )
                await process_response(response)
                data = response.data
        case "webhooks":
            if action_type.value == "update":
                response = mistapi.api.v1.orgs.webhooks.updateOrgWebhook(
                    apisession,
                    org_id=str(org_id),
                    webhook_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            elif action_type.value == "create":
                response = mistapi.api.v1.orgs.webhooks.createOrgWebhook(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.webhooks.deleteOrgWebhook(
                    apisession, org_id=str(org_id), webhook_id=str(object_id)
                )
                await process_response(response)
                data = response.data
        case "wlantemplates":
            if action_type.value == "update":
                response = mistapi.api.v1.orgs.templates.updateOrgTemplate(
                    apisession,
                    org_id=str(org_id),
                    template_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            elif action_type.value == "create":
                response = mistapi.api.v1.orgs.templates.createOrgTemplate(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.templates.deleteOrgTemplate(
                    apisession, org_id=str(org_id), template_id=str(object_id)
                )
                await process_response(response)
                data = response.data
        case "wxrules":
            if action_type.value == "update":
                response = mistapi.api.v1.orgs.wxrules.updateOrgWxRule(
                    apisession,
                    org_id=str(org_id),
                    wxrule_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            elif action_type.value == "create":
                response = mistapi.api.v1.orgs.wxrules.createOrgWxRule(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.wxrules.deleteOrgWxRule(
                    apisession, org_id=str(org_id), wxrule_id=str(object_id)
                )
                await process_response(response)
                data = response.data
        case "wxtags":
            if action_type.value == "update":
                response = mistapi.api.v1.orgs.wxtags.updateOrgWxTag(
                    apisession,
                    org_id=str(org_id),
                    wxtag_id=str(object_id),
                    body=payload,
                )
                await process_response(response)
                data = response.data
            elif action_type.value == "create":
                response = mistapi.api.v1.orgs.wxtags.createOrgWxTag(
                    apisession, org_id=str(org_id), body=payload
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.wxtags.deleteOrgWxTag(
                    apisession, org_id=str(org_id), wxtag_id=str(object_id)
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

    return format_response(response, response_format)
