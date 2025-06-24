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
    CONFIGURATION = "configuration"
    CONSTANTS_DEFINITIONS = "constants_definitions"
    ORGS = "orgs"
    ORGS_ALARM_TEMPLATES = "orgs_alarm_templates"
    ORGS_LICENSES = "orgs_licenses"
    CLIENTS = "clients"
    DEVICES = "devices"
    UTILITIES_UPGRADE = "utilities_upgrade"
    ORGS_SLES = "orgs_sles"
    MXEDGES = "mxedges"
    ORGS_SITES = "orgs_sites"
    ORGS_STATS = "orgs_stats"
    MARVIS = "marvis"
    ORGS_NAC = "orgs_nac"
    WEBHOOKS = "webhooks"
    ORGS_WXTAGS = "orgs_wxtags"
    SELF_ACCOUNT = "self_account"
    SITES = "sites"
    SITES_APPLICATIONS = "sites_applications"
    SITES_EVENTS = "sites_events"
    SITES_INSIGHTS = "sites_insights"
    SITES_ROGUES = "sites_rogues"
    SITES_RFDIAGS = "sites_rfdiags"
    SITES_RRM = "sites_rrm"
    SITES_SERVICES = "sites_services"
    SITES_SLES = "sites_sles"
    SITES_STATS = "sites_stats"
    SITES_WAN_USAGES = "sites_wan_usages"
    SITES_WXTAGS = "sites_wxtags"


