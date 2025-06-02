"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""
import importlib.resources
import json
import asyncio
from enum import Enum
from pydantic import Field
from typing import Annotated, Optional
from fastmcp.server.dependencies import get_context
from mistmcp.__server import mcp
from . import tools

tools.self_account.getself.add_tool()

with importlib.resources.path("mistmcp", "tools.json") as json_path:
    with json_path.open() as json_file:
        TOOLS_AVAILABLE = json.load(json_file)

TOOLS_ENABLED = {}

class McpToolsCategory(Enum):
    CONSTANTS_DEFINITIONS = "constants_definitions"
    CONSTANTS_EVENTS = "constants_events"
    CONSTANTS_MODELS = "constants_models"
    ORGS = "orgs"
    ORGS_DEVICES___SSR = "orgs_devices___ssr"
    ORGS_ADVANCED_ANTI_MALWARE_PROFILES = "orgs_advanced_anti_malware_profiles"
    ORGS_ALARMS = "orgs_alarms"
    ORGS_ALARM_TEMPLATES = "orgs_alarm_templates"
    ORGS_AP_TEMPLATES = "orgs_ap_templates"
    ORGS_ANTIVIRUS_PROFILES = "orgs_antivirus_profiles"
    ORGS_LICENSES = "orgs_licenses"
    ORGS_CLIENTS___WIRELESS = "orgs_clients___wireless"
    ORGS_DEVICE_PROFILES = "orgs_device_profiles"
    ORGS_DEVICES = "orgs_devices"
    ORGS_EVENTS = "orgs_events"
    ORGS_EVPN_TOPOLOGIES = "orgs_evpn_topologies"
    ORGS_GATEWAY_TEMPLATES = "orgs_gateway_templates"
    ORGS_GUESTS = "orgs_guests"
    ORGS_IDP_PROFILES = "orgs_idp_profiles"
    ORGS_SLES = "orgs_sles"
    ORGS_INVENTORY = "orgs_inventory"
    ORGS_LOGS = "orgs_logs"
    ORGS_MARVIS_INVITES = "orgs_marvis_invites"
    ORGS_MXCLUSTERS = "orgs_mxclusters"
    ORGS_MXEDGES = "orgs_mxedges"
    ORGS_MXTUNNELS = "orgs_mxtunnels"
    ORGS_CLIENTS___NAC = "orgs_clients___nac"
    ORGS_NAC_RULES = "orgs_nac_rules"
    ORGS_NAC_TAGS = "orgs_nac_tags"
    ORGS_NETWORKS = "orgs_networks"
    ORGS_NETWORK_TEMPLATES = "orgs_network_templates"
    ORGS_DEVICES___OTHERS = "orgs_devices___others"
    ORGS_PSKS = "orgs_psks"
    ORGS_RF_TEMPLATES = "orgs_rf_templates"
    ORGS_SECURITY_POLICIES = "orgs_security_policies"
    ORGS_SERVICE_POLICIES = "orgs_service_policies"
    ORGS_SERVICES = "orgs_services"
    ORGS_SETTING = "orgs_setting"
    ORGS_INTEGRATION_SKYATP = "orgs_integration_skyatp"
    ORGS_SITEGROUPS = "orgs_sitegroups"
    ORGS_SITES = "orgs_sites"
    ORGS_SITE_TEMPLATES = "orgs_site_templates"
    ORGS_STATS = "orgs_stats"
    ORGS_STATS___ASSETS = "orgs_stats___assets"
    ORGS_STATS___BGP_PEERS = "orgs_stats___bgp_peers"
    ORGS_STATS___DEVICES = "orgs_stats___devices"
    ORGS_STATS___MXEDGES = "orgs_stats___mxedges"
    ORGS_STATS___OTHER_DEVICES = "orgs_stats___other_devices"
    ORGS_STATS___PORTS = "orgs_stats___ports"
    ORGS_STATS___SITES = "orgs_stats___sites"
    ORGS_STATS___TUNNELS = "orgs_stats___tunnels"
    ORGS_STATS___VPN_PEERS = "orgs_stats___vpn_peers"
    ORGS_WLAN_TEMPLATES = "orgs_wlan_templates"
    ORGS_MARVIS = "orgs_marvis"
    ORGS_USER_MACS = "orgs_user_macs"
    ORGS_VPNS = "orgs_vpns"
    ORGS_CLIENTS___WAN = "orgs_clients___wan"
    ORGS_WEBHOOKS = "orgs_webhooks"
    ORGS_CLIENTS___WIRED = "orgs_clients___wired"
    ORGS_WLANS = "orgs_wlans"
    ORGS_WXRULES = "orgs_wxrules"
    ORGS_WXTAGS = "orgs_wxtags"
    ORGS_WXTUNNELS = "orgs_wxtunnels"
    ADMINS = "admins"
    SELF_ACCOUNT = "self_account"
    SELF_AUDIT_LOGS = "self_audit_logs"
    SELF_ALARMS = "self_alarms"
    SITES = "sites"
    SITES_ALARMS = "sites_alarms"
    SITES_ANOMALY = "sites_anomaly"
    SITES_APPLICATIONS = "sites_applications"
    SITES_AP_TEMPLATES = "sites_ap_templates"
    SITES_CLIENTS___WIRELESS = "sites_clients___wireless"
    SITES_DEVICE_PROFILES = "sites_device_profiles"
    SITES_DEVICES = "sites_devices"
    SITES_DEVICES___WIRELESS = "sites_devices___wireless"
    SITES_DEVICES___WAN_CLUSTER = "sites_devices___wan_cluster"
    SITES_SYNTHETIC_TESTS = "sites_synthetic_tests"
    SITES_DEVICES___WIRED___VIRTUAL_CHASSIS = "sites_devices___wired___virtual_chassis"
    SITES_EVENTS = "sites_events"
    SITES_EVPN_TOPOLOGIES = "sites_evpn_topologies"
    SITES_GATEWAY_TEMPLATES = "sites_gateway_templates"
    SITES_GUESTS = "sites_guests"
    SITES_INSIGHTS = "sites_insights"
    ORGS_NAC_FINGERPRINTS = "orgs_nac_fingerprints"
    SITES_ROGUES = "sites_rogues"
    SITES_MAPS = "sites_maps"
    SITES_MAPS___AUTO_PLACEMENT = "sites_maps___auto_placement"
    SITES_MAPS___AUTO_ZONE = "sites_maps___auto_zone"
    SITES_MXEDGES = "sites_mxedges"
    SITES_CLIENTS___NAC = "sites_clients___nac"
    SITES_NETWORKS = "sites_networks"
    SITES_NETWORK_TEMPLATES = "sites_network_templates"
    SITES_DEVICES___OTHERS = "sites_devices___others"
    SITES_PSKS = "sites_psks"
    SITES_RFDIAGS = "sites_rfdiags"
    SITES_RF_TEMPLATES = "sites_rf_templates"
    SITES_RRM = "sites_rrm"
    SITES_SECINTEL_PROFILES = "sites_secintel_profiles"
    SITES_SERVICE_POLICIES = "sites_service_policies"
    SITES_SERVICES = "sites_services"
    SITES_SETTING = "sites_setting"
    SITES_SITE_TEMPLATES = "sites_site_templates"
    SITES_SKYATP = "sites_skyatp"
    SITES_SLES = "sites_sles"
    SITES_STATS = "sites_stats"
    SITES_STATS___APPS = "sites_stats___apps"
    SITES_STATS___BGP_PEERS = "sites_stats___bgp_peers"
    SITES_STATS___CALLS = "sites_stats___calls"
    SITES_STATS___CLIENTS_WIRELESS = "sites_stats___clients_wireless"
    SITES_STATS___DEVICES = "sites_stats___devices"
    SITES_STATS___DISCOVERED_SWITCHES = "sites_stats___discovered_switches"
    SITES_STATS___MXEDGES = "sites_stats___mxedges"
    SITES_STATS___PORTS = "sites_stats___ports"
    SITES_STATS___WXRULES = "sites_stats___wxrules"
    SITES_VPNS = "sites_vpns"
    SITES_CLIENTS___WAN = "sites_clients___wan"
    SITES_WAN_USAGES = "sites_wan_usages"
    SITES_WEBHOOKS = "sites_webhooks"
    SITES_CLIENTS___WIRED = "sites_clients___wired"
    SITES_WLANS = "sites_wlans"
    SITES_WXRULES = "sites_wxrules"
    SITES_WXTAGS = "sites_wxtags"
    SITES_WXTUNNELS = "sites_wxtunnels"


