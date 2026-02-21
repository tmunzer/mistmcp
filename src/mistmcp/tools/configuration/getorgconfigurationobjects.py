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
    ORG = "org"
    ALARMTEMPLATES = "alarmtemplates"
    WLANS = "wlans"
    SITEGROUPS = "sitegroups"
    AVPROFILES = "avprofiles"
    DEVICES = "devices"
    DEVICEPROFILES = "deviceprofiles"
    EVPN_TOPOLOGIES = "evpn_topologies"
    GATEWAYTEMPLATES = "gatewaytemplates"
    IDPPROFILES = "idpprofiles"
    AAMWPROFILES = "aamwprofiles"
    MXCLUSTERS = "mxclusters"
    MXEDGES = "mxedges"
    MXTUNNELS = "mxtunnels"
    NACTAGS = "nactags"
    NACRULES = "nacrules"
    NETWORKTEMPLATES = "networktemplates"
    NETWORKS = "networks"
    PSKS = "psks"
    RFTEMPLATES = "rftemplates"
    SERVICES = "services"
    SERVICEPOLICIES = "servicepolicies"
    SITES = "sites"
    SITETEMPLATES = "sitetemplates"
    VPNS = "vpns"
    WEBHOOKS = "webhooks"
    WLANTEMPLATES = "wlantemplates"
    WXRULES = "wxrules"
    WXTAGS = "wxtags"


