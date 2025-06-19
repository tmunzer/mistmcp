""" "
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

from enum import Enum


class McpToolsCategory(Enum):
    CONSTANTS_EVENTS = "constants_events"
    CONSTANTS_DEFINITIONS = "constants_definitions"
    CONSTANTS_MODELS = "constants_models"
    ORGS = "orgs"
    ORGS_WAN = "orgs_wan"
    ORGS_ALARMS = "orgs_alarms"
    ORGS_ALARM_TEMPLATES = "orgs_alarm_templates"
    DEVICES_CONFIG = "devices_config"
    ORGS_LICENSES = "orgs_licenses"
    ORGS_CLIENTS = "orgs_clients"
    ORGS_DEVICES = "orgs_devices"
    UTILITIES_UPGRADE = "utilities_upgrade"
    ORGS_EVENTS = "orgs_events"
    ORGS_LAN = "orgs_lan"
    ORGS_SLES = "orgs_sles"
    ORGS_INVENTORY = "orgs_inventory"
    ORGS_LOGS = "orgs_logs"
    ORGS_MXEDGES = "orgs_mxedges"
    ORGS_NAC = "orgs_nac"
    ORGS_DEVICES___OTHERS = "orgs_devices___others"
    ORGS_WLANS = "orgs_wlans"
    ORGS_SITEGROUPS = "orgs_sitegroups"
    ORGS_SITES = "orgs_sites"
    ORGS_STATS = "orgs_stats"
    ORGS_MARVIS = "orgs_marvis"
    ORGS_WEBHOOKS = "orgs_webhooks"
    SELF_ACCOUNT = "self_account"
    SITES = "sites"
    SITES_WAN = "sites_wan"
    SITES_CLIENTS = "sites_clients"
    SITES_DEVICES = "sites_devices"
    SITES_SYNTHETIC_TESTS = "sites_synthetic_tests"
    SITES_EVENTS = "sites_events"
    SITES_LAN = "sites_lan"
    SITES_INSIGHTS = "sites_insights"
    SITES_ROGUES = "sites_rogues"
    SITES_MAPS = "sites_maps"
    SITES_MXEDGES = "sites_mxedges"
    SITES_WLANS = "sites_wlans"
    SITES_RFDIAGS = "sites_rfdiags"
    SITES_RRM = "sites_rrm"
    SITES_SLES = "sites_sles"
    SITES_STATS = "sites_stats"
    SITES_WAN_USAGES = "sites_wan_usages"
    SITES_WEBHOOKS = "sites_webhooks"


TOOLS = {
    "constants_definitions": {
        "description": "tools to retrieve constant values that can be used in different parts of the configuration",
        "tools": [
            "listApChannels",
            "listApLedDefinition",
            "listFingerprintTypes",
            "listInsightMetrics",
            "listLicenseTypes",
            "listWebhookTopics",
        ],
    },
    "constants_events": {
        "description": "tools to retrieve the definitions of the Mist events. These definitions are providing example of the Webhook payloads",
        "tools": [
            "listAlarmDefinitions",
            "listClientEventsDefinitions",
            "listDeviceEventsDefinitions",
            "listMxEdgeEventsDefinitions",
            "listNacEventsDefinitions",
            "listOtherDeviceEventsDefinitions",
            "listSystemEventsDefinitions",
        ],
    },
    "constants_models": {
        "description": "tools to retrieve the list of Hardware Models and their features",
        "tools": [
            "listDeviceModels",
            "listMxEdgeModels",
            "listSupportedOtherDeviceModels",
        ],
    },
    "devices_config": {
        "description": "Configuration related to devices. It provides access to various device configurations such as AP templates, device profiles, and more.",
        "tools": [
            "listOrgAptemplates",
            "listOrgDeviceProfiles",
            "listSiteApTemplateDerived",
            "listSiteDeviceProfilesDerived",
        ],
    },
    "orgs": {
        "description": "An organization usually represents a customer - which has inventories, licenses. An Organization can contain multiple sites. A site usually represents a deployment at the same location (a campus, an office).",
        "tools": ["getOrg", "searchOrgEvents", "getOrgSettings"],
    },
    "orgs_alarm_templates": {
        "description": "An Alarm Template is a set of Alarm Rules that could be applied to\none or more sites (while each site can only pick one Alarm Template), or to the\nwhole org.\n\n\nOnce created, the Alarm template must be assigned with the `alarmtemplate_id` attribute to one of the following\n* the whole org with the [Update Org](/#operations/updateOrg) tool\n* one or multiple sites with the [Update Site Info](/#operations/updateSiteInfo) tool",
        "tools": [
            "listOrgAlarmTemplates",
            "listOrgSuppressedAlarms",
            "getOrgAlarmTemplate",
        ],
    },
    "orgs_alarms": {
        "description": "Alarms are triggered based on certain events. Alarms could be configured using an Alarm Template.",
        "tools": ["countOrgAlarms", "searchOrgAlarms"],
    },
    "orgs_clients": {
        "description": "Clients for the organizations. It provides access to various client types such as NAC, WAN, wired, and wireless clients.",
        "tools": [
            "countOrgWirelessClients",
            "searchOrgWirelessClientEvents",
            "searchOrgWirelessClients",
            "countOrgWirelessClientsSessions",
            "searchOrgWirelessClientSessions",
            "listOrgGuestAuthorizations",
            "countOrgGuestAuthorizations",
            "searchOrgGuestAuthorization",
            "getOrgGuestAuthorization",
            "countOrgNacClients",
            "countOrgNacClientEvents",
            "searchOrgNacClientEvents",
            "searchOrgNacClients",
            "countOrgWanClientEvents",
            "countOrgWanClients",
            "searchOrgWanClientEvents",
            "searchOrgWanClients",
            "countOrgWiredClients",
            "searchOrgWiredClients",
        ],
    },
    "orgs_devices": {
        "description": "Devices are any Network device managed or monitored by Juniper Mist. It can be * Wireless Access Points * Juniper Switch (EX, QFX) * Juniper WAN Gateway (SRX, SSR) * Mist Edges * Other or 3rd party devices, like Cradlepoint Devices",
        "tools": [
            "listOrgDevices",
            "countOrgDevices",
            "countOrgDeviceEvents",
            "searchOrgDeviceEvents",
            "countOrgDeviceLastConfigs",
            "searchOrgDeviceLastConfigs",
            "listOrgApsMacs",
            "searchOrgDevices",
            "listOrgDevicesSummary",
            "getOrgJuniperDevicesCommand",
        ],
    },
    "orgs_devices___others": {
        "description": "tool for 3rd party devices",
        "tools": [
            "listOrgOtherDevices",
            "countOrgOtherDeviceEvents",
            "searchOrgOtherDeviceEvents",
            "getOrgOtherDevice",
        ],
    },
    "orgs_events": {
        "description": "Orgs Events are all the system level changes at the org level",
        "tools": ["countOrgSystemEvents", "searchOrgSystemEvents"],
    },
    "orgs_inventory": {
        "description": "The Org Inventory allows administrators to view and manage all devices registered (claimed) to the Organization.",
        "tools": ["getOrgInventory", "countOrgInventory", "searchOrgInventory"],
    },
    "orgs_lan": {
        "description": "Switches Configuration related objects for the organizations. It provides access to LAN related objects such as EVPN topologies and network templates.",
        "tools": ["listOrgEvpnTopologies", "listOrgNetworkTemplates"],
    },
    "orgs_licenses": {
        "description": "Licenses are a type of service or access that customers can purchase for various features or services offered by a company.\n\nSubscriptions can have different statuses, such as active, expired, exceeded, or trial, depending on their validity and usage. The status of a subscription determines whether it is currently active and valid, has expired, has exceeded the allowed usage limit, or is in a trial period.\n\nLicenses can be activated using an activation code, and the activation process confirms the inputted code and activates the subscription.",
        "tools": [
            "GetOrgLicenseAsyncClaimStatus",
            "getOrgLicensesSummary",
            "getOrgLicensesBySite",
        ],
    },
    "orgs_logs": {
        "description": "Audit Logs are records of activities initiated by users, providing a history of actions such as accessing, creating, updating, or deleting resources or components at the Org level.\n\nThese logs allow superusers and network administrators to track and maintain a record of user actions, including who performed specific actions and when.\n\nAudit logs are useful for monitoring user activity, investigating security breaches, ensuring compliance with regulations, and tracing configuration changes in a network.\n\nThey can be filtered and analyzed to view specific information and granular-level details of each event.",
        "tools": ["listOrgAuditLogs", "countOrgAuditLogs"],
    },
    "orgs_marvis": {
        "description": "Marvis is an AI-driven, interactive virtual network assistant that streamlines network operations, simplifies troubleshooting, and provides an enhanced user experience.\nIt offers real-time network visibility, comprehensive insights, and automation customized for your network.\nMarvis can proactively identify issues, interpret their impact, determine root causes, and recommend fixes.\nIt consists of components such as Marvis Actions, Marvis Minis, Conversational Assistant, Marvis Client, and Marvis Query Language.",
        "tools": ["troubleshootOrg"],
    },
    "orgs_mxedges": {
        "description": "MX Edge related objects for the organizations. It provides access to Mist Edges, Mist Clusters, and Mist Tunnels.",
        "tools": [
            "listOrgMxEdgeClusters",
            "listOrgMxEdges",
            "countOrgMxEdges",
            "countOrgSiteMxEdgeEvents",
            "searchOrgMistEdgeEvents",
            "searchOrgMxEdges",
            "getOrgMxEdgeUpgradeInfo",
            "listOrgMxTunnels",
        ],
    },
    "orgs_nac": {
        "description": "NAC related objects for the organizations. It provides access to NAC Endpoints, NAC fingerprints, tags, and rules.",
        "tools": [
            "listOrgNacRules",
            "listOrgNacTags",
            "searchOrgUserMacs",
            "getOrgUserMac",
            "countOrgClientFingerprints",
            "searchOrgClientFingerprints",
        ],
    },
    "orgs_sitegroups": {
        "description": "Site groups are a group of sites under the same Org. It's many-to-many mapping to sites",
        "tools": ["listOrgSiteGroups", "getOrgSiteGroup"],
    },
    "orgs_sites": {
        "description": "tools to Create or Get the Organization Sites.\n\n\nUse the [Site Settings](https://www.juniper.net/documentation/us/en/software/mist/api/http/api/sites/setting/overview) to configure or update the Site information.",
        "tools": ["countOrgSites", "searchOrgSites", "listOrgSiteTemplates"],
    },
    "orgs_sles": {
        "description": "Org SLEs, or Service-Level Expectations, are metrics used to monitor and report on the user experience of a Wireless, Wired or Wan network.\n\nThey are generated through data science and machine learning algorithms and provide insights into various aspects of the network, such as coverage, capacity, connectivity, and performance.\n\nMist SLEs help identify when users do not have sufficient network quality, when they face issues with connecting or roaming between access points, and when there are problems on the wired network.",
        "tools": ["getOrgSitesSle", "getOrgSle"],
    },
    "orgs_stats": {
        "description": "Statistics for the organizations. It provides access to various statistics related to the organization, such as BGP peers, devices, MX edges, other devices, ports, sites, tunnels, and VPN peers.",
        "tools": [
            "getOrgStats",
            "countOrgBgpStats",
            "searchOrgBgpStats",
            "listOrgDevicesStats",
            "listOrgMxEdgesStats",
            "getOrgOtherDeviceStats",
            "countOrgSwOrGwPorts",
            "searchOrgSwOrGwPorts",
            "listOrgSiteStats",
            "countOrgTunnelsStats",
            "searchOrgTunnelsStats",
            "countOrgPeerPathStats",
            "searchOrgPeerPathStats",
        ],
    },
    "orgs_wan": {
        "description": "WAN Configuration related objects for the organizations. It provides access to WAN related objects such as VPNs.",
        "tools": [
            "listOrgAAMWProfiles",
            "listOrgAntivirusProfiles",
            "listOrgGatewayTemplates",
            "listOrgIdpProfiles",
            "listOrgNetworks",
            "listOrgSecPolicies",
            "listOrgServicePolicies",
            "listOrgServices",
            "listOrgVpns",
        ],
    },
    "orgs_webhooks": {
        "description": "An Org Webhook is a configuration that allows real-time events and data from the Org to be pushed to a provided url.\n\nIt enables the collection of information about various topics such as device events, alarms, and audits updates at the org level.\n\nThe Webhook can be set up and customized using the Mist API, allowing users to receive and analyze specific data from a particular site.",
        "tools": [
            "listOrgWebhooks",
            "countOrgWebhooksDeliveries",
            "searchOrgWebhooksDeliveries",
        ],
    },
    "orgs_wlans": {
        "description": "An Org Wlan is a wireless local area network that is configured at the Org level and applied to a WLAN template.\n\nIt allows for the creation and management of wireless network settings, such as SSIDs (service set identifiers), authentication settings, VLAN configurations, etc...\n\nOrg WLANs are created and managed at the org level and can only be referenced and used within the WLAN Templates.",
        "tools": [
            "listOrgPsks",
            "listOrgRfTemplates",
            "listOrgTemplates",
            "listOrgWlans",
            "getOrgWLAN",
            "listOrgWxRules",
            "listOrgWxTags",
            "getOrgApplicationList",
            "getOrgCurrentMatchingClientsOfAWxTag",
        ],
    },
    "self_account": {
        "description": "tools related to the currently connected user account.",
        "tools": [
            "getSelf",
            "getSelfLoginFailures",
            "listSelfAuditLogs",
            "getSelfApiUsage",
        ],
    },
    "sites": {
        "description": "A site represents a project, a deployment. For MSP, it can be as small as a coffee shop or a five-star 600-room hotel. A site contains a set of Maps, Wlans, Policies, Zones.",
        "tools": ["getSiteInfo", "getSiteSetting", "getSiteSettingDerived"],
    },
    "sites_clients": {
        "description": "Clients for the sites. It provides access to various client types such as NAC, WAN, wired, and wireless clients.",
        "tools": [
            "countSiteWirelessClients",
            "countSiteWirelessClientEvents",
            "searchSiteWirelessClientEvents",
            "searchSiteWirelessClients",
            "countSiteWirelessClientSessions",
            "searchSiteWirelessClientSessions",
            "getSiteEventsForClient",
            "listSiteAllGuestAuthorizations",
            "countSiteGuestAuthorizations",
            "listSiteAllGuestAuthorizationsDerived",
            "searchSiteGuestAuthorization",
            "getSiteGuestAuthorization",
            "countSiteNacClients",
            "countSiteNacClientEvents",
            "searchSiteNacClientEvents",
            "searchSiteNacClients",
            "countSiteWanClientEvents",
            "countSiteWanClients",
            "searchSiteWanClientEvents",
            "searchSiteWanClients",
            "countSiteWiredClients",
            "searchSiteWiredClients",
        ],
    },
    "sites_devices": {
        "description": "Mist provides many ways (device_type specific template, site template, device profile, per-device) to configure devices for different kind of scenarios.\n\nThe precedence goes from most specific to least specific\n\nDevice > Device Profile > RFTemplate (for AP only) > DeviceType-specific Template > Site Template > Site Setting",
        "tools": [
            "listSiteDevices",
            "countSiteDeviceConfigHistory",
            "searchSiteDeviceConfigHistory",
            "countSiteDevices",
            "countSiteDeviceEvents",
            "searchSiteDeviceEvents",
            "exportSiteDevices",
            "countSiteDeviceLastConfig",
            "searchSiteDeviceLastConfigs",
            "searchSiteDevices",
        ],
    },
    "sites_events": {
        "description": "Site events are issues or incidents that affect site-assigned access points (aps) and radius, dhcp, and dns servers.\n\nThey can be investigated and monitored using the insights dashboard in the juniper mist portal. the dashboard provides a summary of site events, including information about the impacted devices and contributing events.\n\nSite events can be categorized as resolved or acknowledged, and additional details can be accessed by clicking on the event.",
        "tools": ["countSiteSystemEvents", "searchSiteSystemEvents"],
    },
    "sites_insights": {
        "description": "Insights is a feature that provides an overview of network experience across the entire site, access points, or clients.\n\nIt offers useful information about current conditions, such as telemetry data from wired switches, edge devices, wireless clients, access points, network applications, and bluetooth low energy (ble) tags.\n\nThese insights can be used to correct issues, make changes, and ensure a good network experience for users.",
        "tools": [
            "getSiteInsightMetricsForClient",
            "getSiteInsightMetricsForDevice",
            "getSiteInsightMetrics",
        ],
    },
    "sites_lan": {
        "description": "Switches Configuration related objects for the sites. It provides access to LAN related objects such as EVPN topologies and network templates.",
        "tools": ["listSiteEvpnTopologies", "listSiteNetworkTemplateDerived"],
    },
    "sites_maps": {
        "description": "A Site Map is a visual representation of the layout and structure of a location, such as a building or campus.\n\nIt includes accurate information about the placement, positions, heights, and orientations of Juniper Mist Access Points (APs) and other devices in the deployment.\n\nThe floorplan is an essential component of location services as it enables the location engine to generate accurate location estimates for client devices, assets, and users at the site.",
        "tools": ["listSiteMaps"],
    },
    "sites_mxedges": {
        "description": "MxEdges (Mist Edges) at the site level are deployed to tunnel traffic at each site due to network constraints or security concerns.\n\nThey can be assigned to a specific site and configured to provide tunneling and radius proxy services for the access points (APs) in that site.\n\nThese Mist Edges allow for the extension of user vlans from the corporate network to the aps, and they support features such as auto preemption for failover, dual tunneling to different mist edge clusters, and anchor tunnels for traffic routing to dmz areas.",
        "tools": [
            "listSiteMxEdges",
            "countSiteMxEdgeEvents",
            "searchSiteMistEdgeEvents",
        ],
    },
    "sites_rfdiags": {
        "description": "Rf Diags is a feature in Juniper Mist location services that allows users to replay recorded sessions of the RF (radio frequency) environment.\n\nIt enables users to gain an understanding of current issues, troubleshoot problems, and review recordings for further analysis or to share with customer support.",
        "tools": [
            "getSiteSiteRfdiagRecording",
            "getSiteRfdiagRecording",
            "downloadSiteRfdiagRecording",
        ],
    },
    "sites_rogues": {
        "description": "Rogues are unauthorized wireless access points that are installed on a network without authorization.\n\nThey can be connected to the LAN via an ethernet cable, similar to a pc, and are typically set up by individuals with malicious intent or by employees trying to cover a dead spot with their own wi-fi hotspot.",
        "tools": [
            "listSiteRogueAPs",
            "listSiteRogueClients",
            "countSiteRogueEvents",
            "searchSiteRogueEvents",
            "getSiteRogueAP",
        ],
    },
    "sites_rrm": {
        "description": "RRM, or Radio Resource Management, is a tool used by large multi-site organizations to efficiently manage their RF spectrum.\n\nIt involves making decisions on channel and power settings for access points (APs) based on factors such as user experience, client count, client usage, and interference.\n\nMist RRM uses a reinforcement learning-based feedback model to monitor the impact of changes in channel and power settings on the capacity and performance of the wireless network. It adapts dynamically to changing conditions throughout the day and aims to optimize wireless coverage and capacity across a site.",
        "tools": [
            "getSiteCurrentChannelPlanning",
            "getSiteCurrentRrmConsiderations",
            "listSiteRrmEvents",
            "listSiteCurrentRrmNeighbors",
        ],
    },
    "sites_sles": {
        "description": "Site SLEs, or Service-Level Expectations, are metrics used to monitor and report on the user experience of a Wireless, Wired or Wan network.\n\nThey are generated through data science and machine learning algorithms and provide insights into various aspects of the network, such as coverage, capacity, connectivity, and performance.\n\nMist SLEs help identify when users do not have sufficient network quality, when they face issues with connecting or roaming between access points, and when there are problems on the wired network.",
        "tools": [
            "getSiteSleClassifierDetails",
            "listSiteSleMetricClassifiers",
            "getSiteSleHistogram",
            "getSiteSleImpactSummary",
            "listSiteSleImpactedApplications",
            "listSiteSleImpactedAps",
            "listSiteSleImpactedChassis",
            "listSiteSleImpactedWiredClients",
            "listSiteSleImpactedGateways",
            "listSiteSleImpactedInterfaces",
            "listSiteSleImpactedSwitches",
            "listSiteSleImpactedWirelessClients",
            "getSiteSleSummary",
            "getSiteSleThreshold",
            "listSiteSlesMetrics",
        ],
    },
    "sites_stats": {
        "description": "Statistics for the sites. It provides access to various statistics related to the site, such as application statistics, call statistics, client statistics, and more.",
        "tools": [
            "getSiteStats",
            "countSiteApps",
            "troubleshootSiteCall",
            "countSiteCalls",
            "searchSiteCalls",
            "getSiteCallsSummary",
            "listSiteTroubleshootCalls",
            "listSiteWirelessClientsStats",
            "searchSiteDiscoveredSwitchesMetrics",
            "countSiteDiscoveredSwitches",
            "listSiteDiscoveredSwitchesMetrics",
            "searchSiteDiscoveredSwitches",
            "getSiteWirelessClientsStatsByMap",
            "listSiteUnconnectedClientStats",
            "listSiteMxEdgesStats",
            "getSiteWxRulesUsage",
        ],
    },
    "sites_synthetic_tests": {
        "description": "Synthetic Tests (Marvis Minis) are a feature of Juniper Networks' Mist platform, designed to proactively identify and resolve network issues before they impact users by simulating user connections and validating network configurations.\n\n\nHere are the key points about Marvis Minis:\n\n* Proactive Testing: Marvis Minis perform user connection tests to validate connectivity and application reachability issues on your network. These tests run automatically every hour and can also be initiated manually by an admin user.\n* Scope and Stress Management: By default, Marvis Minis run on a few APs based on the scope it automatically learns, and it can expand the scope to other APs and switches if necessary, without causing additional stress on network services.\n* Integration with Mist AI: Data from Marvis Minis is continuously fed back into the Mist AI engine, providing additional insights for AIOps responses. This data is also integrated into Marvis Actions for proactive resolution and validation.\n* Subscription and Accessibility: Marvis Minis are available at no extra charge with a Marvis VNA subscription and do not require additional hardware or software.",
        "tools": ["getSiteDeviceSyntheticTest", "searchSiteSyntheticTest"],
    },
    "sites_wan": {
        "description": "WAN Configuration related objects for the sites. It provides access to WAN related objects such as applications, gateway templates, security intelligence profiles, service policies, services, networks, and VPNs.",
        "tools": [
            "listSiteApps",
            "listSiteGatewayTemplateDerived",
            "listSiteNetworksDerived",
            "listSiteSecIntelProfilesDerived",
            "listSiteServicePoliciesDerived",
            "listSiteServicesDerived",
            "countSiteServicePathEvents",
            "searchSiteServicePathEvents",
            "listSiteVpnsDerived",
        ],
    },
    "sites_wan_usages": {
        "description": "tools to retrieve WAN Assurance statistics about the WAN Usage",
        "tools": ["countSiteWanUsage", "searchSiteWanUsage"],
    },
    "sites_webhooks": {
        "description": "A Site Webhook is a configuration that allows real-time events and data from a specific site to be pushed to a provided url.\n\nIt enables the collection of information about various topics such as device events, alarms, audits, client sessions and location updates at the site level.\n\nThe Webhook can be set up and customized using the Mist API, allowing users to receive and analyze specific data from a particular site.",
        "tools": [
            "listSiteWebhooks",
            "countSiteWebhooksDeliveries",
            "searchSiteWebhooksDeliveries",
        ],
    },
    "sites_wlans": {
        "description": "A Site Wlan is a wireless local area network that is configured and applied to a specific site within an organization.\n\nIt allows for the creation and management of wireless network settings, such as SSIDs (service set identifiers), authentication settings, VLAN configurations, etc... for a particular site.\n\nSite Wlans are created and managed at the site level and can only be referenced and used within that particular site.",
        "tools": [
            "listSitePsks",
            "listSiteRfTemplateDerived",
            "listSiteWlans",
            "listSiteWlanDerived",
            "listSiteWxRules",
            "ListSiteWxRulesDerived",
            "listSiteWxTags",
            "getSiteApplicationList",
        ],
    },
    "utilities_upgrade": {
        "description": "tools used to manage device upgrades for a single device, at the site level or at the organization level.",
        "tools": [
            "listOrgDeviceUpgrades",
            "listOrgAvailableDeviceVersions",
            "listOrgMxEdgeUpgrades",
            "listOrgSsrUpgrades",
            "listOrgAvailableSsrVersions",
            "listSiteDeviceUpgrades",
            "listSiteAvailableDeviceVersions",
            "getSiteSsrUpgrade",
        ],
    },
}
