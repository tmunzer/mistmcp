"""Shared helpers for workflow-oriented facade tools."""

from enum import Enum
from typing import Any, Callable

from fastmcp.tools import FunctionTool, ToolResult


def internal_tool(function: Callable[..., Any]) -> FunctionTool:
    """Wrap an internal operation with Pydantic validation."""
    return FunctionTool.from_function(function)


def arguments(base: dict[str, Any]) -> dict[str, Any]:
    """Omit unset values and serialize enum members for internal operations."""
    return {
        key: value.value if isinstance(value, Enum) else value
        for key, value in base.items()
        if value is not None
    }


async def run_internal_tool(
    tool: FunctionTool, tool_arguments: dict[str, Any]
) -> ToolResult:
    """Run an internal handler and return its already-normalized tool result."""
    return await tool.run(tool_arguments)
