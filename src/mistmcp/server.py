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

from mistmcp.config import ServerConfig
from mistmcp.tool_helper import TOOLS

# Global MCP instance for access from tools
_mcp_instance: FastMCP | None = None


def get_mcp() -> FastMCP | None:
    """Get the current MCP instance"""
    return _mcp_instance


def _load_tools(config: ServerConfig) -> list[str]:
    """Load all available tools into the MCP server"""
    enabled_tools: list[str] = []

    # Always load getSelf first
    try:
        module_path = "mistmcp.tools.self_account.getself"
        if module_path in sys.modules:
            del sys.modules[module_path]
        module = importlib.import_module(module_path)
        if hasattr(module, "getSelf"):
            getattr(module, "getSelf").enable()
            enabled_tools.append("getSelf")
            if config.debug:
                print("Enabled essential tool: getSelf", file=sys.stderr)
    except Exception as e:
        if config.debug:
            print(f"Warning: Could not enable getSelf: {e}", file=sys.stderr)

    # Load all other tools from TOOLS configuration
    for category, category_info in TOOLS.items():
        tools = category_info.get("tools", [])
        if config.debug:
            print(f"Loading {len(tools)} tools from '{category}'", file=sys.stderr)

        for tool_name in tools:
            if tool_name in enabled_tools:
                continue  # Skip already loaded tools

            try:
                snake_name = tool_name.lower().replace(" ", "_").replace("-", "_")
                module_path = f"mistmcp.tools.{category}.{snake_name}"

                if module_path in sys.modules:
                    del sys.modules[module_path]

                module = importlib.import_module(module_path)

                # Find and enable the tool function
                tool_func = None
                if hasattr(module, tool_name):
                    tool_func = getattr(module, tool_name)
                else:
                    # Try case-insensitive search
                    for attr in dir(module):
                        if (
                            attr.lower() == tool_name.lower()
                            and callable(getattr(module, attr))
                            and not attr.startswith("_")
                        ):
                            tool_func = getattr(module, attr)
                            break

                if tool_func:
                    tool_func.enable()
                    enabled_tools.append(tool_name)
                    if config.debug:
                        print(f"  Enabled: {tool_name}", file=sys.stderr)

            except Exception as e:
                if config.debug:
                    print(
                        f"  Warning: Could not load {tool_name}: {e}", file=sys.stderr
                    )

    return enabled_tools


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

When you need to validate the configuration applied to a specific device or site:
1. Identify the template assigned to the site with "getSiteInfo" (if any)
2. Retrieve the template configuration at Org level with "getOrgConfigurationObjects"
3. Check site level configuration with "getSiteSettingsDerived"
4. Check device level configuration with "getSiteConfigurationObjects"
5. Merge configurations (device overrides site, site overrides org) and validate

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
        on_duplicate_tools="replace",
        mask_error_details=False,
    )

    # Store instance globally for tool access
    _mcp_instance = mcp

    # Load all tools
    enabled_tools = _load_tools(config)

    if config.debug:
        print(f"MCP Server ready with {len(enabled_tools)} tools", file=sys.stderr)

    return mcp
