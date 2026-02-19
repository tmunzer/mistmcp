"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import importlib
import sys

from fastmcp import FastMCP
from fastmcp.server.transforms import Visibility

from mistmcp.config import ServerConfig
from mistmcp.elicitation_middleware import ElicitationMiddleware
from mistmcp.tool_helper import TOOLS

# Global MCP instance for access from tools
_mcp_instance: FastMCP | None = None


def get_mcp() -> FastMCP | None:
    """Get the current MCP instance"""
    return _mcp_instance


def _load_tools(config: ServerConfig) -> list[str]:
    """Load all available tools into the MCP server"""
    loaded_tools: list[str] = []

    # Load all tools from TOOLS configuration
    for category, category_info in TOOLS.items():
        tools = category_info.get("tools", [])
        if config.debug:
            print(f"Loading {len(tools)} tools from '{category}'", file=sys.stderr)

        for tool_name in tools:
            if tool_name in loaded_tools:
                continue  # Skip already loaded tools

            try:
                snake_name = tool_name.lower().replace(" ", "_").replace("-", "_")
                module_path = f"mistmcp.tools.{category}.{snake_name}"

                if module_path in sys.modules:
                    del sys.modules[module_path]

                importlib.import_module(module_path)
                loaded_tools.append(tool_name)
                if config.debug:
                    print(f"  Loaded: {tool_name}", file=sys.stderr)

            except Exception as e:
                if config.debug:
                    print(
                        f"  Warning: Could not load {tool_name}: {e}", file=sys.stderr
                    )

    return loaded_tools


def create_mcp_server(config: ServerConfig) -> FastMCP:
    """
    Create and configure the MCP server with all tools loaded.

    Args:
        config: Server configuration

    Returns:
        Configured FastMCP instance ready to run
    """
    global _mcp_instance

    instructions = """
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

    # Create server
    mcp = FastMCP(
        name="Mist MCP Server",
        instructions=instructions,
        on_duplicate="replace",
        mask_error_details=False,
        middleware=[ElicitationMiddleware()],
    )

    # Write tools are disabled by default and enabled per-session by
    # ElicitationMiddleware during initialization when the client declares
    # elicitation support or explicitly sends X-Disable-Elicitation: true.
    mcp.add_transform(Visibility(False, tags={"write"}, components={"tool"}))

    # Store instance globally for tool access
    _mcp_instance = mcp

    # Load all tools
    enabled_tools = _load_tools(config)

    if config.debug:
        print(f"MCP Server ready with {len(enabled_tools)} tools", file=sys.stderr)

    return mcp
