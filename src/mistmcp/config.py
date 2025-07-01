"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import importlib.resources
import sys
from enum import Enum
from typing import List, Optional


class ToolLoadingMode(Enum):
    """Defines how tools should be loaded in the MCP server"""

    MANAGED = "managed"  # Use tool manager for dynamic loading
    ALL = "all"  # Load all available tools at startup (default)


class ServerConfig:
    """Configuration class for the MCP server"""

    def __init__(
        self,
        transport_mode: str = "stdio",
        tool_loading_mode: ToolLoadingMode = ToolLoadingMode.ALL,
        tool_categories: Optional[List[str]] = None,
        debug: bool = False,
    ) -> None:
        self.transport_mode: str = transport_mode
        self.tool_loading_mode: ToolLoadingMode = tool_loading_mode
        self.tool_categories: list[str] = tool_categories or []
        self.mist_apitoken: str = ""
        self.mist_host: str = ""
        self.debug = debug

        # Load available tools configuration
        self._load_tools_config()

    def _load_tools_config(self) -> None:
        """Load tools configuration by scanning the tools directory"""
        try:
            import os

            # Get the tools directory path
            with importlib.resources.path("mistmcp", "tools") as tools_path:
                self.available_tools = {}

                # Scan all subdirectories in the tools directory
                for item in os.listdir(tools_path):
                    item_path = tools_path / item
                    if item_path.is_dir() and not item.startswith("__"):
                        # Get all .py files in the category directory
                        tools_in_category = []
                        try:
                            for tool_file in os.listdir(item_path):
                                if tool_file.endswith(
                                    ".py"
                                ) and not tool_file.startswith("__"):
                                    # Extract actual function name from the tool file
                                    try:
                                        tool_file_path = os.path.join(
                                            item_path, tool_file
                                        )
                                        with open(
                                            tool_file_path, "r", encoding="utf-8"
                                        ) as f:
                                            content = f.read()
                                            # Look for async def function_name pattern
                                            import re

                                            match = re.search(
                                                r"^async def ([a-zA-Z_][a-zA-Z0-9_]*)\s*\(",
                                                content,
                                                re.MULTILINE,
                                            )
                                            if match:
                                                function_name = match.group(1)
                                                tools_in_category.append(function_name)
                                            else:
                                                # Fallback to filename-based approach
                                                tool_name = tool_file[
                                                    :-3
                                                ]  # Remove .py extension
                                                tools_in_category.append(tool_name)
                                    except Exception:
                                        # Fallback to filename-based approach
                                        tool_name = tool_file[
                                            :-3
                                        ]  # Remove .py extension
                                        tools_in_category.append(tool_name)
                        except OSError:
                            continue

                        if tools_in_category:
                            self.available_tools[item] = {
                                "description": f"Tools for {item.replace('_', ' ')} functionality",
                                "tools": tools_in_category,
                            }

            if self.debug:
                print(
                    f"Discovered {len(self.available_tools)} tool categories from filesystem",
                    file=sys.stderr,
                )

        except (ImportError, OSError, AttributeError) as e:
            if self.debug:
                print(f"Warning: Could not scan tools directory: {e}", file=sys.stderr)
            # Fallback to empty tools
            self.available_tools = {}

    def get_tools_to_load(self) -> List[str]:
        """
        Returns list of tool categories to load based on the configuration mode
        """
        if self.tool_loading_mode == ToolLoadingMode.MANAGED:
            # In managed mode, only load essential tools initially
            # Tools will be dynamically loaded on demand via manageMcpTools
            return []

        elif self.tool_loading_mode == ToolLoadingMode.ALL:
            # In all mode, load all available tools at startup
            return list(self.available_tools.keys())

        return []

    def get_description_suffix(self) -> str:
        """
        Returns a description suffix based on the loading mode
        """

        if self.tool_loading_mode == ToolLoadingMode.MANAGED:
            return "\n\nMODE: MANAGED - Essential tools loaded at startup, others available on demand."

        elif self.tool_loading_mode == ToolLoadingMode.ALL:
            return "\n\nMODE: ALL - All available tools loaded at startup."

        return ""


config = ServerConfig()
