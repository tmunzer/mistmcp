"""Tests for mistmcp configuration module"""

import pytest

from mistmcp.config import ServerConfig, ToolLoadingMode


class TestToolLoadingMode:
    """Test ToolLoadingMode enum"""

    def test_enum_values(self) -> None:
        """Test that all enum values are correct"""
        assert ToolLoadingMode.MANAGED.value == "managed"
        assert ToolLoadingMode.ALL.value == "all"

    def test_enum_creation_from_string(self) -> None:
        """Test creating enum from string values"""
        assert ToolLoadingMode("managed") == ToolLoadingMode.MANAGED
        assert ToolLoadingMode("all") == ToolLoadingMode.ALL

    def test_invalid_enum_value(self) -> None:
        """Test that invalid enum values raise ValueError"""
        with pytest.raises(ValueError):
            ToolLoadingMode("invalid")


class TestServerConfig:
    """Test ServerConfig class"""

    def test_default_configuration(self) -> None:
        """Test default configuration values"""
        config = ServerConfig()
        assert config.tool_loading_mode == ToolLoadingMode.MANAGED
        assert config.tool_categories == []
        assert config.debug is False
        assert hasattr(config, "available_tools")

    def test_managed_configuration(self) -> None:
        """Test managed mode configuration"""
        config = ServerConfig(tool_loading_mode=ToolLoadingMode.MANAGED)
        assert config.tool_loading_mode == ToolLoadingMode.MANAGED
        # In simplified mode, managed mode loads all available tools
        tools = config.get_tools_to_load()
        assert isinstance(tools, list)

    def test_all_configuration(self) -> None:
        """Test all mode configuration"""
        config = ServerConfig(tool_loading_mode=ToolLoadingMode.ALL)
        assert config.tool_loading_mode == ToolLoadingMode.ALL
        # get_tools_to_load() returns all available tools
        tools = config.get_tools_to_load()
        assert isinstance(tools, list)

    def test_debug_configuration(self) -> None:
        """Test debug mode configuration"""
        config = ServerConfig(debug=True)
        assert config.debug is True

    def test_get_description_suffix(self) -> None:
        """Test description suffix generation"""
        # Test managed mode
        config = ServerConfig(tool_loading_mode=ToolLoadingMode.MANAGED)
        suffix = config.get_description_suffix()
        assert "MANAGED" in suffix

        # Test all mode
        config = ServerConfig(tool_loading_mode=ToolLoadingMode.ALL)
        suffix = config.get_description_suffix()
        assert "ALL" in suffix