@mcp.tool(
    name="manageMcpTools",
    description="Used to reconfigure the MCP server and define a different list of tools based on the use case (monitor, troubleshooting, ...). IMPORTANT: This tool requires user confirmation after execution before proceeding with other actions.",
    tags={"MCP Configuration"},
    annotations={
        "title": "manageMcpTools",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False 
    }
)
async def manageMcpTools(
    enable_mcp_tools_categories:Annotated[list[McpToolsCategory], Field(description="""Enable tools within the MCP based on the tool category""")] = [],
    configuration_required:Annotated[Optional[bool], Field(description="""
This is to request the 'write' API endpoints, used to create or configure resources in the Mist Cloud. 
Do not use it except if it explicitly requested by the user, and ask the user confirmation before using any 'write' tool!
""", default=False
)]=False,
) -> str:
    """Select the list of tools provided by the MCP server"""
    global TOOLS_ENABLED
    # Get the MCP server context
    ctx = get_context()
    tools_enabled = TOOLS_ENABLED

     # Disable requested tools based on categories
    for category in disable_mcp_tools_categories:
        await ctx.info(f"{category.value} -> disabling category")
        if not tools_enabled.get(category.value):
            await ctx.warning(f"{category.value} -> not enabled")
            
            await ctx.info(f"{category.value} -> Trying to unload the category tools")
            # Check if category exists in available tools
            if not TOOLS_AVAILABLE.get(category.value):
                await ctx.warning(f"{category.value} -> Unknown category")
                continue
                
            # Load each tool in the category
            for tool in TOOLS_AVAILABLE[category.value]["tools"]:
                import_name = f"mistmcp.tools.{category.value}.{tool}"
                await ctx.debug(f"{category.value} -> Category available")
                await ctx.debug(f"{category.value}.{tool} -> Unloading the tool")
                try:
                    # Import the module containing the tool
                    module = importlib.import_module(f"mistmcp.tools.{category.value}")
                    await ctx.info(f"{import_name} -> module loaded")
                    
                    # Add the tool to MCP server
                    getattr(module, tool).remove_tool()
                    await ctx.info(f"{tool} -> \"remove_tool()\" function triggered")
                    
                    
                except (ImportError, AttributeError) as e:
                    # Handle errors during tool loading
                    await ctx.error(f"{import_name} -> failed to load the tool: {str(e)}")
                    continue
            del tools_enabled[category.value]
    
    # Enable requested tools based on categories
    for category in enable_mcp_tools_categories:
        await ctx.info(f"{category.value} -> enabling category")
        # Check if category exists in available tools
        if not TOOLS_AVAILABLE.get(category.value):
            await ctx.warning(f"{category.value} -> Unknown category")
            continue
            
        # Load each tool in the category
        for tool in TOOLS_AVAILABLE[category.value]["tools"]:
            import_name = f"mistmcp.tools.{category.value}.{tool}"
            await ctx.debug(f"{category.value} -> Category available")
            await ctx.debug(f"{category.value}.{tool} -> Loading the tool")
            try:
                # Import the module containing the tool
                module = importlib.import_module(f"mistmcp.tools.{category.value}")
                await ctx.info(f"{import_name} -> module loaded")
                
                # Add the tool to MCP server
                getattr(module, tool).add_tool()
                await ctx.info(f"{tool} -> \"add_tool()\" function triggered")
                if not tools_enabled.get(category.value):
                    tools_enabled[category.value] = []
                tools_enabled[category.value].append(tool)
                
            except (ImportError, AttributeError) as e:
                # Handle errors during tool loading
                await ctx.error(f"{import_name} -> failed to load the tool: {str(e)}")
                continue

    # Add a small delay to ensure tools are registered with server
    TOOLS_ENABLED = tools_enabled
    await asyncio.sleep(.5)
    await ctx.session.send_tool_list_changed()
    await asyncio.sleep(.5)
    # Log final list of enabled tools
    message = f"""
🔧 MCP TOOLS CONFIGURATION COMPLETE 🔧

Tools enabled: {json.dumps(tools_enabled)}

"""
# ⚠️  IMPORTANT: STOP PROCESSING AND CONFIRM ⚠️

# The MCP server tool configuration has been updated. Before proceeding with any further actions, please confirm that you want to continue with this new tool configuration.

# Do you want to proceed? (yes/no)
    await ctx.info(message)

    # Return a message that forces the agent to stop and ask for confirmation
    return f"""⚠️ STOP: USER CONFIRMATION REQUIRED ⚠️

{message}

This tool has completed its configuration. The agent MUST stop here and ask the user for explicit confirmation before proceeding with any other actions.

AGENT INSTRUCTION: Do not continue with any other tools or actions. Present this message to the user and wait for their explicit confirmation to proceed."""
