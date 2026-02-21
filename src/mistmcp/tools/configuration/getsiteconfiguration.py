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

from mistmcp.request_processor import get_apisession
from mistmcp.response_processor import process_response
from mistmcp.response_formatter import format_response
from mistmcp.server import mcp
from mistmcp.logger import logger


class Object_type(Enum):
    SITE = "site"
    WLANS = "wlans"
    RF_TEMPLATE = "rf_template"
    NETWORK_TEMPLATE = "network_template"
    GATEWAY_TEMPLATE = "gateway_template"
    ALARM_TEMPLATE = "alarm_template"


NETWORK_TEMPLATE_FIELDS = [
    "auto_upgrade_linecard",
    "acl_policies",
    "acl_tags",
    "additional_config_cmds",
    "dhcp_snooping",
    "disabled_system_defined_port_usages",
    "dns_servers",
    "dns_suffix",
    "extra_routes",
    "extra_routes6",
    "fips_enabled",
    "id",
    "mist_nac",
    "networks",
    "ntp_servers",
    "port_mirroring",
    "port_usages",
    "radius_config",
    "remote_syslog",
    "snmp_config",
    "routing_policies",
    "switch_matching",
    "switch_mgmt",
    "vrf_config",
    "vrf_instances",
]


@mcp.tool(
    name="getSiteDerivedConfiguration",
    description="""Retrieve derived configuration (org + site configuration) for a specific site.""",
    tags={"configuration"},
    annotations={
        "title": "getSiteDerivedConfiguration",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getSiteDerivedConfiguration(
    org_id: Annotated[
        UUID,
        Field(description="""ID of the Mist Org"""),
    ],
    site_id: Annotated[
        UUID,
        Field(description="""ID of the site to retrieve configuration objects from."""),
    ],
    object_type: Annotated[
        Object_type, Field(description="""Type of configuration object to retrieve.""")
    ],
    ctx: Context | None = None,
) -> dict | list | str:
    """Retrieve derived configuration (org + site configuration) for a specific site"""

    logger.debug("Tool {operationId} called")

    apisession, response_format = get_apisession()

    site_data = mistapi.api.v1.sites.sites.getSiteInfo(apisession, site_id=str(site_id))
    await process_response(site_data)

    data = {}
    match object_type.value:
        case "wlans":
            sitegroup_ids = site_data.data.get("sitegroup_ids", [])
            assigned_template_ids = []
            assigned_wlans = []
            # ORG TEMPLATES
            org_wlan_templates = mistapi.api.v1.orgs.templates.listOrgTemplates(
                apisession, org_id=str(org_id), limit=1000
            )
            await process_response(org_wlan_templates)
            for template in org_wlan_templates.data:
                applies = template.get("applies", {})
                template_org_id = applies.get("org_id", "")
                template_site_ids = applies.get("site_ids", []) or []
                template_sitegroup_ids = applies.get("sitegroup_ids", []) or []
                if (
                    str(site_id) in template_site_ids
                    or (set(template_sitegroup_ids) & set(sitegroup_ids))
                    or template_org_id == str(org_id)
                ):
                    assigned_template_ids.append(template.get("id"))
            # ORG WLANS
            org_wlans = mistapi.api.v1.orgs.wlans.listOrgWlans(
                apisession, org_id=str(org_id), limit=1000
            )
            await process_response(org_wlans)
            for wlan in org_wlans.data:
                if wlan.get("template_id") in assigned_template_ids:
                    assigned_wlans.append(wlan)
            # SITE WLANS
            site_wlans = mistapi.api.v1.sites.wlans.listSiteWlans(
                apisession, site_id=str(site_id), limit=1000
            )
            await process_response(site_wlans)
            for wlan in site_wlans.data:
                assigned_wlans.append(wlan)
            data = assigned_wlans

        case "rf_template":
            rf_template_id = site_data.data.get("rftemplate_id")
            if rf_template_id:
                response = mistapi.api.v1.orgs.rftemplates.getOrgRfTemplate(
                    apisession, org_id=str(org_id), rftemplate_id=str(rf_template_id)
                )
                await process_response(response)
                data = response.data
            else:
                data = {}

        case "alarm_template":
            alarm_template_id = None
            if site_data.data.get("alarmtemplate_id"):
                alarm_template_id = site_data.data.get("alarmtemplate_id")
            else:
                org_info = mistapi.api.v1.orgs.orgs.getOrg(
                    apisession, org_id=str(org_id)
                )
                await process_response(org_info)
                alarm_template_id = org_info.data.get("alarmtemplate_id")
            if alarm_template_id:
                response = mistapi.api.v1.orgs.alarmtemplates.getOrgAlarmTemplate(
                    apisession,
                    org_id=str(org_id),
                    alarmtemplate_id=str(alarm_template_id),
                )
                await process_response(response)
                data = response.data
            else:
                data = {}

        case "network_template":
            network_template_id = site_data.data.get("networktemplate_id")
            if network_template_id:
                response = mistapi.api.v1.orgs.networktemplates.getOrgNetworkTemplate(
                    apisession,
                    org_id=str(org_id),
                    networktemplate_id=str(network_template_id),
                )
                await process_response(response)
                data = response.data
            else:
                data = {}

            site_config = mistapi.api.v1.sites.setting.getSiteSetting(
                apisession, site_id=str(site_id)
            )
            await process_response(site_config)

            for key, value in site_config.data.items():
                if key in NETWORK_TEMPLATE_FIELDS:
                    if isinstance(value, dict) and isinstance(data.get(key, {}), dict):
                        data[key] = {**data.get(key, {}), **value}
                    elif isinstance(value, list) and isinstance(
                        data.get(key, []), list
                    ):
                        data[key] = data.get(key, []) + value
                    else:
                        data[key] = value

        case "gateway_template":
            gateway_template_id = site_data.data.get("gatewaytemplate_id")
            if gateway_template_id:
                response = mistapi.api.v1.orgs.gatewaytemplates.getOrgGatewayTemplate(
                    apisession,
                    org_id=str(org_id),
                    gatewaytemplate_id=str(gateway_template_id),
                )
                await process_response(response)
                data = response.data

        case "site":
            site_template_id = site_data.data.get("sitetemplate_id")
            if site_template_id:
                response = mistapi.api.v1.orgs.sitetemplates.getOrgSiteTemplate(
                    apisession,
                    org_id=str(org_id),
                    sitetemplate_id=str(site_template_id),
                )
                await process_response(response)
                data = response.data
            else:
                data = {}

            site_config = mistapi.api.v1.sites.setting.getSiteSetting(
                apisession, site_id=str(site_id)
            )
            await process_response(site_config)

            for key, value in site_config.data.items():
                if key not in NETWORK_TEMPLATE_FIELDS:
                    if isinstance(value, dict) and isinstance(data.get(key, {}), dict):
                        data[key] = {**data.get(key, {}), **value}
                    elif isinstance(value, list) and isinstance(
                        data.get(key, []), list
                    ):
                        data[key] = data.get(key, []) + value
                    else:
                        data[key] = value

        case _:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Object_type]}",
                }
            )

    return format_response(data, response_format)
