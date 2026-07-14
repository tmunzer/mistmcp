"""Configuration object and device-history facade tool."""

from enum import Enum
from typing import Annotated
from uuid import UUID

import mistapi
from fastmcp.exceptions import ToolError
from fastmcp.tools import ToolResult
from mistapi.__api_response import APIResponse as _APIResponse
from pydantic import Field
from requests.structures import CaseInsensitiveDict

from mistmcp.logger import logger
from mistmcp.request_processor import get_apisession
from mistmcp.response_formatter import format_response
from mistmcp.response_processor import handle_network_error, process_response
from mistmcp.server import mcp
from mistmcp.tools._facade import arguments, internal_tool, run_internal_tool


class ConfigurationOperation(Enum):
    OBJECTS = "objects"
    DEVICE_HISTORY = "device_history"


class Object_type(Enum):
    ORG_INFO = "org_info"
    ORG_SETTINGS = "org_settings"
    ORG_ALARMTEMPLATES = "org_alarmtemplates"
    ORG_WLANS = "org_wlans"
    ORG_SITEGROUPS = "org_sitegroups"
    ORG_AVPROFILES = "org_avprofiles"
    ORG_DEVICEPROFILES = "org_deviceprofiles"
    ORG_EVPN_TOPOLOGIES = "org_evpn_topologies"
    ORG_GATEWAYTEMPLATES = "org_gatewaytemplates"
    ORG_IDPPROFILES = "org_idpprofiles"
    ORG_AAMWPROFILES = "org_aamwprofiles"
    ORG_MXCLUSTERS = "org_mxclusters"
    ORG_MXEDGES = "org_mxedges"
    ORG_MXTUNNELS = "org_mxtunnels"
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
    ORG_GUEST_AUTHORIZATIONS = "org_guest_authorizations"
    SITE_INFO = "site_info"
    SITE_SETTINGS = "site_settings"
    SITE_EVPN_TOPOLOGIES = "site_evpn_topologies"
    SITE_MAPS = "site_maps"
    SITE_MXEDGES = "site_mxedges"
    SITE_PSKS = "site_psks"
    SITE_WEBHOOKS = "site_webhooks"
    SITE_WLANS = "site_wlans"
    SITE_WXRULES = "site_wxrules"
    SITE_WXTAGS = "site_wxtags"
    SITE_DEVICES = "site_devices"
    SITE_GUEST_AUTHORIZATIONS = "site_guest_authorizations"


_CONFIGURATION_OBJECT_DESCRIPTIONS = {
    "org_info": "organization identity and metadata",
    "org_settings": "organization-wide settings",
    "org_alarmtemplates": "alarm templates",
    "org_wlans": "organization WLAN definitions",
    "org_sitegroups": "site groups",
    "org_avprofiles": "antivirus profiles",
    "org_deviceprofiles": "device profiles",
    "org_evpn_topologies": "organization EVPN topologies",
    "org_gatewaytemplates": "gateway templates",
    "org_idpprofiles": "intrusion-detection and prevention profiles",
    "org_aamwprofiles": "advanced anti-malware profiles",
    "org_mxclusters": "Mist Edge clusters",
    "org_mxedges": "Mist Edge inventory and configuration",
    "org_mxtunnels": "Mist Edge tunnels",
    "org_nactags": "NAC tags",
    "org_nacrules": "NAC policy rules",
    "org_networktemplates": "switch network templates",
    "org_networks": "organization network definitions",
    "org_psks": "organization pre-shared keys",
    "org_rftemplates": "RF templates",
    "org_services": "WAN services",
    "org_servicepolicies": "WAN service policies",
    "org_sites": "sites in the organization; site_id selects one site",
    "org_sitetemplates": "site templates",
    "org_vpns": "organization VPN definitions",
    "org_webhooks": "organization webhooks",
    "org_wlantemplates": "WLAN templates",
    "org_wxrules": "organization WxLAN policy rules",
    "org_wxtags": "organization WxLAN tags",
    "org_guest_authorizations": "pre-created organization guest authorization records, optionally selected by guest_mac",
    "site_info": "site identity and metadata",
    "site_settings": "site settings",
    "site_evpn_topologies": "site EVPN topologies",
    "site_maps": "site floor maps",
    "site_mxedges": "Mist Edges assigned to a site",
    "site_psks": "site pre-shared keys",
    "site_webhooks": "site webhooks",
    "site_wlans": "site WLANs; computed=true includes inherited organization WLANs",
    "site_wxrules": "site WxLAN policy rules",
    "site_wxtags": "site WxLAN tags",
    "site_devices": "site device configuration; computed=true includes inherited settings",
    "site_guest_authorizations": "pre-created site guest authorization records, optionally selected by guest_mac",
}


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


