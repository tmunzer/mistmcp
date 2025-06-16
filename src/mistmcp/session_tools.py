"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

from functools import wraps
from typing import Any, Callable, Optional

from fastmcp.exceptions import ToolError

from mistmcp.session_manager import is_tool_enabled_for_current_session


def session_tool(enabled: bool = False, **kwargs):
    """
    Decorator for tools that checks session-level permissions before execution.
    This is a wrapper around the standard @mcp.tool() decorator that adds
    per-session tool enablement checking.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get the tool name from the function
            tool_name = func.__name__

            # Check if the tool is enabled for the current session
            if not is_tool_enabled_for_current_session(tool_name):
                raise ToolError(
                    {
                        "error": "tool_disabled",
                        "message": f"Tool '{tool_name}' is not enabled for this session. "
                        f"Use 'manageMcpTools' to enable it first.",
                        "tool_name": tool_name,
                    }
                )

            # Tool is enabled, proceed with execution
            return await func(*args, **kwargs)

        # Store the original function and configuration for later registration
        setattr(wrapper, "_original_func", func)
        setattr(
            wrapper,
            "_mcp_tool_config",
            {
                "enabled": enabled,  # This controls whether the tool is globally registered
                **kwargs,
            },
        )
        setattr(wrapper, "_is_session_tool", True)

        return wrapper

    return decorator


def require_session_tool(tool_name: str):
    """
    Decorator that requires a specific tool to be enabled in the session.
    Useful for internal functions that should only run when certain tools are available.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not is_tool_enabled_for_current_session(tool_name):
                raise ToolError(
                    {
                        "error": "required_tool_disabled",
                        "message": f"This operation requires the '{tool_name}' tool to be enabled.",
                        "required_tool": tool_name,
                    }
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def get_session_tool_info(func: Callable) -> Optional[dict]:
    """Get session tool configuration from a decorated function"""
    if hasattr(func, "_is_session_tool") and getattr(func, "_is_session_tool"):
        return {
            "name": func.__name__,
            "config": getattr(func, "_mcp_tool_config", {}),
            "original_func": getattr(func, "_original_func", func),
        }
    return None


def register_session_tool_with_mcp(func: Callable, mcp_instance) -> Optional[Any]:
    """
    Register a session tool with an MCP instance.
    Similar to register_tool_with_mcp but for session-aware tools.
    """
    tool_info = get_session_tool_info(func)
    if not tool_info:
        return None

    config = tool_info["config"]

    # Use the MCP instance to create the tool with the wrapper function
    # (which includes session checking)
    tool_decorator = mcp_instance.tool(**config)
    tool = tool_decorator(func)  # Use the wrapper function, not the original

    return tool
