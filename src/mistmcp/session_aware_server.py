"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

from typing import Any, Dict

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_request
from starlette.requests import Request

from mistmcp.config import ServerConfig
from mistmcp.session_manager import get_current_session, session_manager
from mistmcp.tool_helper import TOOLS


class SessionAwareFastMCP(FastMCP):
    """
    Enhanced FastMCP server that supports per-session tool filtering.

    This extends the base FastMCP class to filter tool access based on client sessions.
    Each client maintains independent tool configurations through the session manager.
    """

    def __init__(self, config: ServerConfig, **kwargs) -> None:
        super().__init__(**kwargs)
        self.config = config

    async def get_tools(self) -> Dict[str, Any]:
        """Override get_tools to return session-filtered tools"""
        tools_mode: str = self.config.tool_loading_mode.value
        tools_categories: list[str] = self.config.tool_categories
        try:
            if self.config.transport_mode == "http":
                # For HTTP mode, we can access query parameters directly
                req: Request = get_http_request()
                tools_mode = req.query_params.get(
                    "mode", self.config.tool_loading_mode.value
                )
                if req.query_params.get("categories"):
                    # If 'custom' mode is specified, use provided categories
                    tools_categories = req.query_params.get("categories", "").split(",")
            else:
                # For other transport modes, use the server mode
                tools_mode = self.config.tool_loading_mode.value
            session = get_current_session(tools_mode)
            enabled_tools = session.enabled_tools
        except Exception:
            # If we can't get session context, return default tools only
            # This ensures consistent behavior across different contexts
            enabled_tools = session_manager.default_enabled_tools

        returned_tools = {}
        # Get all registered tools
        all_tools = await super().get_tools()

        if tools_mode == "all":
            # If tools_mode is 'all', return all tools without filtering
            returned_tools = all_tools
        elif tools_categories:
            requested_tools: list[str] = ["getSelf"]
            for category in tools_categories:
                tools = TOOLS.get(category, {}).get("tools", [])
                requested_tools.extend(tools)
            for tool_name, tool_obj in all_tools.items():
                if tool_name in requested_tools:
                    returned_tools[tool_name] = tool_obj

        # Filter tools based on current session's enabled tools
        else:
            for tool_name, tool_obj in all_tools.items():
                if tool_name in enabled_tools:
                    returned_tools[tool_name] = tool_obj

        return returned_tools

    async def get_tool(self, key: str):
        """Override get_tool to enforce session-based access control"""
        try:
            session = get_current_session(self.config.tool_loading_mode.value)
            enabled_tools = session.enabled_tools
        except Exception:
            # If we can't get session context, use default tools
            enabled_tools = session_manager.default_enabled_tools

        # Check if tool is enabled for this session
        if key not in enabled_tools:
            from fastmcp.exceptions import ToolError

            raise ToolError(
                f"Tool '{key}' is not enabled for your session. "
                f"Use 'manageMcpTools' to enable the required tool category first."
            )

        # Tool is enabled, get it from parent
        return await super().get_tool(key)

    async def get_session_info(self) -> Dict[str, Any]:
        """Get information about the current session"""
        try:
            session = get_current_session(self.config.tool_loading_mode.value)

            return {
                "session_id": session.session_id,
                "tools_mode": session.tools_mode,
                "enabled_tools": list(session.enabled_tools),
                "enabled_categories": list(session.enabled_categories),
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
            }
        except Exception as e:
            return {"error": f"Could not get session info: {e}"}

    async def list_all_sessions(self) -> Dict[str, Any]:
        """List all active sessions (for debugging/admin purposes)"""

        sessions_info = {}
        for session_id, session in session_manager.get_all_sessions().items():
            sessions_info[session_id] = {
                "enabled_tools": list(session.enabled_tools),
                "enabled_categories": list(session.enabled_categories),
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "is_expired": session.is_expired(
                    session_manager.session_timeout_minutes
                ),
            }

        return {
            "total_sessions": len(sessions_info),
            "sessions": sessions_info,
            "default_tools": list(session_manager.default_enabled_tools),
        }


def create_session_aware_mcp_server(config: ServerConfig) -> SessionAwareFastMCP:
    """Create a session-aware MCP server"""

    # Base server instructions
    base_instructions = """
Mist MCP Server is a multi-client server that provides access to the Juniper Mist MCP API.
It allows multiple clients to manage their network (Wi-Fi, LAN, WAN, NAC) using the Mist MCP API.

Each client maintains their own session with independent tool configurations.
Use 'manageMcpTools' to enable/disable tools for your specific session.

AGENT INSTRUCTION:
You are a Network Engineer using the Juniper Mist solution to manage your network (Wi-Fi, Lan, Wan, NAC).
All information regarding Organizations, Sites, Devices, Clients, performance, issues and configuration
can be retrieved with the tools provided by the Mist MCP Server.

Your tool access is session-specific - other clients cannot see or modify your tool configuration.
"""

    # Add mode-specific instructions
    from mistmcp.server_factory import get_mode_instructions

    mode_instructions = get_mode_instructions(config)

    # Create the session-aware server
    mcp = SessionAwareFastMCP(
        config=config,
        name="Mist MCP Server (Multi-Client)",
        instructions=base_instructions
        + mode_instructions
        + config.get_description_suffix(),
        on_duplicate_tools="replace",
        mask_error_details=False,
    )

    return mcp
