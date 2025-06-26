"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

from typing import Any, Dict

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_request
from starlette.requests import Request

from mistmcp.config import ServerConfig
from mistmcp.session_manager import get_current_session, session_manager
from mistmcp.tool_helper import TOOLS


class SessionAwareFastMCP(FastMCP):
    """
    Enhanced FastMCP server that supports per-session tool filtering.

    This extends the base FastMCP class to filter tool access based on client sessions.
    Each client maintains independent tool configurations through the session manager.
    """

    def __init__(self, config: ServerConfig, **kwargs) -> None:
        super().__init__(**kwargs)
        self.config = config

    async def get_tools(self) -> Dict[str, Any]:
        """Override get_tools to return session-filtered tools"""
        tools_mode: str = self.config.tool_loading_mode.value
        tools_categories: list[str] = self.config.tool_categories
        try:
            if self.config.transport_mode == "http":
                # For HTTP mode, we can access query parameters directly
                req: Request = get_http_request()
                tools_mode = req.query_params.get(
                    "mode", self.config.tool_loading_mode.value
                )
                if req.query_params.get("categories"):
                    # If 'custom' mode is specified, use provided categories
                    tools_categories = req.query_params.get("categories", "").split(",")
            else:
                # For other transport modes, use the server mode
                tools_mode = self.config.tool_loading_mode.value
            session = get_current_session(tools_mode)
            enabled_tools = session.enabled_tools
        except Exception:
            # If we can't get session context, return default tools only
            # This ensures consistent behavior across different contexts
            enabled_tools = session_manager.default_enabled_tools

        returned_tools = {}
        # Get all registered tools
        all_tools = await super().get_tools()

        if tools_mode == "all":
            # If tools_mode is 'all', return all tools without filtering
            returned_tools = all_tools
        elif tools_categories:
            requested_tools: list[str] = ["getSelf"]
            for category in tools_categories:
                tools = TOOLS.get(category, {}).get("tools", [])
                requested_tools.extend(tools)
            for tool_name, tool_obj in all_tools.items():
                if tool_name in requested_tools:
                    returned_tools[tool_name] = tool_obj

        # Filter tools based on current session's enabled tools
        else:
            for tool_name, tool_obj in all_tools.items():
                if tool_name in enabled_tools:
                    returned_tools[tool_name] = tool_obj

        return returned_tools

    async def get_tool(self, key: str):
        """Override get_tool to enforce session-based access control"""
        try:
            session = get_current_session(self.config.tool_loading_mode.value)
            enabled_tools = session.enabled_tools
        except Exception:
            # If we can't get session context, use default tools
            enabled_tools = session_manager.default_enabled_tools

        # Check if tool is enabled for this session
        if key not in enabled_tools:
            from fastmcp.exceptions import ToolError

            raise ToolError(
                f"Tool '{key}' is not enabled for your session. "
                f"Use 'manageMcpTools' to enable the required tool category first."
            )

        # Tool is enabled, get it from parent
        return await super().get_tool(key)

    async def get_session_info(self) -> Dict[str, Any]:
        """Get information about the current session"""
        try:
            session = get_current_session(self.config.tool_loading_mode.value)

            return {
                "session_id": session.session_id,
                "tools_mode": session.tools_mode,
                "enabled_tools": list(session.enabled_tools),
                "enabled_categories": list(session.enabled_categories),
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
            }
        except Exception as e:
            return {"error": f"Could not get session info: {e}"}

    async def list_all_sessions(self) -> Dict[str, Any]:
        """List all active sessions (for debugging/admin purposes)"""

        sessions_info = {}
        for session_id, session in session_manager.get_all_sessions().items():
            sessions_info[session_id] = {
                "enabled_tools": list(session.enabled_tools),
                "enabled_categories": list(session.enabled_categories),
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "is_expired": session.is_expired(
                    session_manager.session_timeout_minutes
                ),
            }

        return {
            "total_sessions": len(sessions_info),
            "sessions": sessions_info,
            "default_tools": list(session_manager.default_enabled_tools),
        }


