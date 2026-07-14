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
Juniper Mist Cloud MCP server for managing and monitoring Wi-Fi, LAN, WAN, and
NAC networks. This server uses a workflow-oriented tool catalog.

# START HERE
1. Resolve the organization ID with `mist_get_account(information=account_info)`.
2. Resolve sites and configuration IDs with `mist_get_configuration`.
3. Use `mist_describe` to discover platform constants or configuration schemas.
4. Prefer read/search/insight tools before proposing a configuration change.
5. Only send parameters needed for the selected operation; omit empty values.

# TOOL ROUTING
- Account details, API usage, login failures, and licenses: `mist_get_account`
- Platform constants and configuration schemas: `mist_describe`
- Devices and clients: `mist_search_assets`
- Configuration objects and device config history: `mist_get_configuration`
- Events, alarms, and audit logs: `mist_search_activity`
- NAC user MACs and rogue devices: `mist_search_security`
- Site insight metrics and RRM information: `mist_get_site_insights`
- SLE assurance data: `mist_get_sle`
- Operational statistics: `mist_get_stats`
- Site and WAN topology: `mist_topology`
- Marvis troubleshooting: `mist_troubleshoot`
- Device diagnostics and commands: `mist_utilities`
- Firmware and upgrade operations: `mist_upgrades`

# CRITICAL RULES
- Never guess IDs or MAC addresses; retrieve them first.
- Use the documented top-level parameters for the selected operation and omit
  parameters that do not apply to it.
- Use `mist_describe(subject=constant, name=...)` before filtering by an unknown
  event type, alarm type, metric, model, or other Mist constant.
- Inspect the configuration schema before writes and verify changes by reading the
  affected object afterward.
- Write tools may be hidden in read-only sessions. Do not attempt writes through a
  read-only facade.

# PAGINATION
When a response includes `next` (or legacy `_next`), pass that URL unchanged to
`mist_get_next_page(url=<next_url>)`.
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

# Handwritten tools live outside ``mistmcp.tools`` because the OpenAPI generator
# replaces that entire package on every run.
_CUSTOM_TOOL_MODULES = {
    "mist_topology": "mistmcp.topology.tool",
}


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

    for tool_name, module_path in _CUSTOM_TOOL_MODULES.items():
        try:
            importlib.import_module(module_path)
            if tool_name not in loaded_tools:
                loaded_tools.append(tool_name)
            logger.debug("  Loaded custom tool: %s", tool_name)
        except Exception as e:
            logger.debug("  Warning: Could not load custom tool %s: %s", tool_name, e)

    return loaded_tools


_PROTECTED_WRITE_TAGS = {"write", "write_delete"}


def _write_visible_tags(config: ServerConfig) -> set[str]:
    """Protected write tags that should be visible at build time for this config.

    Authoritative in stateless mode; a behavior-neutral floor in stateful mode, where
    ElicitationMiddleware.on_initialize re-resolves write/write_delete per session.
    """
    if config.enable_write_tools and config.disable_elicitation:
        return {"write"}  # DANGER ZONE: update only, never write_delete
    return set()  # read-only / elicitation-capable: hide both at build time


def _configure_write_visibility(mcp_server: FastMCP, config: ServerConfig) -> None:
    """Install a deterministic hide-all-then-show-visible transform sequence for the
    protected write tags. FastMCP Visibility marks are later-wins, so the EFFECTIVE
    visibility equals this call's resolution even when called repeatedly on the reused
    module singleton (the transform list grows by 1-2 entries per call; create_mcp_server
    runs once per process)."""
    visible = _write_visible_tags(config)
    mcp_server.add_transform(
        Visibility(False, tags=_PROTECTED_WRITE_TAGS, components={"tool"})
    )
    if visible:
        mcp_server.add_transform(Visibility(True, tags=visible, components={"tool"}))


def create_mcp_server(config: ServerConfig) -> FastMCP:
    """Configure and return the MCP server with all tools loaded."""
    enabled_tools = _load_tools(config)

    _configure_write_visibility(mcp, config)

    logger.debug("MCP Server ready with %d tools", len(enabled_tools))

    return mcp
