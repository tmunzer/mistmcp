"""
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
    UTILITIES_UPGRADE = "utilities_upgrade"
    SITES_INSIGHTS = "sites_insights"
    CONSTANTS = "constants"
    SLES = "sles"
    ORGS = "orgs"
    CLIENTS = "clients"
    DEVICES = "devices"
    ORGS_STATS = "orgs_stats"
    MARVIS = "marvis"
    ORGS_NAC = "orgs_nac"
    SELF_ACCOUNT = "self_account"
    SITES = "sites"
    SITES_ROGUES = "sites_rogues"
    SITES_RRM = "sites_rrm"
    SITES_STATS = "sites_stats"


TOOLS = {
    "clients": {
        "description": "Clients related objects for the sites and organizations. It provides access to clients, guests, and NAC clients. Defining the `site_id` parameter will return the clients for the specified site, while leaving it empty will return the clients for the whole organization.",
        "tools": [
            "searchOrgWirelessClientEvents",
            "searchOrgWirelessClients",
            "searchOrgWirelessClientSessions",
            "searchOrgGuestAuthorization",
            "searchOrgNacClientEvents",
            "searchOrgNacClients",
            "searchOrgWanClientEvents",
            "searchOrgWanClients",
            "searchOrgWiredClients",
            "listSiteRoamingEvents",
            "searchSiteGuestAuthorization",
        ],
    },
    "configuration": {
        "description": "Configuration related objects for the sites and organizations. It provides access to various configuration objects such as site settings, device profiles, and more. These objects can be used to configure the network in a consistent manner.",
        "tools": [
            "getSiteConfiguration",
            "getOrgConfigurationObjects",
            "getSiteConfigurationObjects",
        ],
    },
    "constants": {
        "description": "Constants are read-only values and definitions used across the Juniper Mist platform. They include predefined lists of device models, alarm types, and other standardized values that are referenced throughout the API.",
        "tools": ["getConstants"],
    },
    "devices": {
        "description": "Devices are any Network device managed or monitored by Juniper Mist. It can be * Wireless Access Points * Juniper Switch (EX, QFX) * Juniper WAN Gateway (SRX, SSR) * Mist Edges * Other or 3rd party devices, like Cradlepoint Devices. Mist provides many ways (device_type specific template, site template, device profile, per-device) to configure devices for different kind of scenarios.\n\nThe precedence goes from most specific to least specific\n\nDevice > Device Profile > RFTemplate (for AP only) > DeviceType-specific Template > Site Template > Site Setting",
        "tools": [
            "searchOrgDeviceEvents",
            "searchOrgDevices",
            "listOrgDevicesSummary",
            "getOrgInventory",
            "searchOrgMistEdgeEvents",
            "searchSiteDeviceConfigHistory",
            "searchSiteDeviceEvents",
            "searchSiteDeviceLastConfigs",
            "searchSiteDevices",
            "searchSiteMistEdgeEvents",
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
    "orgs": {
        "description": "An organization usually represents a customer - which has inventories, licenses. An Organization can contain multiple sites. A site usually represents a deployment at the same location (a campus, an office).",
        "tools": [
            "getOrg",
            "searchOrgAlarms",
            "listOrgSuppressedAlarms",
            "GetOrgLicenseAsyncClaimStatus",
            "searchOrgEvents",
            "getOrgLicensesSummary",
            "getOrgLicensesBySite",
            "listOrgAuditLogs",
            "getOrgSettings",
            "searchOrgSites",
        ],
    },
    "orgs_nac": {
        "description": "NAC related objects for the organizations. It provides access to NAC Endpoints, NAC fingerprints, tags, and rules.",
        "tools": ["searchOrgUserMacs", "searchOrgClientFingerprints"],
    },
    "orgs_stats": {
        "description": "Statistics for the organizations. It provides access to various statistics related to the organization, such as BGP peers, devices, MX edges, other devices, ports, sites, tunnels, and VPN peers.",
        "tools": [
            "getOrgStats",
            "searchOrgBgpStats",
            "listOrgDevicesStats",
            "listOrgMxEdgesStats",
            "getOrgMxEdgeStats",
            "searchOrgOspfStats",
            "getOrgOtherDeviceStats",
            "searchOrgSwOrGwPorts",
            "listOrgSiteStats",
            "searchOrgTunnelsStats",
            "searchOrgPeerPathStats",
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
    "sites_insights": {
        "description": "Insights related objects for the sites. It provides access to site insights and insight metrics. Site insights are generated by Mist AI to provide actionable information about the network performance and user experience.",
        "tools": ["getInsightMetrics"],
    },
    "sites_rogues": {
        "description": "Rogues are unauthorized wireless access points that are installed on a network without authorization.\n\nThey can be connected to the LAN via an ethernet cable, similar to a pc, and are typically set up by individuals with malicious intent or by employees trying to cover a dead spot with their own wi-fi hotspot.",
        "tools": ["listSiteRogueAPs", "listSiteRogueClients", "searchSiteRogueEvents"],
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
    "sites_stats": {
        "description": "Statistics for the sites. It provides access to various statistics related to the site, such as application statistics, call statistics, client statistics, and more.",
        "tools": [
            "getSiteStats",
            "listSiteWirelessClientsStats",
            "listSiteMxEdgesStats",
            "getSiteWxRulesUsage",
            "searchSiteWanUsage",
            "getSiteApplicationList",
        ],
    },
    "sles": {
        "description": "SLEs, or Service-Level Expectations, are metrics used to monitor and report on the user experience of a Wireless, Wired or Wan network.\\n\\nThey are generated through data science and machine learning algorithms and provide insights into various aspects of the network, such as coverage, capacity, connectivity, and performance.\\n\\nMist SLEs help identify when users do not have sufficient network quality, when they face issues with connecting or roaming between access points, and when there are problems on the wired network.\\n\\n SLEs API Calls at the MSP level can be used to retrieve the SLEs summary for each Organization attached to the MSP account.",
        "tools": [
            "getSiteSle",
            "getOrgSitesSle",
            "getOrgSle",
            "getSiteSleClassifierSummaryTrend",
            "listSiteSleMetricClassifiers",
            "getSiteSleHistogram",
            "getSiteSleThreshold",
            "listSiteSlesMetrics",
        ],
    },
    "utilities_upgrade": {
        "description": "tools used to manage device upgrades for a single device, at the site level or at the organization level.",
        "tools": [
            "listUpgrades",
            "listOrgAvailableDeviceVersions",
            "listOrgAvailableSsrVersions",
        ],
    },
}