def create_session_aware_mcp_server(config: ServerConfig) -> SessionAwareFastMCP:
    """Create a session-aware MCP server"""

    # Base server instructions
    base_instructions = """
Mist MCP Server provides access to the Juniper Mist MCP API to manage their network (Wi-Fi, LAN, WAN, NAC).

Each client maintains their own session with independent tool configurations.

AGENT INSTRUCTION:
You are a Network Engineer using the Juniper Mist solution to manage your network (Wi-Fi, Lan, Wan, NAC).
All information regarding Organizations, Sites, Devices, Clients, performance, issues and configuration
can be retrieved with the tools provided by the Mist MCP Server.


CONFIGURATION OBJECT DEFINITIONS AND USAGE:
- aamwprofiles: Sky ATP Advanced Anti-Malware is a comprehensive cloud-based security solution
    that provides multi-layered malware protection. Configured at the Org level and must be referenced
    within the `aamwprofile_id` Service Policies attribute to define the anti-malware profile
- alarmtemplates: An Alarm Template is a set of Alarm Rules that could be applied to
    one or more sites (while each site can only pick one Alarm Template), or to the
    whole org with the `alarmtemplate_id` attribute. Configured at the Org level
- aptemplates: AP Templates are defining Wi-Fi and AP settings that can be assigned
    to Access Points based on different types of rules. AP Templates are configured at the Org level
    and must be assigned to one or multiple sites to be used.
- avprofiles: Antivirus profiles are used to define the content to scan for any malware and the
    action to be taken when malware is detected. Configured at the Org level and must be referenced within
    the `avprofile_id` Service Policies attribute to define the anti-malware profile
- devices: Devices are the physical access points (AP), switches (EX), or gateways (SSR or SRX). A Device
    must be assigned to a Site, and will inherit the Site's and Org's configuration, including
    the Templates, Profiles, and other settings.
- deviceprofiles: A Device Profile contains a subset of Device's configurations you'd like a
    device to have. It will be merged at runtime when we're provisioning an AP. Configured at the Org level.
- evpn_topologies: EVPN allows an alternative but more efficient LAN architecture utilizing
    VxLAN / MP-BGP - separating control plane (MAC / IP Learning) from forwarding
    plane. Configured at the Org or Site level
- gatewaytemplates: Gateway Template is configured at the Org level and applied to a site for gateway(s)
    in a site. When Templates are not used, Site Setting holds settings for multiple device types
    and they can differ to set device_type specific configs, use this whatever is
    defined under `gateway` will overwrite/shadow the one at root-level
- mxclusters: A Mist Edge Cluster (MxCluster) is a group of Juniper Mist Edge devices (one or many)
    that are configured to work together in order to provide high availability and
    load balancing for the tunneling of traffic from access points (APs). Configured at the Org level,
- mxedges: A Mist Edge (MxEdge) is a physical or virtual appliance that is deployed in a network to provide
    centralized data path for user traffic or as a RADIUS Proxy, which was traditionally performed by
    legacy wireless controllers. Configured at the Org level (must be assigned to a MxCluster) or Site level,
- mxtunnels: A Mist Tunnel (MxTunnel) is a configuration object that allows for
    the tunneling of user VLANs from the Access Points (APs) to a central point on
    the network.
- nactags: NAC Tags are the building blocks to compose nacrules, configured at the Org level. They can either
    appear in the  "matching" / "not_matching" sections of a nacrule, in which case they play the role of classifiers,
    or they could appear in the "apply_tags" section of the of a nacrule, in which case they influence the result.
- nacrules: The NAC Rules are a set of rules that devices and users must fulfill in order to gain access to the
    network and use network resources. Configured at the Org level.
- networks: A Network refers to a subnet, a group or segment of users that are defined for
    use across the entire organization. Configured at the Org level and can be
    referenced in Service Policies to define the source or destination of traffic.
- networktemplates: A Network Template is a configuration template that allows for the
    consistent and standardized configuration of switches across an organization's
    network infrastructure. Switch templates can be applied to sites, and they make the initial setup
    of switches easy and adaptable to specific site or switch settings. Sites settings or device settings can
    override the switch template settings, allowing for flexibility in configuration. Configured at the Org level.
- idpprofiles: An IDP profile is a set of predefined rules and actions that determine
    how the Intrusion Detection and Prevention (IDP) system handles network traffic.
    The IDP profile is configured at the Org level and can be applied to an service policy with the `idpprofile_id` attribute.
- psks: A multi PSK (Pre-Shared Key) is a feature that allows the use of multiple
    PSKs for securing network connections. Can be configured at the Org level (for Org WLANs) or Site level
    (for Site WLANs). It is used to manage and control access to the network by
    providing different PSKs for different users or devices.
- rftemplates: Rf Templates are a feature in Juniper Mist wireless assurance that
    allow for uniform radio configurations to be applied across all sites in an organization.
    Configured at the Org level, must be assigned to one or multiple sites to be used.
- services: A Service refers to the applications that network users will connect
    to. These applications represent traffic destinations and are essential for defining
    network policies and security configurations. Configured at the Org level, they can be
    referenced in Service Policies to define the destination of traffic.
- servicepolicies: Services Policies (~firewall rules) are a security policy that defines who can access
    applications, they are used to control access to applications and ensure proper
    traffic management within a network. Configured at the Org level, they must be referenced in
    Gateway Templates Devices Profiles (type=gateway) or Devices (type=gateway) to be used.
- sites: A Mist Site is a logical grouping of devices and resources within an
    organization. It represents a physical location where devices such as access points,
    switches, and gateways are deployed. Sites are used to manage and organize devices,
    configurations, and policies within the Mist platform.
- sitegroups: Site groups are a group of sites under the same Org. It's many-to-many
    mapping to sites, and can be used to apply WLAN templates, Alarm templates,
    or other configurations to multiple sites at once. Site groups are configured at the Org level.
- sitetemplates: Site templates are pre-configured sets of attributes and settings
    that can be applied to one or more sites in a Mist Organization. Configured at the Org level, must
    be assigned to one or multiple sites to be used.
- templates: A WLAN template is a collection of WLANs, Tunneling Policies,
    and WxLAN policies. Can be configured at the Org level, must be assigned to the whole org, one or multiple sites,
    or one or multiples groups of sites to be used.
- vpns: VPNs  are used to create the WAN Assurance Overlay configuration between a Hub and one or multiple
    WAN Edge Gateways.
- webhooks: An Org Webhook is a configuration that allows real-time events and
    data from the Org to be pushed to a provided url. Can be configured at the Org level or Site level.
- wlans: An Org Wlan is a wireless local area network that is configured at the Org level
    and applied to a WLAN template, or at the Site level. It allows for the creation and management of wireless
    network settings, such as SSIDs (service set identifiers), authentication settings, VLAN configurations, etc...
- wxrules: Org WxRules are a set of rules, restrictions, and settings that can be applied to WLANs within a
    specific WLAN Template (Org level configuration) or a site (Site level configuration).
- wxtags: Wxtags are tags or groups that can be created and used within the
    Org WxRules (Org level configuration) or Site WxRules (site level configuration).
"""

    # Add mode-specific instructions
    from mistmcp.server_factory import get_mode_instructions

    mode_instructions = get_mode_instructions(config)

    # Create the session-aware server
    mcp = SessionAwareFastMCP(
        config=config,
        name="Mist MCP Server",
        instructions=base_instructions
        + mode_instructions
        + config.get_description_suffix(),
        on_duplicate_tools="replace",
        mask_error_details=False,
    )

    return mcp
