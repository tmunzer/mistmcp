"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import sys

from fastmcp import FastMCP

from mistmcp.config import ServerConfig, ToolLoadingMode
from mistmcp.simple_server import create_mcp_server as create_simple_mcp_server
from mistmcp.tool_loader import ToolLoader


class McpInstance:
    """
    Singleton-like container for managing MCP (Model Context Protocol) instance.
    This class provides a simple way to store and retrieve a FastMCP
    instance globally within the application.
    """

    current_mcp_instance: FastMCP

    def get(self) -> FastMCP:
        """
        Retrieve the current MCP instance.
        Returns:
            FastMCP: The currently stored MCP instance.
        """
        return self.current_mcp_instance

    def set(self, instance: FastMCP) -> None:
        """
        Set the current MCP instance.
        Args:
            instance (FastMCP): The MCP instance to store.
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


def create_mcp_server(config: ServerConfig) -> FastMCP:
    """
    Create and configure a simple MCP server based on the provided configuration.
    """

    # Create the server with appropriate configuration
    try:
        # Create the simple server
        mcp = create_simple_mcp_server(config)

        # Store the instance globally BEFORE configuring tools
        mcp_instance.set(mcp)

        # Configure tools based on configuration
        tool_loader = ToolLoader(config)
        tool_loader.configure_tools(mcp)

        if config.debug:
            print("MCP Server created successfully", file=sys.stderr)
            print(tool_loader.get_enabled_tools_summary(), file=sys.stderr)

        return mcp

    except Exception as e:
        print(f"Error creating MCP server: {e}", file=sys.stderr)
        if config.debug:
            import traceback

            traceback.print_exc()
        raise


def get_mode_instructions(config: ServerConfig) -> str:
    """
    Get mode-specific instructions for the agent
    """

    if config.tool_loading_mode == ToolLoadingMode.MANAGED:
        return """
MANAGED MODE: Only essential tools loaded at startup.

This mode provides only basic essential tools (getSelf, manageMcpTools). Use the manageMcpTools to load additional tool categories as needed.

IMPORTANT:
* If the tool requires the `org_id`, you should be able to get it with the `getSelf` tool
* Use `manageMcpTools` to load additional tool categories when needed
* If the tool requires the `site_id`, you will need to load the 'orgs_sites' category first using manageMcpTools
"""

    if config.tool_loading_mode == ToolLoadingMode.ALL:
        return """
ALL TOOLS MODE: All available tools are loaded and ready to use.

All tool categories have been pre-loaded, so you can use any Mist API functionality immediately without needing to manage tools.

IMPORTANT:
* If the tool requires the `org_id`, you should be able to get it with the `getSelf` tool
* If the tool requires the `site_id`, you should be able to get it with the `listOrgSites` tool. This will also provide the templates assigned to the site.
"""

    return ""
