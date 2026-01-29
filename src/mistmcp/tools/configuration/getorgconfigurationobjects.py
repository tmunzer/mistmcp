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
    ALARMTEMPLATES = "alarmtemplates"
    WLANS = "wlans"
    SITEGROUPS = "sitegroups"
    APTEMPLATES = "aptemplates"
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
    WLANTEMPLATES = "wlantemplates"
    VPNS = "vpns"
    WEBHOOKS = "webhooks"
    WXRULES = "wxrules"
    WXTAGS = "wxtags"


@mcp.tool(
    enabled=False,
    name="getOrgConfigurationObjects",
    description="""Retrieve configuration objects from a specified organization or site.""",
    tags={"configuration"},
    annotations={
        "title": "getOrgConfigurationObjects",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getOrgConfigurationObjects(
    org_id: Annotated[
        UUID,
        Field(
            description="""ID of the organization or site to retrieve configuration objects from."""
        ),
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
) -> dict | list:
    """Retrieve configuration objects from a specified organization or site."""

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

    if not apitoken:
        raise ClientError(
            "Missing required parameter: 'X-Authorization' header or mist_apitoken in config"
        )
    if not cloud:
        raise ClientError(
            "Missing required parameter: 'cloud' query parameter or mist_host in config"
        )

    apisession = mistapi.APISession(
        host=cloud,
        apitoken=apitoken,
    )

    match object_type.value:
        case "alarmtemplates":
            if object_id:
                response = mistapi.api.v1.orgs.alarmtemplates.getOrgAlarmTemplate(
                    apisession, org_id=str(org_id), alarmtemplate_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.orgs.alarmtemplates.listOrgAlarmTemplates(
                    apisession, org_id=str(org_id)
                )
        case "wlans":
            if object_id:
                response = mistapi.api.v1.orgs.wlans.getOrgWLAN(
                    apisession, org_id=str(org_id), wlan_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.orgs.wlans.listOrgWlans(
                    apisession, org_id=str(org_id)
                )
        case "sitegroups":
            if object_id:
                response = mistapi.api.v1.orgs.sitegroups.getOrgSiteGroup(
                    apisession, org_id=str(org_id), sitegroup_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.orgs.sitegroups.listOrgSiteGroups(
                    apisession, org_id=str(org_id)
                )
        case "aptemplates":
            if object_id:
                response = mistapi.api.v1.orgs.aptemplates.getOrgAptemplate(
                    apisession, org_id=str(org_id), aptemplate_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.orgs.aptemplates.listOrgAptemplates(
                    apisession, org_id=str(org_id)
                )
        case "avprofiles":
            if object_id:
                response = mistapi.api.v1.orgs.avprofiles.getOrgAntivirusProfile(
                    apisession, org_id=str(org_id), avprofile_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.orgs.avprofiles.listOrgAntivirusProfiles(
                    apisession, org_id=str(org_id)
                )
        case "devices":
            response = mistapi.api.v1.orgs.devices.listOrgDevices(
                apisession, org_id=str(org_id)
            )
        case "deviceprofiles":
            if object_id:
                response = mistapi.api.v1.orgs.deviceprofiles.getOrgDeviceProfile(
                    apisession, org_id=str(org_id), deviceprofile_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.orgs.deviceprofiles.listOrgDeviceProfiles(
                    apisession, org_id=str(org_id)
                )
        case "evpn_topologies":
            if object_id:
                response = mistapi.api.v1.orgs.evpn_topologies.getOrgEvpnTopology(
                    apisession, org_id=str(org_id), evpn_topology_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.orgs.evpn_topologies.listOrgEvpnTopologies(
                    apisession, org_id=str(org_id)
                )
        case "gatewaytemplates":
            if object_id:
                response = mistapi.api.v1.orgs.gatewaytemplates.getOrgGatewayTemplate(
                    apisession, org_id=str(org_id), gatewaytemplate_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.orgs.gatewaytemplates.listOrgGatewayTemplates(
                    apisession, org_id=str(org_id)
                )
        case "idpprofiles":
            if object_id:
                response = mistapi.api.v1.orgs.idpprofiles.getOrgIdpProfile(
                    apisession, org_id=str(org_id), idpprofile_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.orgs.idpprofiles.listOrgIdpProfiles(
                    apisession, org_id=str(org_id)
                )
        case "aamwprofiles":
            if object_id:
                response = mistapi.api.v1.orgs.aamwprofiles.getOrgAAMWProfile(
                    apisession, org_id=str(org_id), aamwprofile_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.orgs.aamwprofiles.listOrgAAMWProfiles(
                    apisession, org_id=str(org_id)
                )
        case "mxclusters":
            if object_id:
                response = mistapi.api.v1.orgs.mxclusters.getOrgMxEdgeCluster(
                    apisession, org_id=str(org_id), mxcluster_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.orgs.mxclusters.listOrgMxEdgeClusters(
                    apisession, org_id=str(org_id)
                )
        case "mxedges":
            if object_id:
                response = mistapi.api.v1.orgs.mxedges.getOrgMxEdge(
                    apisession, org_id=str(org_id), mxedge_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.orgs.mxedges.listOrgMxEdges(
                    apisession, org_id=str(org_id)
                )
        case "mxtunnels":
            if object_id:
                response = mistapi.api.v1.orgs.mxtunnels.getOrgMxTunnel(
                    apisession, org_id=str(org_id), mxtunnel_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.orgs.mxtunnels.listOrgMxTunnels(
                    apisession, org_id=str(org_id)
                )
        case "nactags":
            if object_id:
                response = mistapi.api.v1.orgs.nactags.getOrgNacTag(
                    apisession, org_id=str(org_id), nactag_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.orgs.nactags.listOrgNacTags(
                    apisession, org_id=str(org_id)
                )
        case "nacrules":
            if object_id:
                response = mistapi.api.v1.orgs.nacrules.getOrgNacRule(
                    apisession, org_id=str(org_id), nacrule_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.orgs.nacrules.listOrgNacRules(
                    apisession, org_id=str(org_id)
                )
        case "networktemplates":
            if object_id:
                response = mistapi.api.v1.orgs.networktemplates.getOrgNetworkTemplate(
                    apisession, org_id=str(org_id), networktemplate_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.orgs.networktemplates.listOrgNetworkTemplates(
                    apisession, org_id=str(org_id)
                )
        case "networks":
            if object_id:
                response = mistapi.api.v1.orgs.networks.getOrgNetwork(
                    apisession, org_id=str(org_id), network_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.orgs.networks.listOrgNetworks(
                    apisession, org_id=str(org_id)
                )
        case "psks":
            if object_id:
                response = mistapi.api.v1.orgs.psks.getOrgPsk(
                    apisession, org_id=str(org_id), psk_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.orgs.psks.listOrgPsks(
                    apisession, org_id=str(org_id)
                )
        case "rftemplates":
            if object_id:
                response = mistapi.api.v1.orgs.rftemplates.getOrgRfTemplate(
                    apisession, org_id=str(org_id), rftemplate_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.orgs.rftemplates.listOrgRfTemplates(
                    apisession, org_id=str(org_id)
                )
        case "services":
            if object_id:
                response = mistapi.api.v1.orgs.services.getOrgService(
                    apisession, org_id=str(org_id), service_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.orgs.services.listOrgServices(
                    apisession, org_id=str(org_id)
                )
        case "servicepolicies":
            if object_id:
                response = mistapi.api.v1.orgs.servicepolicies.getOrgServicePolicy(
                    apisession, org_id=str(org_id), servicepolicy_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.orgs.servicepolicies.listOrgServicePolicies(
                    apisession, org_id=str(org_id)
                )
        case "sites":
            response = mistapi.api.v1.orgs.sites.listOrgSites(
                apisession, org_id=str(org_id)
            )
        case "sitetemplates":
            if object_id:
                response = mistapi.api.v1.orgs.sitetemplates.getOrgSiteTemplate(
                    apisession, org_id=str(org_id), sitetemplate_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.orgs.sitetemplates.listOrgSiteTemplates(
                    apisession, org_id=str(org_id)
                )
        case "wlantemplates":
            if object_id:
                response = mistapi.api.v1.orgs.templates.getOrgTemplate(
                    apisession, org_id=str(org_id), template_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.orgs.templates.listOrgTemplates(
                    apisession, org_id=str(org_id)
                )
        case "vpns":
            if object_id:
                response = mistapi.api.v1.orgs.vpns.getOrgVpn(
                    apisession, org_id=str(org_id), vpn_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.orgs.vpns.listOrgVpns(
                    apisession, org_id=str(org_id)
                )
        case "webhooks":
            if object_id:
                response = mistapi.api.v1.orgs.webhooks.getOrgWebhook(
                    apisession, org_id=str(org_id), webhook_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.orgs.webhooks.listOrgWebhooks(
                    apisession, org_id=str(org_id)
                )
        case "wxrules":
            if object_id:
                response = mistapi.api.v1.orgs.wxrules.getOrgWxRule(
                    apisession, org_id=str(org_id), wxrule_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.orgs.wxrules.listOrgWxRules(
                    apisession, org_id=str(org_id)
                )
        case "wxtags":
            if object_id:
                response = mistapi.api.v1.orgs.wxtags.getOrgWxTag(
                    apisession, org_id=str(org_id), wxtag_id=str(object_id)
                )
            else:
                response = mistapi.api.v1.orgs.wxtags.listOrgWxTags(
                    apisession, org_id=str(org_id)
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
            # await ctx.error(f"Got HTTP{response.status_code} with details {response.data}")
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
                "Not found. The API endpoint doesn't exist or resource doesn't exist"
            )
        elif response.status_code == 429:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps(
                "Too Many Request. The API Token used for the request reached the 5000 API Calls per hour threshold"
            )
        raise ToolError(api_error)

    return response.data
