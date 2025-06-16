"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

from functools import wraps
from typing import Any, Dict

from fastmcp.exceptions import ToolError

from mistmcp.session_manager import is_tool_enabled_for_current_session, session_manager


class SessionAwareToolHandler:
    """
    Middleware that intercepts tool calls and checks session permissions.
    This allows tools to be globally registered but only accessible to sessions that have enabled them.
    """

    def __init__(self, mcp_instance) -> None:
        self.mcp_instance = mcp_instance
        self.original_tool_handlers: dict = {}

    def wrap_tool_for_session_checking(self, tool_name: str, original_handler):
        """Wrap a tool handler to check session permissions before execution"""

        @wraps(original_handler)
        async def session_aware_handler(*args, **kwargs):
            # Check if the tool is enabled for the current session
            if not is_tool_enabled_for_current_session(tool_name):
                raise ToolError(
                    {
                        "error": "tool_disabled_for_session",
                        "message": f"Tool '{tool_name}' is not enabled for your session. "
                        f"Use 'manageMcpTools' to enable the required category first.",
                        "tool_name": tool_name,
                        "hint": "Try: manageMcpTools(list_available_categories=True) to see available tool categories.",
                    }
                )

            # Tool is enabled for this session, proceed with execution
            return await original_handler(*args, **kwargs)

        return session_aware_handler

    def apply_session_middleware(self) -> None:
        """Apply session checking middleware to all registered tools"""

        # This is a conceptual implementation - the exact method depends on FastMCP's internals
        # We might need to hook into the tool registry or request handling pipeline

        # For now, we'll assume we can get the tool registry and wrap handlers
        tools = getattr(self.mcp_instance, "_tools", {})

        for tool_name, tool_obj in tools.items():
            # Skip essential tools that should always be available
            if tool_name in {"getSelf", "manageMcpTools"}:
                continue

            # Store original handler
            if tool_name not in self.original_tool_handlers:
                self.original_tool_handlers[tool_name] = tool_obj

            # Wrap the tool with session checking
            if hasattr(tool_obj, "handler"):
                tool_obj.handler = self.wrap_tool_for_session_checking(
                    tool_name, tool_obj.handler
                )

    def get_available_tools_for_session(self) -> Dict[str, Any]:
        """Get tools that are available for a specific session"""

        # Get session or use default tools
        session = session_manager.get_or_create_session()
        if session:
            enabled_tools = session.enabled_tools
        else:
            enabled_tools = session_manager.default_enabled_tools

        # Filter tools based on session permissions
        all_tools = getattr(self.mcp_instance, "_tools", {})
        available_tools = {}

        for tool_name, tool_obj in all_tools.items():
            if tool_name in enabled_tools:
                available_tools[tool_name] = tool_obj

        return available_tools


def create_session_aware_mcp_server(base_server):
    """Convert a regular MCP server to a session-aware one"""

    # Create the session handler
    session_handler = SessionAwareToolHandler(base_server)

    # Apply session middleware
    session_handler.apply_session_middleware()

    # Add session-aware methods to the server
    base_server._session_handler = session_handler
    base_server.get_available_tools_for_session = (
        session_handler.get_available_tools_for_session
    )

    return base_server
