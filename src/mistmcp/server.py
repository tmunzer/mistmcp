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
from mistmcp.null_strip_middleware import NullStripMiddleware
from mistmcp.tool_helper import TOOLS

_instructions = """
Juniper Mist Cloud MCP server for managing and monitoring Wi-Fi, LAN, WAN, and NAC networks.

# CRITICAL RULES
1. **Never assume IDs or MAC addresses.** Always retrieve them first.
2. **Only send parameters that are needed.** No empty, null, or irrelevant values.
3. **Always resolve `org_id` first** via `mist_get_self(action_type=account_info)`.

# ID RESOLUTION
| Need | Tool | Key Parameters |
| - | - | - |
| org_id | mist_get_self | action_type=account_info |
| site_id | mist_get_configuration_objects | object_type=org_sites, name=<site_name> |
| device MAC/ID | mist_search_org_device | text=<name*>, serial, model, device_type |
| client MAC | mist_search_client | hostname=<name*>, ip=<ip*>, mac=<mac*> |
| config object ID | mist_get_configuration_objects | object_type=<type>, name=<name> |

# KEY WORKFLOWS
- Use `mist_get_constants` to discover valid event_type or insight metric names before searching.
- Use `mist_list_site_sle_info` to discover available SLE metrics before querying SLE data.
- Use `mist_get_configuration_object_schema(verbose=True)` to understand config fields before writing.
- Config objects exist at org and/or site level; site-level takes precedence when both exist.
- `object_type` values `org`, `org_sites`, and `org_devices` are read-only (use with `mist_get_configuration_objects` only).

# CONFIGURATION OBJECTS
Config objects are accessed via `mist_get_configuration_objects` (read) and `mist_change_*` / `mist_update_*` (write).
Site-level takes precedence when both org and site objects of the same type exist.

## Org-Level Only
| object_type | Description |
| - | - |
| org_alarmtemplates | Alarm rules templates assigned to sites |
| org_aptemplates | AP configuration templates (radio, Wi-Fi) |
| org_avprofiles | Antivirus profiles |
| org_aamwprofiles | Advanced Anti-Malware profiles (Sky ATP) |
| org_deviceprofiles | Device config profiles for APs or switches |
| org_evpn_topologies | EVPN VxLAN/MP-BGP underlay topologies |
| org_gatewaytemplates | Gateway (SSR/SRX) templates |
| org_idpprofiles | Intrusion Detection and Prevention profiles |
| org_mxclusters | Mist Edge cluster configs (HA/load balancing) |
| org_mxedges | Mist Edge appliance configs |
| org_mxtunnels | VLAN tunneling to Mist Edge |
| org_nactags | NAC Tags — match conditions for NAC rules |
| org_nacrules | Network Access Control rules |
| org_networktemplates | Switch configuration templates |
| org_psks | Org-level Multi-PSK configs |
| org_rftemplates | RF templates (channels, TX power, bands) |
| org_servicepolicies | Security/firewall policies |
| org_sitegroups | Groups of sites for bulk assignment |
| org_sitetemplates | Site attribute/settings templates |
| org_vpns | WAN Overlay VPN hub/spoke configs |
| org_wlantemplates | WLAN, Tunneling, and WxLAN policy templates |

## Both Org and Site Level (site overrides org)
| org_* / site_* | Description |
| - | - |
| networks | Network/VLAN definitions |
| services | Application/service definitions for firewall policies |
| webhooks | Real-time event push endpoints |
| wlans | Wireless network (SSID) definitions |
| wxrules | WLAN restriction and traffic policy rules |
| wxtags | Tags for WxLAN rules |

## Site-Level Only
| object_type | Description |
| - | - |
| site_devices | Physical devices assigned to a site |
| site_psks | Site-level Multi-PSK configs |
| site_mxedges | Mist Edge appliances at a site |
| site_vpns | Site-level VPN configs |

## Read-Only (mist_get_configuration_objects only)
| object_type | Description |
| - | - |
| org | Organization settings |
| org_sites | List all sites — primary way to get `site_id` |
| org_devices | Full device inventory (all sites + unassigned) |

# PAGINATION
When a response includes `_next`, use `mist_get_next_page(url=<_next>)` for more results.
"""

# Module-level MCP instance — imported directly by tool modules
mcp = FastMCP(
    name="mist_mcp",
    version="0.1.0",
    instructions=_instructions,
    on_duplicate="replace",
    mask_error_details=True,
    middleware=[NullStripMiddleware(), ElicitationMiddleware()],
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
                # snake_name = tool_name.lower().replace(" ", "_").replace("-", "_")
                module_path = f"mistmcp.tools.{tool_name.replace('mist_', '')}"
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
