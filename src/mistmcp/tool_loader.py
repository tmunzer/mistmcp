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
    """Handles loading of tools based on server configuration"""

    def __init__(self, config: ServerConfig) -> None:
        self.config = config
        self.loaded_tools: list[str] = []

    def snake_case(self, s: str) -> str:
        """Convert a string to snake_case format."""
        return s.lower().replace(" ", "_").replace("-", "_")

    def load_essential_tools(self, mcp_instance=None) -> None:
        """Load essential tools that are always needed"""
        try:
            # Always load getSelf tool - but use dynamic import to avoid authentication at import time
            if mcp_instance is None:
                from mistmcp.server_factory import get_current_mcp

                mcp_instance = get_current_mcp()

            if mcp_instance:
                # Temporarily patch the server_factory module to provide MCP instance during import
                import sys
                import types

                import mistmcp.server_factory

                # Create mock modules for old import patterns
                if "mistmcp.__server" not in sys.modules:
                    mock_server = types.ModuleType("mistmcp.__server")
                    setattr(mock_server, "mcp", mcp_instance)
                    sys.modules["mistmcp.__server"] = mock_server

                if "mistmcp.__mistapi" not in sys.modules:
                    mock_mistapi = types.ModuleType("mistmcp.__mistapi")
                    # Set a placeholder for apisession
                    setattr(mock_mistapi, "apisession", None)
                    sys.modules["mistmcp.__mistapi"] = mock_mistapi

                original_instance = mistmcp.server_factory.mcp_instance.get()
                mistmcp.server_factory.mcp_instance.set(mcp_instance)

                try:
                    # Remove from sys.modules if already loaded to force reimport
                    module_path = "mistmcp.tools.self_account.getself"
                    if module_path in sys.modules:
                        del sys.modules[module_path]

                    module = importlib.import_module(module_path)

                    # Restore original instance
                    mistmcp.server_factory.mcp_instance.set(original_instance)

                    # Look for the tool function
                    if hasattr(module, "getSelf"):
                        tool = getattr(module, "getSelf")
                        # In FastMCP 2.8+, the decorator returns a Tool object, so we can call enable() on it
                        if hasattr(tool, "enable"):
                            tool.enable()
                            self.loaded_tools.append("getSelf")
                            if self.config.debug:
                                print("Loaded essential tool: getSelf")
                        else:
                            # For FastMCP 1.x pattern, manually register the tool
                            mcp_instance.tool(
                                name="getSelf",
                                description="Get 'whoami' and privileges (which org and which sites I have access to)",
                                enabled=True,
                            )(tool)
                            self.loaded_tools.append("getSelf")
                            if self.config.debug:
                                print(
                                    "Loaded essential tool: getSelf (manual registration)"
                                )
                        return
                    elif hasattr(module, "add_tool"):
                        # Call add_tool function if it exists (old FastMCP 1.x pattern)
                        module.add_tool()
                        self.loaded_tools.append("getSelf")
                        if self.config.debug:
                            print("Loaded essential tool: getSelf (via add_tool)")
                        return
                    else:
                        if self.config.debug:
                            print(
                                "Warning: No getSelf function or add_tool function found"
                            )
                        return

                except Exception as e:
                    # Restore original instance in case of error
                    mistmcp.server_factory.mcp_instance.set(original_instance)
                    if self.config.debug:
                        print(f"Warning: Could not load essential tool getSelf: {e}")
                        import traceback

                        traceback.print_exc()

            else:
                if self.config.debug:
                    print("Warning: MCP instance not available for getSelf")

        except (ImportError, AttributeError) as e:
            if self.config.debug:
                print(f"Warning: Could not load essential tool getSelf: {e}")
            # Try to continue without it

    def load_tool_manager(self, mcp_instance=None) -> None:
        """Load the tool manager if needed"""
        if self.config.should_load_tool_manager():
            try:
                if mcp_instance is None:
                    from mistmcp.server_factory import get_current_mcp

                    mcp_instance = get_current_mcp()

                from mistmcp.tool_manager import register_manage_mcp_tools_tool

                if mcp_instance:
                    tool = register_manage_mcp_tools_tool(mcp_instance)
                    if tool:
                        # Tool is already enabled when registered
                        self.loaded_tools.append("manageMcpTools")

                        if self.config.debug:
                            print("Loaded tool manager: manageMcpTools")
                    else:
                        if self.config.debug:
                            print("Warning: Failed to register manageMcpTools")
                else:
                    if self.config.debug:
                        print("Warning: MCP instance not available for tool manager")

            except (ImportError, AttributeError) as e:
                if self.config.debug:
                    print(f"Warning: Could not load tool manager: {e}")
        elif self.config.debug:
            print("Tool manager not needed for this mode")

    def load_category_tools(self, categories: List[str], mcp_instance=None) -> None:
        """Load tools from specific categories"""
        if mcp_instance is None:
            from mistmcp.server_factory import get_current_mcp

            mcp_instance = get_current_mcp()

        if not mcp_instance:
            if self.config.debug:
                print("Warning: MCP instance not available for category tools")
            return

        for category in categories:
            if category not in self.config.available_tools:
                if self.config.debug:
                    print(
                        f"Warning: Category '{category}' not found in available tools"
                    )
                continue

            category_tools = self.config.available_tools[category].get("tools", [])

            if self.config.debug:
                print(f"Loading {len(category_tools)} tools from category '{category}'")

            for tool_name in category_tools:
                try:
                    # Temporarily patch the server_factory module to provide MCP instance during import
                    import sys
                    import types

                    import mistmcp.server_factory

                    # Create mock modules for old import patterns
                    if "mistmcp.__server" not in sys.modules:
                        mock_server = types.ModuleType("mistmcp.__server")
                        setattr(mock_server, "mcp", mcp_instance)
                        sys.modules["mistmcp.__server"] = mock_server

                    if "mistmcp.__mistapi" not in sys.modules:
                        mock_mistapi = types.ModuleType("mistmcp.__mistapi")
                        setattr(mock_mistapi, "apisession", None)
                        sys.modules["mistmcp.__mistapi"] = mock_mistapi

                    original_instance = mistmcp.server_factory.mcp_instance.get()
                    mistmcp.server_factory.mcp_instance.set(mcp_instance)

                    # Dynamically import the tool module
                    module_path = (
                        f"mistmcp.tools.{category}.{self.snake_case(tool_name)}"
                    )

                    # Remove from sys.modules if already loaded to force reimport

                    if module_path in sys.modules:
                        del sys.modules[module_path]

                    module = importlib.import_module(module_path)

                    # Restore original instance
                    mistmcp.server_factory.mcp_instance.set(original_instance)

                    # Look for the tool function or add_tool function
                    if hasattr(module, tool_name):
                        # Skip if already loaded
                        if tool_name in self.loaded_tools:
                            if self.config.debug:
                                print(f"Tool {tool_name} already loaded, skipping")
                            continue

                        tool = getattr(module, tool_name)
                        # Register the tool directly with the MCP instance
                        # The decorator returns a Tool object, so we can call enable() on it
                        if hasattr(tool, "enable"):
                            tool.enable()
                            self.loaded_tools.append(tool_name)
                            if self.config.debug:
                                print(
                                    f"Loaded tool: {tool_name} from category {category}"
                                )
                        else:
                            # For FastMCP 1.x pattern, manually register the tool
                            description = f"Tool {tool_name} from category {category}"
                            mcp_instance.tool(
                                name=tool_name, description=description, enabled=True
                            )(tool)
                            self.loaded_tools.append(tool_name)
                            if self.config.debug:
                                print(
                                    f"Loaded tool: {tool_name} from category {category} (manual registration)"
                                )
                    elif hasattr(module, "add_tool"):
                        # Call add_tool function if it exists (old FastMCP 1.x pattern)
                        # But check if the tool is already loaded first
                        if tool_name in self.loaded_tools:
                            if self.config.debug:
                                print(
                                    f"Tool {tool_name} already loaded, skipping add_tool"
                                )
                            continue

                        module.add_tool()
                        self.loaded_tools.append(tool_name)
                        if self.config.debug:
                            print(
                                f"Loaded tool: {tool_name} from category {category} (via add_tool)"
                            )
                    else:
                        if self.config.debug:
                            print(
                                f"Warning: No {tool_name} function or add_tool function found in {module_path}"
                            )
                        continue

                except (ImportError, AttributeError) as e:
                    if self.config.debug:
                        print(
                            f"Warning: Could not load tool {tool_name} from {category}: {e}"
                        )
                    # Restore original instance in case of error
                    import mistmcp.server_factory

                    mistmcp.server_factory.mcp_instance.set(original_instance)
                    continue
                except Exception as e:
                    if self.config.debug:
                        print(
                            f"Warning: Failed to register tool {tool_name} from {category}: {e}"
                        )
                    # Restore original instance in case of error
                    import mistmcp.server_factory

                    mistmcp.server_factory.mcp_instance.set(original_instance)
                    continue

    def load_tools(self, mcp_instance=None) -> None:
        """Load tools based on the server configuration"""
        if self.config.debug:
            print(f"Loading tools in mode: {self.config.tool_loading_mode.value}")
            print(f"Available tool categories: {len(self.config.available_tools)}")

        # Always load essential tools
        self.load_essential_tools(mcp_instance)

        # Load tool manager if needed
        self.load_tool_manager(mcp_instance)

        # Load category tools based on mode
        categories_to_load = self.config.get_tools_to_load()

        if categories_to_load:
            if self.config.debug:
                print(
                    f"Loading tools from {len(categories_to_load)} categories: {categories_to_load[:3]}..."
                )
            self.load_category_tools(categories_to_load, mcp_instance)
        else:
            if self.config.debug:
                print("No additional categories to load for this mode")

        if self.config.debug:
            print(f"Total tools loaded: {len(self.loaded_tools)}")
            print(f"Loaded tools: {', '.join(self.loaded_tools)}")

    def get_loaded_tools_summary(self) -> str:
        """Return a summary of loaded tools"""
        return f"Loaded {len(self.loaded_tools)} tools: {', '.join(self.loaded_tools)}"
