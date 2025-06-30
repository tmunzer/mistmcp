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
            return list(self.available_tools.keys())  # Load all tools (simplified)

        elif self.tool_loading_mode == ToolLoadingMode.ALL:
            return list(self.available_tools.keys())

        return []

    def get_description_suffix(self) -> str:
        """
        Returns a description suffix based on the loading mode
        """

        if self.tool_loading_mode == ToolLoadingMode.MANAGED:
            return "\n\nMODE: MANAGED - Essential tools loaded at startup."

        elif self.tool_loading_mode == ToolLoadingMode.ALL:
            return "\n\nMODE: ALL - All available tools loaded at startup."

        return ""


config = ServerConfig()