@mcp.tool(
    name="getOrgConfigurationObjects",
    description="""Retrieve configuration objects from a specified organization""",
    tags={"configuration"},
    annotations={
        "title": "getOrgConfigurationObjects",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getOrgConfigurationObjects(
    org_id: Annotated[UUID, Field(description="""Organization ID""")],
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
    """Retrieve configuration objects from a specified organization"""

    logger.debug("Tool getOrgConfigurationObjects called")

    apisession, response_format = get_apisession()

    match object_type.value:
        case "org":
            response = mistapi.api.v1.orgs.setting.getOrgSettings(
                apisession, org_id=str(org_id)
            )
            await process_response(response)
        case "alarmtemplates":
            if object_id:
                response = mistapi.api.v1.orgs.alarmtemplates.getOrgAlarmTemplate(
                    apisession, org_id=str(org_id), alarmtemplate_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.alarmtemplates.listOrgAlarmTemplates(
                    apisession, org_id=str(org_id), limit=limit
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
                response = mistapi.api.v1.orgs.wlans.getOrgWLAN(
                    apisession, org_id=str(org_id), wlan_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.wlans.listOrgWlans(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = {
                    item.get("ssid"): item.get("id")
                    for item in response.data
                    if item.get("ssid")
                }
                response.data = data
        case "sitegroups":
            if object_id:
                response = mistapi.api.v1.orgs.sitegroups.getOrgSiteGroup(
                    apisession, org_id=str(org_id), sitegroup_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.sitegroups.listOrgSiteGroups(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
        case "avprofiles":
            if object_id:
                response = mistapi.api.v1.orgs.avprofiles.getOrgAntivirusProfile(
                    apisession, org_id=str(org_id), avprofile_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.avprofiles.listOrgAntivirusProfiles(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = {
                    item.get("name"): item.get("id")
                    for item in response.data
                    if item.get("name")
                }
                response.data = data
        case "devices":
            response = mistapi.api.v1.orgs.devices.listOrgDevices(
                apisession, org_id=str(org_id)
            )
            await process_response(response)
        case "deviceprofiles":
            if object_id:
                response = mistapi.api.v1.orgs.deviceprofiles.getOrgDeviceProfile(
                    apisession, org_id=str(org_id), deviceprofile_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.deviceprofiles.listOrgDeviceProfiles(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = {
                    item.get("name"): item.get("id")
                    for item in response.data
                    if item.get("name")
                }
                response.data = data
        case "evpn_topologies":
            if object_id:
                response = mistapi.api.v1.orgs.evpn_topologies.getOrgEvpnTopology(
                    apisession, org_id=str(org_id), evpn_topology_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.evpn_topologies.listOrgEvpnTopologies(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = {
                    item.get("name"): item.get("id")
                    for item in response.data
                    if item.get("name")
                }
                response.data = data
        case "gatewaytemplates":
            if object_id:
                response = mistapi.api.v1.orgs.gatewaytemplates.getOrgGatewayTemplate(
                    apisession, org_id=str(org_id), gatewaytemplate_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.gatewaytemplates.listOrgGatewayTemplates(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = {
                    item.get("name"): item.get("id")
                    for item in response.data
                    if item.get("name")
                }
                response.data = data
        case "idpprofiles":
            if object_id:
                response = mistapi.api.v1.orgs.idpprofiles.getOrgIdpProfile(
                    apisession, org_id=str(org_id), idpprofile_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.idpprofiles.listOrgIdpProfiles(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = {
                    item.get("name"): item.get("id")
                    for item in response.data
                    if item.get("name")
                }
                response.data = data
        case "aamwprofiles":
            if object_id:
                response = mistapi.api.v1.orgs.aamwprofiles.getOrgAAMWProfile(
                    apisession, org_id=str(org_id), aamwprofile_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.aamwprofiles.listOrgAAMWProfiles(
                    apisession, org_id=str(org_id)
                )
                await process_response(response)
                data = {
                    item.get("name"): item.get("id")
                    for item in response.data
                    if item.get("name")
                }
                response.data = data
        case "mxclusters":
            if object_id:
                response = mistapi.api.v1.orgs.mxclusters.getOrgMxEdgeCluster(
                    apisession, org_id=str(org_id), mxcluster_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.mxclusters.listOrgMxEdgeClusters(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
        case "mxedges":
            if object_id:
                response = mistapi.api.v1.orgs.mxedges.getOrgMxEdge(
                    apisession, org_id=str(org_id), mxedge_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.mxedges.listOrgMxEdges(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
        case "mxtunnels":
            if object_id:
                response = mistapi.api.v1.orgs.mxtunnels.getOrgMxTunnel(
                    apisession, org_id=str(org_id), mxtunnel_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.mxtunnels.listOrgMxTunnels(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
        case "nactags":
            if object_id:
                response = mistapi.api.v1.orgs.nactags.getOrgNacTag(
                    apisession, org_id=str(org_id), nactag_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.nactags.listOrgNacTags(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
        case "nacrules":
            if object_id:
                response = mistapi.api.v1.orgs.nacrules.getOrgNacRule(
                    apisession, org_id=str(org_id), nacrule_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.nacrules.listOrgNacRules(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
        case "networktemplates":
            if object_id:
                response = mistapi.api.v1.orgs.networktemplates.getOrgNetworkTemplate(
                    apisession, org_id=str(org_id), networktemplate_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.networktemplates.listOrgNetworkTemplates(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = {
                    item.get("name"): item.get("id")
                    for item in response.data
                    if item.get("name")
                }
                response.data = data
        case "networks":
            if object_id:
                response = mistapi.api.v1.orgs.networks.getOrgNetwork(
                    apisession, org_id=str(org_id), network_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.networks.listOrgNetworks(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
        case "psks":
            if object_id:
                response = mistapi.api.v1.orgs.psks.getOrgPsk(
                    apisession, org_id=str(org_id), psk_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.psks.listOrgPsks(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
        case "rftemplates":
            if object_id:
                response = mistapi.api.v1.orgs.rftemplates.getOrgRfTemplate(
                    apisession, org_id=str(org_id), rftemplate_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.rftemplates.listOrgRfTemplates(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = {
                    item.get("name"): item.get("id")
                    for item in response.data
                    if item.get("name")
                }
                response.data = data
        case "services":
            if object_id:
                response = mistapi.api.v1.orgs.services.getOrgService(
                    apisession, org_id=str(org_id), service_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.services.listOrgServices(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = {
                    item.get("name"): item.get("id")
                    for item in response.data
                    if item.get("name")
                }
                response.data = data
        case "servicepolicies":
            if object_id:
                response = mistapi.api.v1.orgs.servicepolicies.getOrgServicePolicy(
                    apisession, org_id=str(org_id), servicepolicy_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.servicepolicies.listOrgServicePolicies(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = {
                    item.get("name"): item.get("id")
                    for item in response.data
                    if item.get("name")
                }
                response.data = data
        case "sites":
            response = mistapi.api.v1.orgs.sites.listOrgSites(
                apisession, org_id=str(org_id), limit=limit
            )
            await process_response(response)
        case "sitetemplates":
            if object_id:
                response = mistapi.api.v1.orgs.sitetemplates.getOrgSiteTemplate(
                    apisession, org_id=str(org_id), sitetemplate_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.sitetemplates.listOrgSiteTemplates(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = {
                    item.get("name"): item.get("id")
                    for item in response.data
                    if item.get("name")
                }
                response.data = data
        case "vpns":
            if object_id:
                response = mistapi.api.v1.orgs.vpns.getOrgVpn(
                    apisession, org_id=str(org_id), vpn_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.vpns.listOrgVpns(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
        case "webhooks":
            if object_id:
                response = mistapi.api.v1.orgs.webhooks.getOrgWebhook(
                    apisession, org_id=str(org_id), webhook_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.webhooks.listOrgWebhooks(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
        case "wlantemplates":
            if object_id:
                response = mistapi.api.v1.orgs.templates.getOrgTemplate(
                    apisession, org_id=str(org_id), template_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.templates.listOrgTemplates(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = {
                    item.get("name"): item.get("id")
                    for item in response.data
                    if item.get("name")
                }
                response.data = data
        case "wxrules":
            if object_id:
                response = mistapi.api.v1.orgs.wxrules.getOrgWxRule(
                    apisession, org_id=str(org_id), wxrule_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.wxrules.listOrgWxRules(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
        case "wxtags":
            if object_id:
                response = mistapi.api.v1.orgs.wxtags.getOrgWxTag(
                    apisession, org_id=str(org_id), wxtag_id=str(object_id)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.wxtags.listOrgWxTags(
                    apisession, org_id=str(org_id), limit=limit
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
