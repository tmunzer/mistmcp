"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import importlib

from fastmcp import FastMCP
from fastmcp.server.transforms import Visibility

from mistmcp.config import ServerConfig
from mistmcp.elicitation_middleware import ElicitationMiddleware
from mistmcp.logger import logger
from mistmcp.tool_helper import TOOLS

_instructions = """
Mist MCP Server provides access to the Juniper Mist MCP API to manage their network (Wi-Fi, LAN, WAN, NAC).

AGENT INSTRUCTION:
You are a Network Engineer using the Juniper Mist solution to manage your network (Wi-Fi, Lan, Wan, NAC).
All information regarding Organizations, Sites, Devices, Clients, performance, issues and configuration
can be retrieved with the tools provided by the Mist MCP Server.

Parameters:
- only send the parameters that are needed for the request, do not send empty or null parameters

IMPORTANT:
* If a tool requires the `org_id`, use the `getSelf` tool to get it
* If a tool requires the `site_id`, use the `listOrgSites` tool to get it

CONFIGURATION OBJECTS:
- aamwprofiles: Sky ATP Advanced Anti-Malware profiles
- alarmtemplates: Alarm Rules templates for sites or org
- aptemplates: AP Templates for Wi-Fi and AP settings
- avprofiles: Antivirus profiles for malware detection
- devices: Physical APs, switches (EX), or gateways (SSR/SRX)
- deviceprofiles: Device configuration profiles
- evpn_topologies: EVPN VxLAN/MP-BGP configurations
- gatewaytemplates: Gateway Templates for site gateways
- mxclusters: Mist Edge Clusters for HA and load balancing
- mxedges: Mist Edge appliances
- mxtunnels: Mist Tunnels for VLAN tunneling
- nactags: NAC Tags for building nacrules
- nacrules: NAC Rules for network access control
- networks: Network subnets and user segments
- networktemplates: Switch configuration templates
- idpprofiles: Intrusion Detection and Prevention profiles
- psks: Multi PSK configurations
- rftemplates: Radio frequency templates
- services: Application definitions for policies
- servicepolicies: Security/firewall policies
- sites: Logical device groupings by location
- sitegroups: Groups of sites for bulk configuration
- sitetemplates: Site attribute templates
- wlantemplates: WLAN, Tunneling, and WxLAN policy collections
- vpns: WAN Overlay VPN configurations
- webhooks: Real-time event push configurations
- wlans: Wireless network (SSID) configurations
- wxrules: WLAN restriction rules
- wxtags: Tags for WxRules
"""

# Module-level MCP instance — imported directly by tool modules
mcp = FastMCP(
    name="Mist MCP Server",
    instructions=_instructions,
    on_duplicate="replace",
    mask_error_details=False,
    middleware=[ElicitationMiddleware()],
)

# Write tools are disabled by default and enabled per-session by
# ElicitationMiddleware during initialization when the client declares
# elicitation support or explicitly sends X-Disable-Elicitation: true.
mcp.add_transform(Visibility(False, tags={"write"}, components={"tool"}))


def _load_tools(config: ServerConfig) -> list[str]:
    """Load all available tools into the MCP server"""
    loaded_tools: list[str] = []

    for category, category_info in TOOLS.items():
        tools = category_info.get("tools", [])
        logger.debug("Loading %d tools from '%s'", len(tools), category)

        for tool_name in tools:
            if tool_name in loaded_tools:
                continue

            try:
                snake_name = tool_name.lower().replace(" ", "_").replace("-", "_")
                module_path = f"mistmcp.tools.{category}.{snake_name}"
                importlib.import_module(module_path)
                loaded_tools.append(tool_name)
                logger.debug("  Loaded: %s", tool_name)

            except Exception as e:
                logger.debug("  Warning: Could not load %s: %s", tool_name, e)

    return loaded_tools


def create_mcp_server(config: ServerConfig) -> FastMCP:
    """Configure and return the MCP server with all tools loaded."""
    enabled_tools = _load_tools(config)

    logger.debug("MCP Server ready with %d tools", len(enabled_tools))

    return mcp