TOOLS = {
    "clients": {
        "description": "Clients related objects for the sites and organizations. It provides access to clients, guests, and NAC clients. Defining the `site_id` parameter will return the clients for the specified site, while leaving it empty will return the clients for the whole organization.",
        "tools": [
            "searchOrgWirelessClientEvents",
            "searchOrgWirelessClients",
            "searchOrgWirelessClientSessions",
            "searchOrgGuestAuthorization",
            "getOrgGuestAuthorization",
            "searchOrgNacClientEvents",
            "searchOrgNacClients",
            "searchOrgWanClientEvents",
            "searchOrgWanClients",
            "searchOrgWiredClients",
            "searchSiteGuestAuthorization",
            "getSiteGuestAuthorization",
        ],
    },
    "configuration": {
        "description": "Configuration related objects for the sites and organizations. It provides access to various configuration objects such as site settings, device profiles, and more. These objects can be used to configure the network in a consistent manner.",
        "tools": ["getOrgConfigurationObjects", "getSiteConfigurationObjects"],
    },
    "constants_definitions": {
        "description": "tools to retrieve constant values that can be used in different parts of the configuration",
        "tools": [
            "listFingerprintTypes",
            "listInsightMetrics",
            "listLicenseTypes",
            "listWebhookTopics",
        ],
    },
    "devices": {
        "description": "Devices are any Network device managed or monitored by Juniper Mist. It can be * Wireless Access Points * Juniper Switch (EX, QFX) * Juniper WAN Gateway (SRX, SSR) * Mist Edges * Other or 3rd party devices, like Cradlepoint Devices. Mist provides many ways (device_type specific template, site template, device profile, per-device) to configure devices for different kind of scenarios.\n\nThe precedence goes from most specific to least specific\n\nDevice > Device Profile > RFTemplate (for AP only) > DeviceType-specific Template > Site Template > Site Setting",
        "tools": [
            "searchOrgDeviceEvents",
            "listOrgApsMacs",
            "searchOrgDevices",
            "listOrgDevicesSummary",
            "getOrgInventory",
            "searchOrgInventory",
            "getOrgJuniperDevicesCommand",
            "searchSiteDeviceConfigHistory",
            "searchSiteDeviceEvents",
            "searchSiteDeviceLastConfigs",
            "searchSiteDevices",
        ],
    },
    "marvis": {
        "description": "Marvis is a virtual network assistant that provides insights and analytics for the Mist network. It can be used to analyze network performance, troubleshoot issues, and optimize network configurations.\n\nIt includes features such as synthetic tests, which allow users to simulate network traffic and measure performance metrics.",
        "tools": [
            "troubleshootOrg",
            "getSiteDeviceSyntheticTest",
            "searchSiteSyntheticTest",
        ],
    },
    "mxedges": {
        "description": "MX Edge related objects for the organizations. It provides access to Mist Edges, Mist Clusters, and Mist Tunnels.",
        "tools": [
            "searchOrgMistEdgeEvents",
            "searchOrgMxEdges",
            "getOrgMxEdgeUpgradeInfo",
            "searchSiteMistEdgeEvents",
        ],
    },
    "orgs": {
        "description": "An organization usually represents a customer - which has inventories, licenses. An Organization can contain multiple sites. A site usually represents a deployment at the same location (a campus, an office).",
        "tools": [
            "getOrg",
            "searchOrgAlarms",
            "searchOrgEvents",
            "listOrgAuditLogs",
            "getOrgSettings",
        ],
    },
    "orgs_alarm_templates": {
        "description": "An Alarm Template is a set of Alarm Rules that could be applied to\none or more sites (while each site can only pick one Alarm Template), or to the\nwhole org.\n\n\nOnce created, the Alarm template must be assigned with the `alarmtemplate_id` attribute to one of the following\n* the whole org with the [Update Org](/#operations/updateOrg) tool\n* one or multiple sites with the [Update Site Info](/#operations/updateSiteInfo) tool",
        "tools": ["listOrgSuppressedAlarms"],
    },
    "orgs_licenses": {
        "description": "Licenses are a type of service or access that customers can purchase for various features or services offered by a company.\n\nSubscriptions can have different statuses, such as active, expired, exceeded, or trial, depending on their validity and usage. The status of a subscription determines whether it is currently active and valid, has expired, has exceeded the allowed usage limit, or is in a trial period.\n\nLicenses can be activated using an activation code, and the activation process confirms the inputted code and activates the subscription.",
        "tools": [
            "GetOrgLicenseAsyncClaimStatus",
            "getOrgLicensesSummary",
            "getOrgLicensesBySite",
        ],
    },
    "orgs_nac": {
        "description": "NAC related objects for the organizations. It provides access to NAC Endpoints, NAC fingerprints, tags, and rules.",
        "tools": ["searchOrgUserMacs", "getOrgUserMac", "searchOrgClientFingerprints"],
    },
    "orgs_sites": {
        "description": "tools to Create or Get the Organization Sites.\n\n\nUse the [Site Settings](https://www.juniper.net/documentation/us/en/software/mist/api/http/api/sites/setting/overview) to configure or update the Site information.",
        "tools": ["searchOrgSites"],
    },
    "orgs_sles": {
        "description": "Org SLEs, or Service-Level Expectations, are metrics used to monitor and report on the user experience of a Wireless, Wired or Wan network.\n\nThey are generated through data science and machine learning algorithms and provide insights into various aspects of the network, such as coverage, capacity, connectivity, and performance.\n\nMist SLEs help identify when users do not have sufficient network quality, when they face issues with connecting or roaming between access points, and when there are problems on the wired network.",
        "tools": ["getOrgSitesSle", "getOrgSle"],
    },
    "orgs_stats": {
        "description": "Statistics for the organizations. It provides access to various statistics related to the organization, such as BGP peers, devices, MX edges, other devices, ports, sites, tunnels, and VPN peers.",
        "tools": [
            "getOrgStats",
            "searchOrgBgpStats",
            "listOrgDevicesStats",
            "listOrgMxEdgesStats",
            "getOrgMxEdgeStats",
            "getOrgOtherDeviceStats",
            "searchOrgSwOrGwPorts",
            "listOrgSiteStats",
            "searchOrgTunnelsStats",
            "searchOrgPeerPathStats",
        ],
    },
    "orgs_wxtags": {
        "description": "Wxtags are tags or groups that can be created and used within the Org.\n\nThey are used to classify users and resources and can be applied to Access Points, WLAN configurations or WxRules within that site.\n\nOrg WxTags are created and managed at the org level and can only be referenced and used within the org level configuration.",
        "tools": ["getOrgApplicationList", "getOrgCurrentMatchingClientsOfAWxTag"],
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
    "sites_applications": {
        "description": "Applications contains a list of applications users are interested in monitoring / routing / policing",
        "tools": ["listSiteApps"],
    },
    "sites_events": {
        "description": "Site events are issues or incidents that affect site-assigned access points (aps) and radius, dhcp, and dns servers.\n\nThey can be investigated and monitored using the insights dashboard in the juniper mist portal. the dashboard provides a summary of site events, including information about the impacted devices and contributing events.\n\nSite events can be categorized as resolved or acknowledged, and additional details can be accessed by clicking on the event.",
        "tools": ["listSiteRoamingEvents"],
    },
    "sites_insights": {
        "description": "Insights is a feature that provides an overview of network experience across the entire site, access points, or clients.\n\nIt offers useful information about current conditions, such as telemetry data from wired switches, edge devices, wireless clients, access points, network applications, and bluetooth low energy (ble) tags.\n\nThese insights can be used to correct issues, make changes, and ensure a good network experience for users.",
        "tools": [
            "getSiteInsightMetricsForClient",
            "getSiteInsightMetricsForDevice",
            "getSiteInsightMetrics",
        ],
    },
    "sites_rfdiags": {
        "description": "Rf Diags is a feature in Juniper Mist location services that allows users to replay recorded sessions of the RF (radio frequency) environment.\n\nIt enables users to gain an understanding of current issues, troubleshoot problems, and review recordings for further analysis or to share with customer support.",
        "tools": ["getSiteSiteRfdiagRecording", "getSiteRfdiagRecording"],
    },
    "sites_rogues": {
        "description": "Rogues are unauthorized wireless access points that are installed on a network without authorization.\n\nThey can be connected to the LAN via an ethernet cable, similar to a pc, and are typically set up by individuals with malicious intent or by employees trying to cover a dead spot with their own wi-fi hotspot.",
        "tools": [
            "listSiteRogueAPs",
            "listSiteRogueClients",
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
    "sites_services": {
        "description": "A Service represents an a traffic destination or an application that network users connect to. They are associated with users and networks and are used in application policies to permit or deny access.\n\nServices are defined at the [Org level](/#operations/createOrgService).\n\nThe Site level endpoints can be used to get the site services statistics or the derived services, meaning the merge between the site level configuration and the org level configuration.",
        "tools": ["searchSiteServicePathEvents"],
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
            "troubleshootSiteCall",
            "searchSiteCalls",
            "getSiteCallsSummary",
            "listSiteTroubleshootCalls",
            "listSiteWirelessClientsStats",
            "getSiteWirelessClientStats",
            "searchSiteDiscoveredSwitchesMetrics",
            "listSiteDiscoveredSwitchesMetrics",
            "searchSiteDiscoveredSwitches",
            "listSiteMxEdgesStats",
            "getSiteMxEdgeStats",
            "getSiteWxRulesUsage",
        ],
    },
    "sites_wan_usages": {
        "description": "tools to retrieve WAN Assurance statistics about the WAN Usage",
        "tools": ["searchSiteWanUsage"],
    },
    "sites_wxtags": {
        "description": "Wxtags are tags or groups that can be created and used within a specific site.\n\nThey are used to classify users and resources and can be applied to Access Points, WLAN configurations or WxRules within that site.\n\nSite WxTags are created and managed at the site level and can only be referenced and used within that particular site.",
        "tools": ["getSiteApplicationList"],
    },
    "utilities_upgrade": {
        "description": "tools used to manage device upgrades for a single device, at the site level or at the organization level.",
        "tools": [
            "listOrgDeviceUpgrades",
            "getOrgDeviceUpgrade",
            "listOrgAvailableDeviceVersions",
            "listOrgMxEdgeUpgrades",
            "getOrgMxEdgeUpgrade",
            "listOrgSsrUpgrades",
            "listOrgAvailableSsrVersions",
            "listSiteDeviceUpgrades",
            "getSiteDeviceUpgrade",
            "getSiteSsrUpgrade",
        ],
    },
    "webhooks": {
        "description": "A Webhook is a configuration that allows real-time events and data from the Org to be pushed to a provided url.\n\nIt enables the collection of information about various topics such as device events, alarms, and audits updates at the org level.\n\nThe Webhook can be set up and customized using the Mist API, allowing users to receive and analyze specific data from a particular site.",
        "tools": ["searchOrgWebhooksDeliveries", "searchSiteWebhooksDeliveries"],
    },
}
