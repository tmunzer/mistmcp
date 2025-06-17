"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import importlib.resources
import json
from enum import Enum
from typing import List, Optional


class ToolLoadingMode(Enum):
    """Defines how tools should be loaded in the MCP server"""

    MANAGED = "managed"  # Use tool manager for dynamic loading (default)
    ALL = "all"  # Load all available tools at startup
    CUSTOM = "custom"  # Load specific categories provided as parameter


class ServerConfig:
    """Configuration class for the MCP server"""

    def __init__(
        self,
        transport_mode: str = "stdio",
        tool_loading_mode: ToolLoadingMode = ToolLoadingMode.MANAGED,
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
        """Load the tools.json configuration file"""
        try:
            with importlib.resources.path("mistmcp", "tools.json") as json_path:
                with json_path.open(encoding="utf-8") as json_file:
                    self.available_tools = json.load(json_file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            if self.debug:
                print(f"Warning: Could not load tools configuration: {e}")
            self.available_tools = {}

    def get_tools_to_load(self) -> List[str]:
        """
        Returns list of tool categories to load based on the configuration mode
        """
        if self.tool_loading_mode == ToolLoadingMode.MANAGED:
            return []  # Tools will be loaded dynamically via manageMcpTools

        elif self.tool_loading_mode == ToolLoadingMode.ALL:
            return list(self.available_tools.keys())

        elif self.tool_loading_mode == ToolLoadingMode.CUSTOM:
            # Validate that requested categories exist
            valid_categories = []
            for category in self.tool_categories:
                if category in self.available_tools:
                    valid_categories.append(category)
                else:
                    print(f"Warning: Unknown tool category '{category}' - skipping")
            return valid_categories

        return []

    def should_load_tool_manager(self) -> bool:
        """
        Returns True if the tool manager should be loaded
        """
        return self.tool_loading_mode in [
            ToolLoadingMode.MANAGED,
            ToolLoadingMode.CUSTOM,
        ]

    def get_description_suffix(self) -> str:
        """
        Returns a description suffix based on the loading mode
        """

        if self.tool_loading_mode == ToolLoadingMode.MANAGED:
            return "\n\nMODE: MANAGED - Tools loaded dynamically. Use `manageMcpTools` to enable tools as needed."

        elif self.tool_loading_mode == ToolLoadingMode.ALL:
            return "\n\nMODE: ALL - All available tools loaded at startup."

        elif self.tool_loading_mode == ToolLoadingMode.CUSTOM:
            categories = ", ".join(self.tool_categories)
            return f"\n\nMODE: CUSTOM - Pre-loaded tool categories: {categories}. Use `manageMcpTools` to modify."

        return ""


config = ServerConfig()
