"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import sys

from mistmcp.config import ServerConfig, ToolLoadingMode
from mistmcp.session_aware_server import (
    SessionAwareFastMCP,
    create_session_aware_mcp_server,
)
from mistmcp.session_manager import session_manager
from mistmcp.tool_loader import ToolLoader


class McpInstance:
    """
    Singleton-like container for managing MCP (Model Context Protocol) instance.
    This class provides a simple way to store and retrieve a SessionAwareFastMCP
    instance globally within the application.
    """

    current_mcp_instance: SessionAwareFastMCP

    def get(self) -> SessionAwareFastMCP:
        """
        Retrieve the current MCP instance.
        Returns:
            SessionAwareFastMCP: The currently stored MCP instance.
        """
        return self.current_mcp_instance

    def set(self, instance: SessionAwareFastMCP) -> None:
        """
        Set the current MCP instance.
        Args:
            instance (SessionAwareFastMCP): The MCP instance to store.
        """
        self.current_mcp_instance = instance


mcp_instance = McpInstance()


def get_current_mcp():
    """Get the current MCP instance"""
    try:
        return mcp_instance.get()
    except AttributeError:
        # current_mcp_instance hasn't been set yet
        return None


def create_mcp_server(config: ServerConfig, transport_mode: str = "stdio"):
    """
    Create and configure a session-aware MCP server based on the provided configuration.

    This creates a multi-client server where each client maintains independent tool configurations
    through session management.
    """

    # Create the server with appropriate configuration
    try:
        # Create the session-aware server instead of regular FastMCP
        mcp = create_session_aware_mcp_server(config, transport_mode)

        # Store the instance globally BEFORE loading tools
        mcp_instance.set(mcp)

        # Load tools based on configuration
        tool_loader = ToolLoader(config)
        tool_loader.load_tools(mcp)

        if config.debug:
            print("Session-aware MCP Server created successfully")
            print(tool_loader.get_loaded_tools_summary())
            print(
                f"Session manager initialized with default tools: {session_manager.default_enabled_tools}"
            )

        return mcp

    except Exception as e:
        print(f"Error creating session-aware MCP server: {e}", file=sys.stderr)
        if config.debug:
            import traceback

            traceback.print_exc()
        raise


def get_mode_instructions(config: ServerConfig) -> str:
    """
    Get mode-specific instructions for the agent
    """
    if config.tool_loading_mode == ToolLoadingMode.MINIMAL:
        return """
MINIMAL MODE: Only essential tools are loaded. Use the `manageMcpTools` tool to enable additional tools as needed.

IMPORTANT:
* Start by using `getSelf` to get organization information
* Use `manageMcpTools` to enable tool categories required for your tasks
* Be selective - only enable the categories you need for the current task
"""

    elif config.tool_loading_mode == ToolLoadingMode.MANAGED:
        return """
MANAGED MODE: Tools are loaded dynamically as needed.

By default, only essential tools are enabled. Use the `manageMcpTools` tool to enable or disable tools within the Mist MCP server:
1. The tools are grouped by category, meaning activating a new category may give access to multiple tools
2. If the tool requires the `org_id`, you should be able to get it with the `getSelf` tool
3. If the tool requires the `site_id`, you should be able to get it with the `listOrgSites` tool
4. Anticipate the required parameters. For example, the user is asking for a resource at the site level, be sure to be able to get the `site_id` information.
5. DO NOT keep categories if they are not required for the next steps.

IMPORTANT:
* Before acting, think twice, take a deep breath, plan your move, and then, start acting.
* After updating the list of tools, stop and ask the user if it is ok to continue
"""

    elif config.tool_loading_mode == ToolLoadingMode.ALL:
        return """
ALL TOOLS MODE: All available tools are loaded and ready to use.

All tool categories have been pre-loaded, so you can use any Mist API functionality immediately without needing to manage tools.

IMPORTANT:
* If the tool requires the `org_id`, you should be able to get it with the `getSelf` tool
* If the tool requires the `site_id`, you should be able to get it with the `listOrgSites` tool
* All tools are available - no need to use `manageMcpTools` unless you want to reduce the tool set
"""

    elif config.tool_loading_mode == ToolLoadingMode.CUSTOM:
        categories = ", ".join(config.tool_categories)
        return f"""
CUSTOM MODE: Pre-loaded with specific tool categories: {categories}

The following tool categories have been pre-loaded and are available for immediate use:
{categories}

You can use `manageMcpTools` to enable additional categories or modify the current selection if needed.

IMPORTANT:
* If the tool requires the `org_id`, you should be able to get it with the `getSelf` tool
* If the tool requires the `site_id`, you should be able to get it with the `listOrgSites` tool
* Use `manageMcpTools` only if you need tools from categories not currently loaded
"""

    return ""
