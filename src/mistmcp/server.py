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
| device MAC/ID | mist_search_device | text=<name*>, serial, model, device_type |
| client MAC | mist_search_client | hostname=<name*>, ip=<ip*>, mac=<mac*> |
| config object ID | mist_get_configuration_objects | object_type=<type>, name=<name> (not supported for site_devices) |

# KEY WORKFLOWS
- Use `mist_get_constants` to discover valid event_type or insight metric names before searching.
- Use `mist_list_site_sle_info` to discover available SLE metrics before querying SLE data.
- Use `mist_get_configuration_object_schema(verbose=True)` to understand config fields before writing.
- Use `mist_update_configuration_objects` for create/update and `mist_change_configuration_objects` for create/update/delete.
- Use `mist_utilities` for device-side diagnostics and maintenance commands such as ping, traceroute, ARP, BGP, OSPF, routes, cable tests, traffic monitoring, and service path checks. Call it without `utility` to list the supported utilities and their extra parameters for a platform.
- `mist_utilities` commands can stream output over WebSocket and may take around a minute to finish.
- Config objects exist at org and/or site level; site-level takes precedence when both exist.
- Object-type naming: read uses `org_*` / `site_*`; aggregated write tools also use `org_*` / `site_*`.
- `name` filtering is not supported for `site_devices`; use `mist_search_device`.

# CONFIGURATION OBJECTS
Config objects are accessed via `mist_get_configuration_objects` (read) and `mist_change_configuration_objects` / `mist_update_configuration_objects` (write).
Site-level takes precedence when both org and site objects of the same type exist.

## Org-Level Read Types
| object_type | Description |
| - | - |
| org_alarmtemplates | Alarm rules templates assigned to sites |
| org_wlans | Org WLAN definitions |
| org_sitegroups | Groups of sites for bulk assignment |
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
| org_networks | Network/VLAN definitions |
| org_psks | Org-level Multi-PSK configs |
| org_rftemplates | RF templates (channels, TX power, bands) |
| org_services | Application/service definitions |
| org_servicepolicies | Security/firewall policies |
| org_sitetemplates | Site attribute/settings templates |
| org_vpns | WAN Overlay VPN hub/spoke configs |
| org_webhooks | Real-time event push endpoints |
| org_wlantemplates | WLAN, Tunneling, and WxLAN policy templates |
| org_wxrules | WLAN restriction and traffic policy rules |
| org_wxtags | Tags for WxLAN rules |

## Site-Level Read Types
| object_type | Description |
| - | - |
| site_evpn_topologies | Site EVPN topologies |
| site_maps | Site map objects |
| site_mxedges | Mist Edge appliances at a site |
| site_psks | Site-level Multi-PSK configs |
| site_webhooks | Site-level webhook endpoints |
| site_wlans | Site WLAN definitions |
| site_wxrules | Site WLAN restriction and traffic policy rules |
| site_wxtags | Site tags for WxLAN rules |
| site_devices | Physical devices assigned to a site |

## Write-Capable Object Types
| object_type | Description |
| - | - |
| org_info | Organization settings (update only) |
| org_settings | Organization settings profile (update only) |
| org_alarmtemplates | Org alarm templates |
| org_wlans | Org WLAN definitions |
| org_sitegroups | Org site groups |
| org_avprofiles | Org antivirus profiles |
| org_aamwprofiles | Org advanced anti-malware profiles |
| org_deviceprofiles | Org device profiles |
| org_gatewaytemplates | Org gateway templates |
| org_idpprofiles | Org IDP profiles |
| org_nactags | Org NAC tags |
| org_nacrules | Org NAC rules |
| org_networktemplates | Org network templates |
| org_networks | Org networks/VLANs |
| org_psks | Org PSKs |
| org_rftemplates | Org RF templates |
| org_services | Org services |
| org_servicepolicies | Org service policies |
| org_sites | Org sites |
| org_sitetemplates | Org site templates |
| org_vpns | Org VPNs |
| org_webhooks | Org webhooks |
| org_wlantemplates | Org WLAN templates |
| org_wxrules | Org Wx rules |
| org_wxtags | Org Wx tags |
| site_settings | Site settings profile (update only) |
| site_devices | Site devices (update only) |
| site_psks | Site-level Multi-PSK configs |
| site_webhooks | Site-level webhook endpoints |
| site_wlans | Site WLAN definitions |
| site_wxrules | Site Wx rules |
| site_wxtags | Site Wx tags |

## Read-Only Helper Types (mist_get_configuration_objects only)
| object_type | Description |
| - | - |
| org | Organization settings |
| org_sites | List all sites — primary way to get `site_id` |

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