async def get_configuration_objects(
    org_id: Annotated[UUID, Field(description="Organization ID")],
    object_type: Annotated[
        Object_type, Field(
            description="Type of configuration object to retrieve")
    ],
    site_id: Annotated[
        UUID,
        Field(
            default=None,
            description="ID of the site to retrieve configuration objects from. Required when object_type is starting with `site_`, optional if object_type is 'org_sites' to retrieve a single site",
        ),
    ],
    object_id: Annotated[
        UUID,
        Field(
            default=None,
            description="ID of the specific configuration object to retrieve. If not provided, all objects of the specified type will be retrieved.  Not supported when `object_type` is `org_guest_authorizations` or `site_guest_authorizations`",
        ),
    ],
    name: Annotated[
        str,
        Field(
            default=None,
            description="Name of the specific configuration object to retrieve. Not supported when `object_type` is `org_info`, `org_settings`, `site_info`, `site_settings`, `site_devices`, `org_guest_authorizations` or `site_guest_authorizations` (use the `mist_search_assets` tool if you need to find a specific device). If not provided, all objects of the specified type will be retrieved. Case insensitive. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `aabbcc*` and `*bbcc*` match `aabbccddeeff`). Suffix-only wildcards (e.g. `*bccddeeff`) are not supported",
        ),
    ],
    guest_mac: Annotated[
        str,
        Field(
            default=None,
            description="MAC address of the guest to retrieve authorization records for. Only applicable when `object_type` is `org_guest_authorizations` or `site_guest_authorizations`. If not provided, all guest authorization records will be retrieved. Format is `aabbccddeeff` or `aa:bb:cc:dd:ee:ff` (case insensitive)",
        ),
    ],
    computed: Annotated[
        bool,
        Field(
            default=None,
            description="Whether to retrieve the computed configuration object with all inherited settings applied. Only considered when object_type is `org_sites` and `site_devices` when a single object is returned, or when object_type is `site_wlans`",
        ),
    ],
    limit: Annotated[
        int,
        Field(
            default=20,
            description="Max number of results per page. Default is 20, Max is 1000. Not supported when `object_type` is `org_info`, `org_settings`, `site_info` or `site_settings`",
        ),
    ] = 20,
) -> dict | list | str:
    """Retrieve configuration objects from a specified organization or site. For the site configuration objects, set the attribute `computed` to `true` to retrieve the computed configuration including all configuration objects defined at the org level and assigned to the site. This tool allows you to retrieve a list of configuration objects (e.g. wlans, device profiles, network templates) or to filter them providing their ID."""
    logger.debug("Tool get_configuration_objects called")
    logger.debug(
        "Input Parameters: org_id=%s, object_type=%s, site_id=%s, object_id=%s, name=%s, computed=%s, limit=%s",
        org_id,
        object_type,
        site_id,
        object_id,
        name,
        computed,
        limit,
    )
    apisession, response_format = await get_apisession()
    response
    try:
        if object_type.value.startswith("site_"):
            if not site_id:
                raise ToolError(
                    "site_id is required when object_type starts with 'site_'"
                )
            else:
                response = await _site_configuration_objects_getter(
                    apisession=apisession,
                    object_type=object_type.value,
                    org_id=str(org_id),
                    site_id=str(site_id),
                    object_id=str(object_id) if object_id else None,
                    name=name if name else None,
                    guest_mac=guest_mac if guest_mac else None,
                    computed=computed,
                    limit=limit if limit else 20,
                )
        else:
            response = await _org_configuration_objects_getter(
                apisession=apisession,
                object_type=object_type.value,
                org_id=str(org_id),
                site_id=str(site_id) if site_id else None,
                object_id=str(object_id) if object_id else None,
                name=name if name else None,
                guest_mac=guest_mac if guest_mac else None,
                limit=limit if limit else 20,
                computed=computed if computed else None,
            )
    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)
    if response is None:
        raise ToolError(
            {
                "status_code": 503,
                "message": "API call failed: No response object was created due to an error.",
            }
        )
    return format_response(response, response_format)


