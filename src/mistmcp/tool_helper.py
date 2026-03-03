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
    INFO = "info"
    DEVICES = "devices"
    UTILITIES_UPGRADE = "utilities_upgrade"
    SITES_INSIGHTS = "sites_insights"
    CONSTANTS = "constants"
    SLES = "sles"
    WRITE = "write"
    WRITE_DELETE = "write_delete"
    SELF_ACCOUNT = "self_account"
    SITES_RRM = "sites_rrm"
    ORGS = "orgs"
    STATS = "stats"
    EVENTS = "events"
    CLIENTS = "clients"
    SITES_ROGUES = "sites_rogues"
    MARVIS = "marvis"
    ORGS_NAC = "orgs_nac"


TOOLS = {
    "clients": {
        "description": "Clients related objects for the sites and organizations. It provides access to clients, guests, and NAC clients. Defining the `site_id` parameter will return the clients for the specified site, while leaving it empty will return the clients for the whole organization.",
        "tools": ["mist_search_guest_authorization", "mist_search_org_client"],
    },
    "configuration": {
        "description": "Configuration related objects for the sites and organizations. It provides access to various configuration objects such as site settings, device profiles, and more. These objects can be used to configure the network in a consistent manner.",
        "tools": [
            "mist_get_site_derived_configuration",
            "mist_get_device_configuration",
            "mist_get_object_schema",
            "mist_get_org_configuration_objects",
            "mist_get_site_configuration_objects",
        ],
    },
    "constants": {
        "description": "Constants are read-only values and definitions used across the Juniper Mist platform. They include predefined lists of device models, alarm types, and other standardized values that are referenced throughout the API.",
        "tools": ["mist_get_constants"],
    },
    "devices": {
        "description": "Devices are any Network device managed or monitored by Juniper Mist. It can be * Wireless Access Points * Juniper Switch (EX, QFX) * Juniper WAN Gateway (SRX, SSR) * Mist Edges * Other or 3rd party devices, like Cradlepoint Devices. Mist provides many ways (device_type specific template, site template, device profile, per-device) to configure devices for different kind of scenarios.\n\nThe precedence goes from most specific to least specific\n\nDevice > Device Profile > RFTemplate (for AP only) > DeviceType-specific Template > Site Template > Site Setting",
        "tools": [
            "mist_get_org_inventory",
            "mist_search_devices",
            "mist_search_site_device_config_history",
            "mist_search_site_device_last_configs",
        ],
    },
    "events": {
        "description": "Events related to the sites and organizations. It provides access to various events such as device events, client events, and more. These events can be used for monitoring and troubleshooting purposes.",
        "tools": ["mist_search_events", "mist_list_audit_logs"],
    },
    "info": {
        "description": "Tools that provide information about the sites and organizations.",
        "tools": ["mist_get_next_page", "mist_get_info"],
    },
    "marvis": {
        "description": "Marvis is a virtual network assistant that provides insights and analytics for the Mist network. It can be used to analyze network performance, troubleshoot issues, and optimize network configurations.\n\nIt includes features such as synthetic tests, which allow users to simulate network traffic and measure performance metrics.",
        "tools": [
            "mist_troubleshoot_org",
            "mist_get_site_device_synthetic_test",
            "mist_search_site_synthetic_test",
        ],
    },
    "orgs": {
        "description": "An organization usually represents a customer - which has inventories, licenses. An Organization can contain multiple sites. A site usually represents a deployment at the same location (a campus, an office).",
        "tools": [
            "mist_get_org_licenses",
            "mist_search_org_alarms",
            "mist_list_org_suppressed_alarms",
            "mist_search_org_sites",
        ],
    },
    "orgs_nac": {
        "description": "NAC related objects for the organizations. It provides access to NAC Endpoints, NAC fingerprints, tags, and rules.",
        "tools": ["mist_search_org_user_macs", "mist_search_org_client_fingerprints"],
    },
    "self_account": {
        "description": "tools related to the currently connected user account.",
        "tools": ["mist_get_self"],
    },
    "sites_insights": {
        "description": "Insights related objects for the sites. It provides access to site insights and insight metrics. Site insights are generated by Mist AI to provide actionable information about the network performance and user experience.",
        "tools": ["mist_get_insight_metrics"],
    },
    "sites_rogues": {
        "description": "Rogues are unauthorized wireless access points that are installed on a network without authorization.\n\nThey can be connected to the LAN via an ethernet cable, similar to a pc, and are typically set up by individuals with malicious intent or by employees trying to cover a dead spot with their own wi-fi hotspot.",
        "tools": ["mist_list_rogue_devices"],
    },
    "sites_rrm": {
        "description": "RRM, or Radio Resource Management, is a tool used by large multi-site organizations to efficiently manage their RF spectrum.\n\nIt involves making decisions on channel and power settings for access points (APs) based on factors such as user experience, client count, client usage, and interference.\n\nMist RRM uses a reinforcement learning-based feedback model to monitor the impact of changes in channel and power settings on the capacity and performance of the wireless network. It adapts dynamically to changing conditions throughout the day and aims to optimize wireless coverage and capacity across a site.",
        "tools": ["mist_get_site_rrm_info"],
    },
    "sles": {
        "description": "SLEs, or Service-Level Expectations, are metrics used to monitor and report on the user experience of a Wireless, Wired or Wan network.\\n\\nThey are generated through data science and machine learning algorithms and provide insights into various aspects of the network, such as coverage, capacity, connectivity, and performance.\\n\\nMist SLEs help identify when users do not have sufficient network quality, when they face issues with connecting or roaming between access points, and when there are problems on the wired network.\\n\\n SLEs API Calls at the MSP level can be used to retrieve the SLEs summary for each Organization attached to the MSP account.",
        "tools": [
            "mist_get_site_sle",
            "mist_list_site_sle_info",
            "mist_get_org_sites_sle",
            "mist_get_org_sle",
        ],
    },
    "stats": {
        "description": "Tools that provide various statistics about the organizations, sites, devices, clients, ports and more.",
        "tools": ["mist_get_stats", "mist_search_site_wan_usage"],
    },
    "utilities_upgrade": {
        "description": "tools used to manage device upgrades for a single device, at the site level or at the organization level.",
        "tools": ["mist_list_upgrades"],
    },
    "write": {
        "description": "Tools that perform write operations, such as creating, updating, or deleting resources in the Juniper Mist platform. These tools allow users to modify configurations, manage devices, and perform other actions that change the state of the network.",
        "tools": [
            "mist_update_site_configuration_objects",
            "mist_update_org_configuration_objects",
        ],
    },
    "write_delete": {
        "description": "Tools that perform both write and delete operations. These tools allow users to create, update, and delete resources in the Juniper Mist platform, providing more flexibility in managing the network configurations and resources.",
        "tools": [
            "mist_change_site_configuration_objects",
            "mist_change_org_configuration_objects",
        ],
    },
}
