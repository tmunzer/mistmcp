"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import asyncio
import json
from typing import Annotated

from fastmcp.server.dependencies import get_context
from pydantic import Field

from mistmcp.session_manager import get_current_session, session_manager
from mistmcp.tools_helper import TOOLS, McpToolsCategory

# Don't import the MCP instance at import time to avoid circular dependencies


def snake_case(s: str) -> str:
    """Convert a string to snake_case format."""
    return s.lower().replace(" ", "_").replace("-", "_")


# Define the tool function without decorator - will be registered dynamically
async def manageMcpTools(
    enable_mcp_tools_categories: Annotated[
        list[McpToolsCategory] | str,
        Field(description="Enable tools within the MCP based on the tool category"),
    ] = [],
    #     configuration_required: Annotated[
    #         Optional[bool],
    #         Field(
    #             description="""
    # This is to request the 'write' API endpoints, used to create or configure resources in the Mist Cloud.
    # Do not use it except if it explicitly requested by the user, and ask the user confirmation before using any 'write' tool!
    # """,
    #             default=False,
    #         ),
    #   ] = False,
) -> str:
    """Select the list of tools provided by the MCP server"""

    # Get the current session
    ctx = get_context()
    session = get_current_session("managed")  # Use managed as default mode

    # Load tools configuration
    tools_available = TOOLS

    # Calculate new tool sets
    new_enabled_tools = session.enabled_tools.copy()
    new_enabled_categories = session.enabled_categories.copy()

    changes_made = []

    if isinstance(enable_mcp_tools_categories, str):
        tools_converted = False
        tools = enable_mcp_tools_categories
        try:
            enable_mcp_tools_categories = json.loads(tools)
            tools_converted = True
        except json.JSONDecodeError:
            pass
        if not tools_converted:
            if "," in tools:
                tmp = []
                for t in tools.split(","):
                    try:
                        tmp.append(McpToolsCategory(snake_case(t.strip())))
                    except ValueError:
                        await ctx.warning(f"Unknown category: {t.strip()}")
                enable_mcp_tools_categories = tmp
            else:
                # Single category as string
                try:
                    enable_mcp_tools_categories = [McpToolsCategory(snake_case(tools))]
                except ValueError:
                    await ctx.warning(f"Unknown category: {tools}")
                    enable_mcp_tools_categories = []

    # Process categories to enable
    for category in enable_mcp_tools_categories:
        if isinstance(category, McpToolsCategory):
            # Already an enum, just use it
            pass
        elif isinstance(category, str):
            # Convert string to enum
            try:
                category = McpToolsCategory(snake_case(category))
            except ValueError:
                await ctx.warning(f"Unknown category: {category}")
                continue
        else:
            await ctx.warning(f"Invalid category type: {type(category)}")
            continue
        if not tools_available.get(category.value):
            await ctx.warning(f"Unknown category: {category.value}")
            continue

        if category.value not in new_enabled_categories:
            new_enabled_categories.add(category.value)

            # Add all tools from this category
            for tool in tools_available.get(category.value, {}).get("tools", []):
                new_enabled_tools.add(tool)

            changes_made.append(f"✅ Enabled category: {category.value}")

    # Always keep essential tools enabled
    if session.mode == "all":
        essential_tools = {"getSelf"}
    else:
        essential_tools = {"getSelf", "manageMcpTools"}
    new_enabled_tools.update(essential_tools)

    # Update the session
    session_manager.update_session_tools(
        enabled_tools=new_enabled_tools,
        enabled_categories=new_enabled_categories,
    )

    # Notify server that tool list has changed
    try:
        await ctx.session.send_tool_list_changed()
    except Exception as e:
        await ctx.warning(f"Failed to send tool list changed notification: {e}")

    await asyncio.sleep(0.5)

    # Create completion message
    message = f"""
🔧 MCP TOOLS CONFIGURATION COMPLETE 🔧

Tools enabled: {", ".join(new_enabled_tools)}

"""
    # Categories processed: {", ".join([cat.value  for cat in enable_mcp_tools_categories])}
    await ctx.info(message)

    # Return message requiring user confirmation before continuing
    return f"""⚠️ STOP: USER CONFIRMATION REQUIRED ⚠️

{message}

This tool has completed its configuration. The agent MUST stop here and ask the user for explicit confirmation before proceeding with any other actions.

AGENT INSTRUCTION: Do not continue with any other tools or actions. Present this message to the user and wait for their explicit confirmation to proceed."""


def register_manage_mcp_tools_tool(mcp_instance=None):
    """Register the manageMcpTools tool with the MCP server"""
    if mcp_instance is None:
        from mistmcp.server_factory import get_current_mcp

        mcp_instance = get_current_mcp()

    if mcp_instance:
        # Register the tool manually using FastMCP's tool API
        tool = mcp_instance.tool(
            enabled=True,  # Enable by default
            name="manageMcpTools",
            description="Used to reconfigure the MCP server and define a different list of tools based on the use case (monitor, troubleshooting, ...). IMPORTANT: This tool requires user confirmation after execution before proceeding with other actions.",
            tags={"MCP Configuration"},
            annotations={
                "title": "manageMcpTools",
                "readOnlyHint": False,
                "destructiveHint": False,
                "openWorldHint": False,
            },
        )(manageMcpTools)
        return tool
    return None