async def _org_configuration_objects_getter(
    apisession: mistapi.APISession,
    object_type: str,
    org_id: str,
    site_id: str | None,
    object_id: str | None,
    name: str | None,
    guest_mac: str | None,
    computed: bool | None,
    limit: int = 20,
) -> _APIResponse:
    match object_type:
        case "org_info":
            response = mistapi.api.v1.orgs.orgs.getOrg(
                apisession, org_id=str(org_id))
            await process_response(response)
        case "org_settings":
            response = mistapi.api.v1.orgs.setting.getOrgSettings(
                apisession, org_id=str(org_id)
            )
            await process_response(response)
        case "org_alarmtemplates":
            if object_id:
                response = mistapi.api.v1.orgs.alarmtemplates.getOrgAlarmTemplate(
                    apisession, org_id=str(org_id), alarmtemplate_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.orgs.alarmtemplates.listOrgAlarmTemplates(
                    apisession, org_id=str(org_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.alarmtemplates.listOrgAlarmTemplates(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = [
                    {"name": item.get("name"), "id": item.get("id")}
                    for item in response.data
                    if item.get("name")
                ]
                response.data = data
        case "org_wlans":
            if object_id:
                response = mistapi.api.v1.orgs.wlans.getOrgWLAN(
                    apisession, org_id=str(org_id), wlan_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.orgs.wlans.listOrgWlans(
                    apisession, org_id=str(org_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "ssid")
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.wlans.listOrgWlans(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = [
                    {"ssid": item.get("ssid"), "id": item.get("id")}
                    for item in response.data
                    if item.get("ssid")
                ]
                response.data = data
        case "org_sitegroups":
            if object_id:
                response = mistapi.api.v1.orgs.sitegroups.getOrgSiteGroup(
                    apisession, org_id=str(org_id), sitegroup_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.orgs.sitegroups.listOrgSiteGroups(
                    apisession, org_id=str(org_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.sitegroups.listOrgSiteGroups(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
        case "org_avprofiles":
            if object_id:
                response = mistapi.api.v1.orgs.avprofiles.getOrgAntivirusProfile(
                    apisession, org_id=str(org_id), avprofile_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.orgs.avprofiles.listOrgAntivirusProfiles(
                    apisession, org_id=str(org_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.avprofiles.listOrgAntivirusProfiles(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = [
                    {"name": item.get("name"), "id": item.get("id")}
                    for item in response.data
                    if item.get("name")
                ]
                response.data = data
        case "org_deviceprofiles":
            if object_id:
                response = mistapi.api.v1.orgs.deviceprofiles.getOrgDeviceProfile(
                    apisession, org_id=str(org_id), deviceprofile_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.orgs.deviceprofiles.listOrgDeviceProfiles(
                    apisession, org_id=str(org_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.deviceprofiles.listOrgDeviceProfiles(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = [
                    {"name": item.get("name"), "id": item.get("id")}
                    for item in response.data
                    if item.get("name")
                ]
                response.data = data
        case "org_evpn_topologies":
            if object_id:
                response = mistapi.api.v1.orgs.evpn_topologies.getOrgEvpnTopology(
                    apisession, org_id=str(org_id), evpn_topology_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.orgs.evpn_topologies.listOrgEvpnTopologies(
                    apisession, org_id=str(org_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.evpn_topologies.listOrgEvpnTopologies(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = [
                    {"name": item.get("name"), "id": item.get("id")}
                    for item in response.data
                    if item.get("name")
                ]
                response.data = data
        case "org_gatewaytemplates":
            if object_id:
                response = mistapi.api.v1.orgs.gatewaytemplates.getOrgGatewayTemplate(
                    apisession, org_id=str(org_id), gatewaytemplate_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.orgs.gatewaytemplates.listOrgGatewayTemplates(
                    apisession, org_id=str(org_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.gatewaytemplates.listOrgGatewayTemplates(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = [
                    {"name": item.get("name"), "id": item.get("id")}
                    for item in response.data
                    if item.get("name")
                ]
                response.data = data
        case "org_idpprofiles":
            if object_id:
                response = mistapi.api.v1.orgs.idpprofiles.getOrgIdpProfile(
                    apisession, org_id=str(org_id), idpprofile_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.orgs.idpprofiles.listOrgIdpProfiles(
                    apisession, org_id=str(org_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.idpprofiles.listOrgIdpProfiles(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = [
                    {"name": item.get("name"), "id": item.get("id")}
                    for item in response.data
                    if item.get("name")
                ]
                response.data = data
        case "org_aamwprofiles":
            if object_id:
                response = mistapi.api.v1.orgs.aamwprofiles.getOrgAAMWProfile(
                    apisession, org_id=str(org_id), aamwprofile_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.orgs.aamwprofiles.listOrgAAMWProfiles(
                    apisession, org_id=str(org_id)
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.aamwprofiles.listOrgAAMWProfiles(
                    apisession, org_id=str(org_id)
                )
                await process_response(response)
                data = [
                    {"name": item.get("name"), "id": item.get("id")}
                    for item in response.data
                    if item.get("name")
                ]
                response.data = data
        case "org_mxclusters":
            if object_id:
                response = mistapi.api.v1.orgs.mxclusters.getOrgMxEdgeCluster(
                    apisession, org_id=str(org_id), mxcluster_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.orgs.mxclusters.listOrgMxEdgeClusters(
                    apisession, org_id=str(org_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.mxclusters.listOrgMxEdgeClusters(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = [
                    {"name": item.get("name"), "id": item.get("id")}
                    for item in response.data
                    if item.get("name")
                ]
                response.data = data
        case "org_mxedges":
            if object_id:
                response = mistapi.api.v1.orgs.mxedges.getOrgMxEdge(
                    apisession, org_id=str(org_id), mxedge_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.orgs.mxedges.listOrgMxEdges(
                    apisession, org_id=str(org_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.mxedges.listOrgMxEdges(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = [
                    {"name": item.get("name"), "id": item.get("id")}
                    for item in response.data
                    if item.get("name")
                ]
                response.data = data
        case "org_mxtunnels":
            if object_id:
                response = mistapi.api.v1.orgs.mxtunnels.getOrgMxTunnel(
                    apisession, org_id=str(org_id), mxtunnel_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.orgs.mxtunnels.listOrgMxTunnels(
                    apisession, org_id=str(org_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.mxtunnels.listOrgMxTunnels(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = [
                    {"name": item.get("name"), "id": item.get("id")}
                    for item in response.data
                    if item.get("name")
                ]
                response.data = data
        case "org_nactags":
            if object_id:
                response = mistapi.api.v1.orgs.nactags.getOrgNacTag(
                    apisession, org_id=str(org_id), nactag_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.orgs.nactags.listOrgNacTags(
                    apisession, org_id=str(org_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.nactags.listOrgNacTags(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
        case "org_nacrules":
            if object_id:
                response = mistapi.api.v1.orgs.nacrules.getOrgNacRule(
                    apisession, org_id=str(org_id), nacrule_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.orgs.nacrules.listOrgNacRules(
                    apisession, org_id=str(org_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.nacrules.listOrgNacRules(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
        case "org_networktemplates":
            if object_id:
                response = mistapi.api.v1.orgs.networktemplates.getOrgNetworkTemplate(
                    apisession, org_id=str(org_id), networktemplate_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.orgs.networktemplates.listOrgNetworkTemplates(
                    apisession, org_id=str(org_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.networktemplates.listOrgNetworkTemplates(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = [
                    {"name": item.get("name"), "id": item.get("id")}
                    for item in response.data
                    if item.get("name")
                ]
                response.data = data
        case "org_networks":
            if object_id:
                response = mistapi.api.v1.orgs.networks.getOrgNetwork(
                    apisession, org_id=str(org_id), network_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.orgs.networks.listOrgNetworks(
                    apisession, org_id=str(org_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.networks.listOrgNetworks(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
        case "org_psks":
            if object_id:
                response = mistapi.api.v1.orgs.psks.getOrgPsk(
                    apisession, org_id=str(org_id), psk_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.orgs.psks.listOrgPsks(
                    apisession, org_id=str(org_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.psks.listOrgPsks(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
        case "org_rftemplates":
            if object_id:
                response = mistapi.api.v1.orgs.rftemplates.getOrgRfTemplate(
                    apisession, org_id=str(org_id), rftemplate_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.orgs.rftemplates.listOrgRfTemplates(
                    apisession, org_id=str(org_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.rftemplates.listOrgRfTemplates(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = [
                    {"name": item.get("name"), "id": item.get("id")}
                    for item in response.data
                    if item.get("name")
                ]
                response.data = data
        case "org_services":
            if object_id:
                response = mistapi.api.v1.orgs.services.getOrgService(
                    apisession, org_id=str(org_id), service_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.orgs.services.listOrgServices(
                    apisession, org_id=str(org_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.services.listOrgServices(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = [
                    {"name": item.get("name"), "id": item.get("id")}
                    for item in response.data
                    if item.get("name")
                ]
                response.data = data
        case "org_servicepolicies":
            if object_id:
                response = mistapi.api.v1.orgs.servicepolicies.getOrgServicePolicy(
                    apisession, org_id=str(org_id), servicepolicy_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.orgs.servicepolicies.listOrgServicePolicies(
                    apisession, org_id=str(org_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.servicepolicies.listOrgServicePolicies(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = [
                    {"name": item.get("name"), "id": item.get("id")}
                    for item in response.data
                    if item.get("name")
                ]
                response.data = data
        case "org_sites":
            if object_id:
                site_id = object_id
            if site_id:
                if computed:
                    response = mistapi.api.v1.sites.setting.getSiteSettingDerived(
                        apisession, site_id=str(site_id)
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.sites.setting.getSiteSetting(
                        apisession, site_id=str(site_id)
                    )
                    await process_response(response)
            elif name:
                response = mistapi.api.v1.orgs.sites.searchOrgSites(
                    apisession, org_id=str(org_id), limit=limit, name=name
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.sites.listOrgSites(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = [
                    {"name": item.get("name"), "id": item.get("id")}
                    for item in response.data
                    if item.get("name")
                ]
                response.data = data
        case "org_sitetemplates":
            if object_id:
                response = mistapi.api.v1.orgs.sitetemplates.getOrgSiteTemplate(
                    apisession, org_id=str(org_id), sitetemplate_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.orgs.sitetemplates.listOrgSiteTemplates(
                    apisession, org_id=str(org_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.sitetemplates.listOrgSiteTemplates(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = [
                    {"name": item.get("name"), "id": item.get("id")}
                    for item in response.data
                    if item.get("name")
                ]
                response.data = data
        case "org_vpns":
            if object_id:
                response = mistapi.api.v1.orgs.vpns.getOrgVpn(
                    apisession, org_id=str(org_id), vpn_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.orgs.vpns.listOrgVpns(
                    apisession, org_id=str(org_id)
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.vpns.listOrgVpns(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
        case "org_webhooks":
            if object_id:
                response = mistapi.api.v1.orgs.webhooks.getOrgWebhook(
                    apisession, org_id=str(org_id), webhook_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.orgs.webhooks.listOrgWebhooks(
                    apisession, org_id=str(org_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.webhooks.listOrgWebhooks(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = [
                    {"name": item.get("name"), "id": item.get("id")}
                    for item in response.data
                    if item.get("name")
                ]
                response.data = data
        case "org_wlantemplates":
            if object_id:
                response = mistapi.api.v1.orgs.templates.getOrgTemplate(
                    apisession, org_id=str(org_id), template_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.orgs.templates.listOrgTemplates(
                    apisession, org_id=str(org_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.templates.listOrgTemplates(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
                data = [
                    {"name": item.get("name"), "id": item.get("id")}
                    for item in response.data
                    if item.get("name")
                ]
                response.data = data
        case "org_wxrules":
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
        case "org_wxtags":
            if object_id:
                response = mistapi.api.v1.orgs.wxtags.getOrgWxTag(
                    apisession, org_id=str(org_id), wxtag_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.orgs.wxtags.listOrgWxTags(
                    apisession, org_id=str(org_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.wxtags.listOrgWxTags(
                    apisession, org_id=str(org_id), limit=limit
                )
                await process_response(response)
        case "org_guest_authorizations":
            if guest_mac:
                response = mistapi.api.v1.orgs.guests.getOrgGuestAuthorization(
                    apisession, org_id=str(org_id), guest_mac=str(guest_mac)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.orgs.guests.listOrgGuestAuthorizations(
                    apisession, org_id=str(org_id)
                )
                await process_response(response)
        case _:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": f"Invalid object_type: {object_type}. Valid values are: {[e.value for e in Object_type]}",
                }
            )
    return response


async def _site_configuration_objects_getter(
    apisession: mistapi.APISession,
    object_type: str,
    org_id: str,
    site_id: str,
    object_id: str | None,
    name: str | None,
    guest_mac: str | None,
    computed: bool,
    limit: int = 20,
) -> _APIResponse:
    match object_type:
        case "site_info":
            response = mistapi.api.v1.sites.sites.getSiteInfo(
                apisession, site_id=str(site_id)
            )
            await process_response(response)
        case "site_settings":
            response = mistapi.api.v1.sites.setting.getSiteSetting(
                apisession, site_id=str(site_id)
            )
            await process_response(response)
        case "site_devices":
            return await _get_site_devices(
                apisession, org_id, site_id, object_id, name, computed, limit
            )
        case "site_evpn_topologies":
            if object_id:
                response = mistapi.api.v1.sites.evpn_topologies.getSiteEvpnTopology(
                    apisession, site_id=str(site_id), evpn_topology_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.sites.evpn_topologies.listSiteEvpnTopologies(
                    apisession, site_id=str(site_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.sites.evpn_topologies.listSiteEvpnTopologies(
                    apisession, site_id=str(site_id), limit=limit
                )
                await process_response(response)
                data = [
                    {"name": item.get("name"), "id": item.get("id")}
                    for item in response.data
                    if item.get("name")
                ]
                response.data = data
        case "site_maps":
            if object_id:
                response = mistapi.api.v1.sites.maps.getSiteMap(
                    apisession, site_id=str(site_id), map_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.sites.maps.listSiteMaps(
                    apisession, site_id=str(site_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.sites.maps.listSiteMaps(
                    apisession, site_id=str(site_id), limit=limit
                )
                await process_response(response)
                data = [
                    {"name": item.get("name"), "id": item.get("id")}
                    for item in response.data
                    if item.get("name")
                ]
                response.data = data
        case "site_mxedges":
            if object_id:
                response = mistapi.api.v1.sites.mxedges.getSiteMxEdge(
                    apisession, site_id=str(site_id), mxedge_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.sites.mxedges.listSiteMxEdges(
                    apisession, site_id=str(site_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.sites.mxedges.listSiteMxEdges(
                    apisession, site_id=str(site_id), limit=limit
                )
                await process_response(response)
                data = [
                    {"name": item.get("name"), "id": item.get("id")}
                    for item in response.data
                    if item.get("name")
                ]
                response.data = data
        case "site_psks":
            if object_id:
                response = mistapi.api.v1.sites.psks.getSitePsk(
                    apisession, site_id=str(site_id), psk_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.sites.psks.listSitePsks(
                    apisession, site_id=str(site_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.sites.psks.listSitePsks(
                    apisession, site_id=str(site_id), limit=limit
                )
                await process_response(response)
        case "site_webhooks":
            if object_id:
                response = mistapi.api.v1.sites.webhooks.getSiteWebhook(
                    apisession, site_id=str(site_id), webhook_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.sites.webhooks.listSiteWebhooks(
                    apisession, site_id=str(site_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.sites.webhooks.listSiteWebhooks(
                    apisession, site_id=str(site_id), limit=limit
                )
                await process_response(response)
                data = [
                    {"name": item.get("name"), "id": item.get("id")}
                    for item in response.data
                    if item.get("name")
                ]
                response.data = data
        case "site_wlans":
            return await _get_site_wlans(
                apisession, org_id, site_id, object_id, name, computed, limit
            )
        case "site_wxrules":
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
        case "site_wxtags":
            if object_id:
                response = mistapi.api.v1.sites.wxtags.getSiteWxTag(
                    apisession, site_id=str(site_id), wxtag_id=str(object_id)
                )
                await process_response(response)
            elif name:
                response = mistapi.api.v1.sites.wxtags.listSiteWxTags(
                    apisession, site_id=str(site_id), limit=1000
                )
                data_in = mistapi.get_all(apisession, response)
                response = _search_object(data_in, name, "name", limit=limit)
                await process_response(response)
            else:
                response = mistapi.api.v1.sites.wxtags.listSiteWxTags(
                    apisession, site_id=str(site_id), limit=limit
                )
                await process_response(response)
        case "site_guest_authorizations":
            if guest_mac:
                response = mistapi.api.v1.sites.guests.getSiteGuestAuthorization(
                    apisession, site_id=str(site_id), guest_mac=str(guest_mac)
                )
                await process_response(response)
            else:
                response = mistapi.api.v1.sites.guests.listSiteAllGuestAuthorizations(
                    apisession, site_id=str(site_id)
                )
                await process_response(response)
        case _:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": f"Invalid object_type: {object_type}. Valid values are: {[e.value for e in Object_type]}",
                }
            )
    return response


async def _get_site_devices(
    apisession: mistapi.APISession,
    org_id: str,
    site_id: str,
    object_id: str,
    name: str,
    computed: bool,
    limit: int = 20,
) -> _APIResponse:
    if object_id:
        if computed:
            response = await _get_computed_device_configuration(
                apisession=apisession,
                org_id=str(org_id),
                site_id=str(site_id),
                device_id=str(object_id),
                device_data=None,
            )
            return response
        else:
            response = mistapi.api.v1.sites.devices.getSiteDevice(
                apisession, site_id=str(site_id), device_id=str(object_id)
            )
            await process_response(response)
            return response
    elif name:
        response = mistapi.api.v1.sites.devices.searchSiteDevices(
            apisession, site_id=str(site_id), hostname=name, limit=1000, type="all"
        )
        await process_response(response)
        if (
            isinstance(response.data, dict)
            and len(response.data.get("results", [])) == 1
            and computed
        ):
            response.data = response.data["results"][0]
            response = await _get_computed_device_configuration(
                apisession=apisession,
                org_id=str(org_id),
                site_id=str(site_id),
                device_data=response,
            )
        return response
    else:
        response = mistapi.api.v1.sites.devices.listSiteDevices(
            apisession, site_id=str(site_id), limit=limit, type="all"
        )
        await process_response(response)
        return response


async def _get_computed_device_configuration(
    apisession: mistapi.APISession,
    org_id: str,
    site_id: str,
    device_id: str | None,
    device_data: _APIResponse | None,
) -> _APIResponse:
    logger.debug("func _get_device_configuration called")
    if device_id:
        device_data = mistapi.api.v1.sites.devices.getSiteDevice(
            apisession, site_id=str(site_id), device_id=str(device_id)
        )
        await process_response(device_data)
    elif not device_data:
        raise ToolError(
            {
                "status_code": 400,
                "message": "Either device_id or device_data must be provided",
            }
        )
    data = {}
    if isinstance(device_data.data, dict):
        match device_data.data.get("type"):
            case "switch":
                switch_name = device_data.data.get("name", "")
                switch_model = device_data.data.get("model", "")
                switch_role = device_data.data.get("role", "")
                switch_data = {}
                site_config = mistapi.api.v1.sites.setting.getSiteSettingDerived(
                    apisession, site_id=str(site_id)
                )
                await process_response(site_config)
                if isinstance(site_config.data, dict):
                    switch_data = _process_switch_template(
                        site_config.data,
                        switch_name,
                        switch_model,
                        switch_role,
                        switch_data,
                    )
                for key, value in device_data.data.items():
                    if key == "port_config":
                        port_config = _process_switch_interface(value)
                        switch_data[key] = {**data.get(key, {}), **port_config}
                    elif isinstance(value, dict) and isinstance(
                        switch_data.get(key, {}), dict
                    ):
                        switch_data[key] = {
                            **switch_data.get(key, {}), **value}
                    elif isinstance(value, list) and isinstance(
                        switch_data.get(key, []), list
                    ):
                        switch_data[key] = switch_data.get(key, []) + value
                    else:
                        switch_data[key] = value
                device_data.data = switch_data
            case "gateway":
                gateway_data = {}
                site_data = mistapi.api.v1.sites.sites.getSiteInfo(
                    apisession, site_id=str(site_id)
                )
                await process_response(site_data)
                if isinstance(site_data.data, dict):
                    gateway_template_id = site_data.data.get(
                        "gatewaytemplate_id")
                    if gateway_template_id:
                        response = (
                            mistapi.api.v1.orgs.gatewaytemplates.getOrgGatewayTemplate(
                                apisession,
                                org_id=str(org_id),
                                gatewaytemplate_id=str(gateway_template_id),
                            )
                        )
                        await process_response(response)
                        gateway_data = response.data
                if isinstance(gateway_data, dict):
                    for key, value in device_data.data.items():
                        if key in NETWORK_TEMPLATE_FIELDS:
                            if isinstance(value, dict) and isinstance(
                                gateway_data.get(key, {}), dict
                            ):
                                gateway_data[key] = {
                                    **gateway_data.get(key, {}),
                                    **value,
                                }
                            elif isinstance(value, list) and isinstance(
                                gateway_data.get(key, []), list
                            ):
                                gateway_data[key] = gateway_data.get(
                                    key, []) + value
                            else:
                                gateway_data[key] = value
                device_data.data = gateway_data
    return device_data


def _process_switch_template(
    template: dict, switch_name: str, switch_model: str, switch_role: str, data: dict
) -> dict:
    for key, value in template.items():
        if key in NETWORK_TEMPLATE_FIELDS:
            if key == "name":
                continue
            elif key == "switch_matching" and value.get("enable"):
                data = _process_switch_rule(
                    value.get(
                        "rules", []), switch_name, switch_model, switch_role, data
                )
            elif isinstance(value, dict) and isinstance(data.get(key, {}), dict):
                data[key] = {**data.get(key, {}), **value}
            elif isinstance(value, list) and isinstance(data.get(key, []), list):
                data[key] = data.get(key, []) + value
            else:
                data[key] = value
    return data


def _process_switch_rule(
    rules: list, switch_name: str, switch_model: str, switch_role: str, data: dict
) -> dict:
    for rule in rules:
        rule_cleansed = rule.copy()
        del rule_cleansed["name"]
        match_name_true = False
        match_name_enabled = False
        match_model_true = False
        match_model_enabled = False
        match_role_true = False
        match_role_enabled = False
        for k, v in rule.items():
            if k.startswith("match_name"):
                match_name_enabled = True
                del rule_cleansed[k]
                match_name_true = _process_switch_rule_match(switch_name, k, v)
            elif k.startswith("match_model"):
                match_model_enabled = True
                del rule_cleansed[k]
                match_model_true = _process_switch_rule_match(
                    switch_model, k, v)
            elif k == "match_role":
                match_role_enabled = True
                match_role_true = _process_switch_rule_match(switch_role, k, v)
        if (
            (not match_name_enabled or match_name_true)
            and (not match_model_enabled or match_model_true)
            and (not match_role_enabled or match_role_true)
        ):
            for key, value in rule_cleansed.items():
                if key == "port_config":
                    port_config = _process_switch_interface(value)
                    data[key] = {**data.get(key, {}), **port_config}
                elif isinstance(value, dict) and isinstance(data.get(key, {}), dict):
                    data[key] = {**data.get(key, {}), **value}
                elif isinstance(value, list) and isinstance(data.get(key, []), list):
                    data[key] = data.get(key, []) + value
                else:
                    data[key] = value
            return data
    return data


def _process_switch_rule_match(
    switch_value: str, match_key: str, match_value: str
) -> bool:
    if ":" in match_key:
        match_start, match_stop = match_key.replace(
            "]", "").split("[")[1].split(":")
        try:
            if (
                len(switch_value) > int(match_stop)
                and switch_value[int(match_start): int(match_stop)].lower()
                == match_value.lower()
            ):
                return True
        except Exception:
            return False
    elif switch_value.lower() == match_value.lower():
        return True
    return False


def _process_switch_interface(port_config: dict) -> dict:
    port_config_tmp = {}
    for key, value in port_config.items():
        if "," in key:
            keys = [k.strip() for k in key.split(",")]
            for k in keys:
                port_config_tmp[k] = value
        else:
            port_config_tmp[key] = value
    port_config_cleansed = {}
    for key, value in port_config_tmp.items():
        if key.count("-") > 1:
            prefix, interfaces = key.split("-", 1)
            fpc, pic, port = interfaces.split("/")
            if "-" in fpc:
                fpc_start, fpc_end = fpc.split("-")
                for fpc_num in range(int(fpc_start), int(fpc_end) + 1):
                    port_config_cleansed[f"{prefix}-{fpc_num}/{pic}/{port}"] = value
            elif "-" in pic:
                pic_start, pic_end = pic.split("-")
                for pic_num in range(int(pic_start), int(pic_end) + 1):
                    port_config_cleansed[f"{prefix}-{fpc}/{pic_num}/{port}"] = value
            elif "-" in port:
                port_start, port_end = port.split("-")
                for port_num in range(int(port_start), int(port_end) + 1):
                    port_config_cleansed[f"{prefix}-{fpc}/{pic}/{port_num}"] = value
        else:
            port_config_cleansed[key] = value
    return port_config_cleansed


async def _get_site_wlans(
    apisession: mistapi.APISession,
    org_id: str,
    site_id: str,
    object_id: str,
    name: str,
    computed: bool,
    limit: int = 20,
) -> _APIResponse:
    if object_id:
        response = mistapi.api.v1.sites.wlans.getSiteWlan(
            apisession, site_id=str(site_id), wlan_id=str(object_id)
        )
        await process_response(response)
    elif computed:
        fetch_limit = 1000 if name else limit
        site_data = mistapi.api.v1.sites.sites.getSiteInfo(
            apisession, site_id=str(site_id)
        )
        await process_response(site_data)
        if isinstance(site_data.data, dict):
            sitegroup_ids = site_data.data.get("sitegroup_ids", [])
        else:
            sitegroup_ids = []
        assigned_template_ids = []
        assigned_wlans = []
        org_wlan_templates = mistapi.api.v1.orgs.templates.listOrgTemplates(
            apisession, org_id=str(org_id), limit=fetch_limit
        )
        await process_response(org_wlan_templates)
        for template in org_wlan_templates.data:
            applies = template.get("applies", {})
            template_org_id = applies.get("org_id", "")
            template_site_ids = applies.get("site_ids", []) or []
            template_sitegroup_ids = applies.get("sitegroup_ids", []) or []
            if (
                str(site_id) in template_site_ids
                or set(template_sitegroup_ids) & set(sitegroup_ids)
                or template_org_id == str(org_id)
            ):
                assigned_template_ids.append(template.get("id"))
        org_wlans = mistapi.api.v1.orgs.wlans.listOrgWlans(
            apisession, org_id=str(org_id), limit=fetch_limit
        )
        await process_response(org_wlans)
        for wlan in org_wlans.data:
            if wlan.get("template_id") in assigned_template_ids:
                assigned_wlans.append(wlan)
        site_wlans = mistapi.api.v1.sites.wlans.listSiteWlans(
            apisession, site_id=str(site_id), limit=fetch_limit
        )
        await process_response(site_wlans)
        for wlan in site_wlans.data:
            assigned_wlans.append(wlan)
        if name:
            response = _search_object(
                assigned_wlans, name, "ssid", limit=limit)
            await process_response(response)
        else:
            site_wlans.data = assigned_wlans
            response = site_wlans
    elif name:
        response = mistapi.api.v1.sites.wlans.listSiteWlans(
            apisession, site_id=str(site_id), limit=1000
        )
        data_in = mistapi.get_all(apisession, response)
        response = _search_object(data_in, name, "ssid", limit=limit)
        await process_response(response)
    else:
        response = mistapi.api.v1.sites.wlans.listSiteWlans(
            apisession, site_id=str(site_id), limit=limit
        )
        await process_response(response)
        data = [
            {"ssid": item.get("ssid"), "id": item.get("id")}
            for item in response.data
            if item.get("ssid")
        ]
        response.data = data
    return response


def _search_object(
    data_in: list, name: str, attribute: str = "name", limit: int = 20
) -> _APIResponse:
    data_out = []
    for entry in data_in:
        if name.startswith("*") and name.endswith("*"):
            if name[1:-1].lower() in entry.get(attribute, "").lower():
                data_out.append(entry)
        elif name.startswith("*"):
            if entry.get(attribute, "").lower().endswith(name[1:].lower()):
                data_out.append(entry)
        elif name.endswith("*"):
            if entry.get(attribute, "").lower().startswith(name[:-1].lower()):
                data_out.append(entry)
        elif name.lower() in entry.get(attribute, "").lower():
            data_out.append(entry)
    response = _APIResponse(url="", response=None)
    response.data = data_out[:limit]
    response.status_code = 200
    response.headers = CaseInsensitiveDict(
        {"X-Page-Total": str(len(data_out)), "X-Page-Limit": str(limit)}
    )
    return response


class Query_type(Enum):
    HISTORY = "history"
    LAST_CONFIGS = "last_configs"


class Device_type(Enum):
    AP = "ap"
    SWITCH = "switch"
    GATEWAY = "gateway"


async def search_device_config_history(
    site_id: Annotated[UUID, Field(description="Site ID")],
    query_type: Annotated[
        Query_type,
        Field(
            description="Whether to search for config history entries or just retrieve the last config entry for each device"
        ),
    ],
    device_type: Annotated[
        Device_type, Field(
            description="Type of device to search config history for")
    ],
    device_mac: Annotated[
        str,
        Field(
            description="MAC address of the device to search config history for",
            default=None,
        ),
    ],
    start: Annotated[
        int, Field(
            description="Start of time range (epoch seconds)", default=None)
    ],
    end: Annotated[
        int, Field(description="End of time range (epoch seconds)", default=None)
    ],
    limit: Annotated[
        int, Field(description="Max number of results per page", default=20)
    ] = 20,
) -> dict | list | str:
    """Search for entries in device config history.
    This tool can be used to track configuration changes over time, useful for troubleshooting issues that started after a config change."""
    logger.debug("Tool search_device_config_history called")
    logger.debug(
        "Input Parameters: site_id: %s, query_type: %s, device_type: %s, device_mac: %s, start: %s, end: %s, limit: %s",
        site_id,
        query_type,
        device_type,
        device_mac,
        start,
        end,
        limit,
    )
    apisession, response_format = await get_apisession()
    try:
        object_type = query_type
        match object_type.value:
            case "history":
                response = mistapi.api.v1.sites.devices.searchSiteDeviceConfigHistory(
                    apisession,
                    site_id=str(site_id),
                    type=device_type.value if device_type else None,
                    mac=str(device_mac) if device_mac else None,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    limit=limit,
                )
                await process_response(response)
            case "last_configs":
                response = mistapi.api.v1.sites.devices.searchSiteDeviceLastConfigs(
                    apisession,
                    site_id=str(site_id),
                    device_type=device_type.value if device_type else None,
                    mac=str(device_mac) if device_mac else None,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    limit=limit,
                )
                await process_response(response)
            case _:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Query_type]}",
                    }
                )
    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)
    return format_response(response, response_format)


ConfigurationObjectType = Object_type
HistoryDeviceType = Device_type
HistoryQueryType = Query_type

_GET_CONFIGURATION_OBJECTS = internal_tool(get_configuration_objects)
_SEARCH_DEVICE_CONFIG_HISTORY = internal_tool(search_device_config_history)


_CONFIGURATION_OBJECT_VALUES = ", ".join(
    item.value for item in ConfigurationObjectType)
_CONFIGURATION_OBJECT_GUIDANCE = "\n".join(
    f"* `{name}`: {description}"
    for name, description in _CONFIGURATION_OBJECT_DESCRIPTIONS.items()
)


@mcp.tool(
    name="mist_get_configuration",
    description=f"""Read Mist configuration or inspect device configuration history.

For `operation=objects`, provide `org_id` and `object_type`. Object types beginning
with `site_` also require `site_id`. Use `object_id` for one exact object or `name`
for a case-insensitive wildcard search (`prefix*` or `*substring*`). Name filtering
does not support pagination and is unavailable for info/settings, site devices, and
guest authorizations. `object_id` is also unavailable for guest authorizations. Use
`guest_mac` for those records. `site_id` may select one site with `org_sites`. Set
`computed=true` to include inherited configuration where supported.

Supported configuration objects:
{_CONFIGURATION_OBJECT_GUIDANCE}

For list operations, `limit` defaults to 20 and has a maximum of 1000; paginated
responses may return `next`.

For `operation=device_history`, provide `site_id`, `query_type`, and `device_type`.
Use `history` for change entries or `last_configs` for the latest configuration per
device, optionally filtered by `device_mac`, `start`, and `end`.

The `object_type`, `query_type`, and `device_type` input schemas contain the complete
lists of supported values.""",
    tags={"configuration"},
    annotations={
        "title": "Get configuration",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def get_configuration(
    operation: Annotated[
        ConfigurationOperation, Field(
            description="Configuration query to run.")
    ],
    org_id: Annotated[
        UUID,
        Field(description="Organization ID for object queries.", default=None),
    ],
    site_id: Annotated[
        UUID, Field(
            description="Site ID when required by the query.", default=None)
    ],
    object_type: Annotated[
        ConfigurationObjectType,
        Field(
            description=f"Configuration object type. Supported values: {_CONFIGURATION_OBJECT_VALUES}.",
            default=None,
        ),
    ],
    object_id: Annotated[
        UUID, Field(
            description="Specific configuration object ID.", default=None)
    ],
    name: Annotated[
        str,
        Field(
            description="Case-insensitive name filter. Supports prefix* and *substring* wildcards; suffix-only wildcards are unsupported.",
            default=None,
        ),
    ],
    guest_mac: Annotated[
        str,
        Field(
            description="Guest MAC for org_guest_authorizations or site_guest_authorizations.",
            default=None,
        ),
    ],
    query_type: Annotated[
        HistoryQueryType,
        Field(description="History query: history or last_configs.", default=None),
    ],
    device_type: Annotated[
        HistoryDeviceType,
        Field(description="History device type: ap, switch, or gateway.", default=None),
    ],
    device_mac: Annotated[
        str, Field(description="Device MAC for history queries.", default=None)
    ],
    start: Annotated[
        int, Field(description="History start time.", default=None)
    ],
    end: Annotated[int, Field(description="History end time.", default=None)],
    computed: Annotated[
        bool,
        Field(
            description="Include inherited settings where supported: a single org_sites or site_devices result, or site_wlans.",
            default=None,
        ),
    ],
    limit: Annotated[
        int, Field(description="Maximum results per page.", default=20)
    ] = 20,
) -> ToolResult:
    if operation is ConfigurationOperation.OBJECTS:
        if org_id is None or object_type is None:
            raise ToolError(
                "org_id and object_type are required for operation='objects'. "
                f"Supported object_type values: {_CONFIGURATION_OBJECT_VALUES}."
            )
        return await run_internal_tool(
            _GET_CONFIGURATION_OBJECTS,
            arguments(
                {
                    "org_id": org_id,
                    "site_id": site_id,
                    "object_type": object_type,
                    "object_id": object_id,
                    "name": name,
                    "guest_mac": guest_mac,
                    "computed": computed,
                    "limit": limit,
                }
            ),
        )
    if site_id is None or query_type is None or device_type is None:
        raise ToolError(
            "site_id, query_type, and device_type are required for operation='device_history'."
        )
    return await run_internal_tool(
        _SEARCH_DEVICE_CONFIG_HISTORY,
        arguments(
            {
                "site_id": site_id,
                "query_type": query_type,
                "device_type": device_type,
                "device_mac": device_mac,
                "start": start,
                "end": end,
                "limit": limit,
            }
        ),
    )
