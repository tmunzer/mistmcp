CHANGE_CONFIGURATION_OBJECTS_TEMPLATE = r'''

"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

from enum import Enum
from typing import Annotated
from uuid import UUID

import mistapi
from fastmcp import Context
from fastmcp.exceptions import ToolError
from pydantic import Field

from mistmcp.elicitation_processor import config_elicitation_handler
from mistmcp.logger import logger
from mistmcp.request_processor import get_apisession
from mistmcp.response_formatter import format_response
from mistmcp.response_processor import handle_network_error, process_response
from mistmcp.server import mcp


class Object_type(Enum):
    ORG_INFO = "org_info"
    ORG_ALARMTEMPLATES = "org_alarmtemplates"
    ORG_WLANS = "org_wlans"
    ORG_SITEGROUPS = "org_sitegroups"
    ORG_AVPROFILES = "org_avprofiles"
    ORG_DEVICEPROFILES = "org_deviceprofiles"
    ORG_GATEWAYTEMPLATES = "org_gatewaytemplates"
    ORG_IDPPROFILES = "org_idpprofiles"
    ORG_AAMWPROFILES = "org_aamwprofiles"
    ORG_NACTAGS = "org_nactags"
    ORG_NACRULES = "org_nacrules"
    ORG_NETWORKTEMPLATES = "org_networktemplates"
    ORG_NETWORKS = "org_networks"
    ORG_PSKS = "org_psks"
    ORG_RFTEMPLATES = "org_rftemplates"
    ORG_SERVICES = "org_services"
    ORG_SERVICEPOLICIES = "org_servicepolicies"
    ORG_SITES = "org_sites"
    ORG_SITETEMPLATES = "org_sitetemplates"
    ORG_VPNS = "org_vpns"
    ORG_WEBHOOKS = "org_webhooks"
    ORG_WLANTEMPLATES = "org_wlantemplates"
    ORG_WXRULES = "org_wxrules"
    ORG_WXTAGS = "org_wxtags"
    SITE_INFO = "site_info"
    SITE_DEVICES = "site_devices"
    SITE_PSKS = "site_psks"
    SITE_WEBHOOKS = "site_webhooks"
    SITE_WLANS = "site_wlans"
    SITE_WXRULES = "site_wxrules"
    SITE_WXTAGS = "site_wxtags"


class Action_type(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


@mcp.tool(
    name="mist_change_configuration_objects",
    description="""Update, create or delete configuration object for a specified org or site.

IMPORTANT:

To ensure that you are not missing any existing attributes when updating the configuration object, make sure to :

1. retrieve the current configuration object using the tools `mist_get_configuration_objects` to retrieve the object defined at the site level

2. Modify the desired attributes

3. Use this tool to update the configuration object with the modified attributes



When creating a new configuration object, make sure to use the`mist_get_configuration_object_schema` tool to discover the attributes of the configuration object and which of them are required.



When deleting an org WLAN template (`org_wlantemplates`), make sure to delete all WLANs that are using the template before deleting it, otherwise the deletion will fail

When creating a WLAN, make sure to set the `template_id` attribute in the payload to the ID of an existing WLAN Template. If needed, create a new WLAN Template using this tool before creating the WLAN and use the ID of the newly created template in the WLAN payload
""",
    tags={"write_delete"},
    annotations={
        "title": "Change configuration objects",
        "readOnlyHint": False,
        "destructiveHint": True,
        "openWorldHint": True,
        "idempotentHint": False,
    },
)
async def change_configuration_objects(
    action_type: Annotated[
        Action_type,
        Field(
            description="Whether the action is creating a new object, updating an existing one, or deleting an existing one. When updating or deleting, the object_id parameter must be provided."
        ),
    ],
    object_type: Annotated[
        Object_type,
        Field(
            description="""Type of configuration object to create, update, or delete"""
        ),
    ],
    payload: Annotated[
        dict,
        Field(
            description="""JSON payload of the configuration object to update or create. When updating an existing object, make sure to include all required attributes in the payload. It is recommended to first retrieve the current configuration object using the`mist_get_configuration_objects` tool and use the retrieved object as a base for the payload, modifying only the desired attributes"""
        ),
    ],
    org_id: Annotated[UUID, Field(description="""Organization ID""", default=None)],
    site_id: Annotated[UUID, Field(description="""Site ID""", default=None)],
    object_id: Annotated[
        UUID,
        Field(
            description="""ID of the specific configuration object to update. Required when action_type is 'update' or 'delete'""",
            default=None,
        ),
    ],
    ctx: Context,
) -> dict | list | str:
    """Update, create or delete configuration object for a specified org or site.

    IMPORTANT:

    To ensure that you are not missing any existing attributes when updating the configuration object, make sure to :

    1. retrieve the current configuration object using the tools `mist_get_configuration_objects` to retrieve the object defined at the site level

    2. Modify the desired attributes

    3. Use this tool to update the configuration object with the modified attributes



    When creating a new configuration object, make sure to use the`mist_get_configuration_object_schema` tool to discover the attributes of the configuration object and which of them are required.



    When deleting an org WLAN template (`org_wlantemplates`), make sure to delete all WLANs that are using the template before deleting it, otherwise the deletion will fail

    When creating a WLAN, make sure to set the `template_id` attribute in the payload to the ID of an existing WLAN Template. If needed, create a new WLAN Template using this tool before creating the WLAN and use the ID of the newly created template in the WLAN payload
    """

    logger.debug("Tool change_configuration_objects called")
    logger.debug(
        "Input Parameters: object_type: %s, payload: %s, org_id: %s, site_id: %s, object_id: %s",
        object_type,
        payload,
        org_id,
        site_id,
        object_id,
    )

    apisession, response_format = await get_apisession()

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

    if object_type.value.startswith("org_") and not org_id:
        raise ToolError(
            {
                "status_code": 400,
                "message": (
                    "`org_id` parameter is required when `object_type` starts "
                    "with `org_`."
                ),
            }
        )

    if object_type.value.startswith("site_") and not site_id:
        raise ToolError(
            {
                "status_code": 400,
                "message": (
                    "`site_id` parameter is required when `object_type` starts "
                    "with `site_`."
                ),
            }
        )

    if object_type == Object_type.SITE_DEVICES and action_type != Action_type.UPDATE:
        raise ToolError(
            {
                "status_code": 400,
                "message": (
                    "`site_devices` supports `update` only. "
                    "Use `action_type=update` with `object_id`."
                ),
            }
        )

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

    try:
        match object_type.value:
            case "org_info":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.updateOrg(
                        apisession,
                        org_id=str(org_id),
                        body=payload,
                    )
                    await process_response(response)
                else:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": "Only 'update' action is supported for 'org_info' object type.",
                        }
                    )
            case "org_alarmtemplates":
                if action_type.value == "update":
                    response = (
                        mistapi.api.v1.orgs.alarmtemplates.updateOrgAlarmTemplate(
                            apisession,
                            org_id=str(org_id),
                            alarmtemplate_id=str(object_id),
                            body=payload,
                        )
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = (
                        mistapi.api.v1.orgs.alarmtemplates.createOrgAlarmTemplate(
                            apisession, org_id=str(org_id), body=payload
                        )
                    )
                    await process_response(response)
                else:
                    response = (
                        mistapi.api.v1.orgs.alarmtemplates.deleteOrgAlarmTemplate(
                            apisession,
                            org_id=str(org_id),
                            alarmtemplate_id=str(object_id),
                        )
                    )
                    await process_response(response)
            case "org_wlans":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.wlans.updateOrgWlan(
                        apisession,
                        org_id=str(org_id),
                        wlan_id=str(object_id),
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.wlans.createOrgWlan(
                        apisession, org_id=str(org_id), body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.wlans.deleteOrgWlan(
                        apisession, org_id=str(org_id), wlan_id=str(object_id)
                    )
                    await process_response(response)
            case "org_sitegroups":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.sitegroups.updateOrgSiteGroup(
                        apisession,
                        org_id=str(org_id),
                        sitegroup_id=str(object_id),
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.sitegroups.createOrgSiteGroup(
                        apisession, org_id=str(org_id), body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.sitegroups.deleteOrgSiteGroup(
                        apisession, org_id=str(org_id), sitegroup_id=str(object_id)
                    )
                    await process_response(response)
            case "org_sites":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.sites.updateOrgSite(
                        apisession,
                        org_id=str(org_id),
                        site_id=str(object_id),
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.sites.createOrgSite(
                        apisession, org_id=str(org_id), body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.sites.deleteOrgSite(
                        apisession, org_id=str(org_id), site_id=str(object_id)
                    )
                    await process_response(response)
            case "org_avprofiles":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.avprofiles.updateOrgAntivirusProfile(
                        apisession,
                        org_id=str(org_id),
                        avprofile_id=str(object_id),
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.avprofiles.createOrgAntivirusProfile(
                        apisession, org_id=str(org_id), body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.avprofiles.deleteOrgAntivirusProfile(
                        apisession, org_id=str(org_id), avprofile_id=str(object_id)
                    )
                    await process_response(response)
            case "org_deviceprofiles":
                if action_type.value == "update":
                    response = (
                        mistapi.api.v1.orgs.deviceprofiles.updateOrgDeviceProfile(
                            apisession,
                            org_id=str(org_id),
                            deviceprofile_id=str(object_id),
                            body=payload,
                        )
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = (
                        mistapi.api.v1.orgs.deviceprofiles.createOrgDeviceProfile(
                            apisession, org_id=str(org_id), body=payload
                        )
                    )
                    await process_response(response)
                else:
                    response = (
                        mistapi.api.v1.orgs.deviceprofiles.deleteOrgDeviceProfile(
                            apisession,
                            org_id=str(org_id),
                            deviceprofile_id=str(object_id),
                        )
                    )
                    await process_response(response)
            case "org_gatewaytemplates":
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
                elif action_type.value == "create":
                    response = (
                        mistapi.api.v1.orgs.gatewaytemplates.createOrgGatewayTemplate(
                            apisession, org_id=str(org_id), body=payload
                        )
                    )
                    await process_response(response)
                else:
                    response = (
                        mistapi.api.v1.orgs.gatewaytemplates.deleteOrgGatewayTemplate(
                            apisession,
                            org_id=str(org_id),
                            gatewaytemplate_id=str(object_id),
                        )
                    )
                    await process_response(response)
            case "org_idpprofiles":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.idpprofiles.updateOrgIdpProfile(
                        apisession,
                        org_id=str(org_id),
                        idpprofile_id=str(object_id),
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.idpprofiles.createOrgIdpProfile(
                        apisession, org_id=str(org_id), body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.idpprofiles.deleteOrgIdpProfile(
                        apisession, org_id=str(org_id), idpprofile_id=str(object_id)
                    )
                    await process_response(response)
            case "org_aamwprofiles":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.aamwprofiles.updateOrgAAMWProfile(
                        apisession,
                        org_id=str(org_id),
                        aamwprofile_id=str(object_id),
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.aamwprofiles.createOrgAAMWProfile(
                        apisession, org_id=str(org_id), body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.aamwprofiles.deleteOrgAAMWProfile(
                        apisession, org_id=str(org_id), aamwprofile_id=str(object_id)
                    )
                    await process_response(response)
            case "org_nactags":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.nactags.updateOrgNacTag(
                        apisession,
                        org_id=str(org_id),
                        nactag_id=str(object_id),
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.nactags.createOrgNacTag(
                        apisession, org_id=str(org_id), body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.nactags.deleteOrgNacTag(
                        apisession, org_id=str(org_id), nactag_id=str(object_id)
                    )
                    await process_response(response)
            case "org_nacrules":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.nacrules.updateOrgNacRule(
                        apisession,
                        org_id=str(org_id),
                        nacrule_id=str(object_id),
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.nacrules.createOrgNacRule(
                        apisession, org_id=str(org_id), body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.nacrules.deleteOrgNacRule(
                        apisession, org_id=str(org_id), nacrule_id=str(object_id)
                    )
                    await process_response(response)
            case "org_networktemplates":
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
                elif action_type.value == "create":
                    response = (
                        mistapi.api.v1.orgs.networktemplates.createOrgNetworkTemplate(
                            apisession, org_id=str(org_id), body=payload
                        )
                    )
                    await process_response(response)
                else:
                    response = (
                        mistapi.api.v1.orgs.networktemplates.deleteOrgNetworkTemplate(
                            apisession,
                            org_id=str(org_id),
                            networktemplate_id=str(object_id),
                        )
                    )
                    await process_response(response)
            case "org_networks":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.networks.updateOrgNetwork(
                        apisession,
                        org_id=str(org_id),
                        network_id=str(object_id),
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.networks.createOrgNetwork(
                        apisession, org_id=str(org_id), body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.networks.deleteOrgNetwork(
                        apisession, org_id=str(org_id), network_id=str(object_id)
                    )
                    await process_response(response)
            case "org_psks":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.psks.updateOrgPsk(
                        apisession,
                        org_id=str(org_id),
                        psk_id=str(object_id),
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.psks.createOrgPsk(
                        apisession, org_id=str(org_id), body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.psks.deleteOrgPsk(
                        apisession, org_id=str(org_id), psk_id=str(object_id)
                    )
                    await process_response(response)
            case "org_rftemplates":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.rftemplates.updateOrgRfTemplate(
                        apisession,
                        org_id=str(org_id),
                        rftemplate_id=str(object_id),
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.rftemplates.createOrgRfTemplate(
                        apisession, org_id=str(org_id), body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.rftemplates.deleteOrgRfTemplate(
                        apisession, org_id=str(org_id), rftemplate_id=str(object_id)
                    )
                    await process_response(response)
            case "org_services":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.services.updateOrgService(
                        apisession,
                        org_id=str(org_id),
                        service_id=str(object_id),
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.services.createOrgService(
                        apisession, org_id=str(org_id), body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.services.deleteOrgService(
                        apisession, org_id=str(org_id), service_id=str(object_id)
                    )
                    await process_response(response)
            case "org_servicepolicies":
                if action_type.value == "update":
                    response = (
                        mistapi.api.v1.orgs.servicepolicies.updateOrgServicePolicy(
                            apisession,
                            org_id=str(org_id),
                            servicepolicy_id=str(object_id),
                            body=payload,
                        )
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = (
                        mistapi.api.v1.orgs.servicepolicies.createOrgServicePolicy(
                            apisession, org_id=str(org_id), body=payload
                        )
                    )
                    await process_response(response)
                else:
                    response = (
                        mistapi.api.v1.orgs.servicepolicies.deleteOrgServicePolicy(
                            apisession,
                            org_id=str(org_id),
                            servicepolicy_id=str(object_id),
                        )
                    )
                    await process_response(response)
            case "org_sitetemplates":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.sitetemplates.updateOrgSiteTemplate(
                        apisession,
                        org_id=str(org_id),
                        sitetemplate_id=str(object_id),
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.sitetemplates.createOrgSiteTemplate(
                        apisession, org_id=str(org_id), body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.sitetemplates.deleteOrgSiteTemplate(
                        apisession, org_id=str(org_id), sitetemplate_id=str(object_id)
                    )
                    await process_response(response)
            case "org_vpns":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.vpns.updateOrgVpn(
                        apisession,
                        org_id=str(org_id),
                        vpn_id=str(object_id),
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.vpns.createOrgVpn(
                        apisession, org_id=str(org_id), body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.vpns.deleteOrgVpn(
                        apisession, org_id=str(org_id), vpn_id=str(object_id)
                    )
                    await process_response(response)
            case "org_webhooks":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.webhooks.updateOrgWebhook(
                        apisession,
                        org_id=str(org_id),
                        webhook_id=str(object_id),
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.webhooks.createOrgWebhook(
                        apisession, org_id=str(org_id), body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.webhooks.deleteOrgWebhook(
                        apisession, org_id=str(org_id), webhook_id=str(object_id)
                    )
                    await process_response(response)
            case "org_wlantemplates":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.templates.updateOrgTemplate(
                        apisession,
                        org_id=str(org_id),
                        template_id=str(object_id),
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.templates.createOrgTemplate(
                        apisession, org_id=str(org_id), body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.templates.deleteOrgTemplate(
                        apisession, org_id=str(org_id), template_id=str(object_id)
                    )
                    await process_response(response)
            case "org_wxrules":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.wxrules.updateOrgWxRule(
                        apisession,
                        org_id=str(org_id),
                        wxrule_id=str(object_id),
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.wxrules.createOrgWxRule(
                        apisession, org_id=str(org_id), body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.wxrules.deleteOrgWxRule(
                        apisession, org_id=str(org_id), wxrule_id=str(object_id)
                    )
                    await process_response(response)
            case "org_wxtags":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.wxtags.updateOrgWxTag(
                        apisession,
                        org_id=str(org_id),
                        wxtag_id=str(object_id),
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.wxtags.createOrgWxTag(
                        apisession, org_id=str(org_id), body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.wxtags.deleteOrgWxTag(
                        apisession, org_id=str(org_id), wxtag_id=str(object_id)
                    )
                    await process_response(response)
            case "site_info":
                if action_type.value == "update":
                    response = mistapi.api.v1.sites.updateSite(
                        apisession,
                        site_id=str(site_id),
                        body=payload,
                    )
                    await process_response(response)
                else:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": "Only 'update' action is supported for 'site_info' object type.",
                        }
                    )
            case "site_devices":
                if action_type.value == "update":
                    response = mistapi.api.v1.sites.devices.updateSiteDevice(
                        apisession,
                        site_id=str(site_id),
                        device_id=str(object_id),
                        body=payload,
                    )
                    await process_response(response)
            case "site_psks":
                if action_type.value == "update":
                    response = mistapi.api.v1.sites.psks.updateSitePsk(
                        apisession,
                        site_id=str(site_id),
                        psk_id=str(object_id),
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.sites.psks.createSitePsk(
                        apisession, site_id=str(site_id), body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.sites.psks.deleteSitePsk(
                        apisession, site_id=str(site_id), psk_id=str(object_id)
                    )
                    await process_response(response)
            case "site_webhooks":
                if action_type.value == "update":
                    response = mistapi.api.v1.sites.webhooks.updateSiteWebhook(
                        apisession,
                        site_id=str(site_id),
                        webhook_id=str(object_id),
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.sites.webhooks.createSiteWebhook(
                        apisession, site_id=str(site_id), body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.sites.webhooks.deleteSiteWebhook(
                        apisession, site_id=str(site_id), webhook_id=str(object_id)
                    )
                    await process_response(response)
            case "site_wlans":
                if action_type.value == "update":
                    response = mistapi.api.v1.sites.wlans.updateSiteWlan(
                        apisession,
                        site_id=str(site_id),
                        wlan_id=str(object_id),
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.sites.wlans.createSiteWlan(
                        apisession, site_id=str(site_id), body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.sites.wlans.deleteSiteWlan(
                        apisession, site_id=str(site_id), wlan_id=str(object_id)
                    )
                    await process_response(response)
            case "site_wxrules":
                if action_type.value == "update":
                    response = mistapi.api.v1.sites.wxrules.updateSiteWxRule(
                        apisession,
                        site_id=str(site_id),
                        wxrule_id=str(object_id),
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.sites.wxrules.createSiteWxRule(
                        apisession, site_id=str(site_id), body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.sites.wxrules.deleteSiteWxRule(
                        apisession, site_id=str(site_id), wxrule_id=str(object_id)
                    )
                    await process_response(response)
            case "site_wxtags":
                if action_type.value == "update":
                    response = mistapi.api.v1.sites.wxtags.updateSiteWxTag(
                        apisession,
                        site_id=str(site_id),
                        wxtag_id=str(object_id),
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.sites.wxtags.createSiteWxTag(
                        apisession, site_id=str(site_id), body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.sites.wxtags.deleteSiteWxTag(
                        apisession, site_id=str(site_id), wxtag_id=str(object_id)
                    )
                    await process_response(response)

            case _:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Object_type]}",
                    }
                )

    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
'''
