"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import importlib
from typing import List

from mistmcp.config import ServerConfig


class ToolLoader:
    """Handles loading and enabling/disabling of tools based on server configuration"""

    def __init__(self, config: ServerConfig) -> None:
        self.config = config
        self.enabled_tools: list[str] = []

    def snake_case(self, s: str) -> str:
        """Convert a string to snake_case format."""
        return s.lower().replace(" ", "_").replace("-", "_")

    def enable_tool_by_name(self, tool_name: str, category: str, mcp_instance) -> bool:
        """Enable a specific tool by importing its module and calling enable()"""
        try:
            # Import the tool module
            snake_case_name = self.snake_case(tool_name)
            module_path = f"mistmcp.tools.{category}.{snake_case_name}"

            # Remove from sys.modules to force reimport
            import sys

            if module_path in sys.modules:
                del sys.modules[module_path]

            # Temporarily set MCP instance for import
            import mistmcp.server_factory

            original_instance = None
            try:
                original_instance = mistmcp.server_factory.mcp_instance.get()
            except AttributeError:
                original_instance = None
            mistmcp.server_factory.mcp_instance.set(mcp_instance)

            try:
                module = importlib.import_module(module_path)

                # Find the function (try different case variations)
                tool_function = None
                if hasattr(module, tool_name):
                    tool_function = getattr(module, tool_name)
                else:
                    # Try case-insensitive search
                    for attr_name in dir(module):
                        if (
                            attr_name.lower() == tool_name.lower()
                            and callable(getattr(module, attr_name))
                            and not attr_name.startswith("_")
                        ):
                            tool_function = getattr(module, attr_name)
                            break

                if tool_function:
                    tool_function.enable()
                    self.enabled_tools.append(tool_name)
                    if self.config.debug:
                        print(f"Enabled tool: {tool_name}")
                    return True
                else:
                    if self.config.debug:
                        print(
                            f"Warning: Function {tool_name} not found in {module_path}"
                        )
                    return False

            finally:
                # Restore original instance
                if original_instance is not None:
                    mistmcp.server_factory.mcp_instance.set(original_instance)

        except Exception as e:
            if self.config.debug:
                print(f"Warning: Could not enable tool {tool_name}: {e}")
            return False

    def enable_getself_tool(self, mcp_instance) -> bool:
        """Enable the getSelf tool"""
        try:
            import sys

            import mistmcp.server_factory

            # Set MCP instance for import
            original_instance = None
            try:
                original_instance = mistmcp.server_factory.mcp_instance.get()
            except AttributeError:
                original_instance = None
            mistmcp.server_factory.mcp_instance.set(mcp_instance)

            try:
                module_path = "mistmcp.tools.self_account.getself"
                if module_path in sys.modules:
                    del sys.modules[module_path]

                module = importlib.import_module(module_path)

                if hasattr(module, "getSelf"):
                    tool = getattr(module, "getSelf")
                    tool.enable()
                    self.enabled_tools.append("getSelf")
                    if self.config.debug:
                        print("Enabled essential tool: getSelf")
                    return True
                else:
                    if self.config.debug:
                        print("Warning: getSelf function not found")
                    return False

            finally:
                if original_instance is not None:
                    mistmcp.server_factory.mcp_instance.set(original_instance)

        except Exception as e:
            if self.config.debug:
                print(f"Warning: Could not enable getSelf: {e}")
            return False

    def enable_managemcp_tool(self, mcp_instance) -> bool:
        """Enable the manageMcpTools tool"""
        try:
            from mistmcp.tool_manager import register_manage_mcp_tools_tool

            tool = register_manage_mcp_tools_tool(mcp_instance)
            if tool:
                self.enabled_tools.append("manageMcpTools")
                if self.config.debug:
                    print("Enabled essential tool: manageMcpTools")
                return True
            else:
                if self.config.debug:
                    print("Warning: Could not register manageMcpTools")
                return False

        except Exception as e:
            if self.config.debug:
                print(f"Warning: Could not enable manageMcpTools: {e}")
            return False

    def configure_tools(self, mcp_instance=None) -> None:
        """Configure tools based on the server mode"""
        if mcp_instance is None:
            from mistmcp.server_factory import get_current_mcp

            mcp_instance = get_current_mcp()

        if not mcp_instance:
            if self.config.debug:
                print("Warning: MCP instance not available")
            return

        if self.config.debug:
            print(f"Configuring tools for mode: {self.config.tool_loading_mode.value}")

        # Always enable getSelf tool
        self.enable_getself_tool(mcp_instance)

        if self.config.tool_loading_mode.value == "managed":
            # Managed mode: only getSelf and manageMcpTools
            self.enable_managemcp_tool(mcp_instance)
            if self.config.debug:
                print("Managed mode: Only essential tools enabled")

        elif self.config.tool_loading_mode.value == "all":
            # All mode: enable all tools except manageMcpTools
            if self.config.debug:
                print("All mode: Enabling all tools...")

            for category, category_info in self.config.available_tools.items():
                tools = category_info.get("tools", [])
                if self.config.debug:
                    print(f"Enabling {len(tools)} tools from category '{category}'")

                for tool_name in tools:
                    # Skip manageMcpTools in all mode
                    if tool_name == "manageMcpTools":
                        continue
                    # Skip getSelf since it's already enabled
                    if tool_name == "getSelf":
                        continue

                    self.enable_tool_by_name(tool_name, category, mcp_instance)

        if self.config.debug:
            print(f"Total tools enabled: {len(self.enabled_tools)}")
            print(f"Enabled tools: {', '.join(self.enabled_tools)}")

    def enable_categories(self, categories: List[str], mcp_instance=None) -> int:
        """Enable tools from specific categories (used by manageMcpTools)"""
        if mcp_instance is None:
            from mistmcp.server_factory import get_current_mcp

            mcp_instance = get_current_mcp()

        if not mcp_instance:
            if self.config.debug:
                print("Warning: MCP instance not available for enabling categories")
            return 0

        enabled_count = 0
        for category in categories:
            if category not in self.config.available_tools:
                if self.config.debug:
                    print(f"Warning: Category '{category}' not found")
                continue

            tools = self.config.available_tools[category].get("tools", [])
            if self.config.debug:
                print(f"Enabling {len(tools)} tools from category '{category}'")

            for tool_name in tools:
                # Skip if already enabled
                if tool_name in self.enabled_tools:
                    continue

                if self.enable_tool_by_name(tool_name, category, mcp_instance):
                    enabled_count += 1

        return enabled_count

    def get_enabled_tools_summary(self) -> str:
        """Return a summary of enabled tools"""
        return (
            f"Enabled {len(self.enabled_tools)} tools: {', '.join(self.enabled_tools)}"
        )
