"""Tests for mistmcp configuration module"""

import pytest

from mistmcp.config import ServerConfig, ToolLoadingMode


class TestToolLoadingMode:
    """Test ToolLoadingMode enum"""

    def test_enum_values(self) -> None:
        """Test that all enum values are correct"""
        assert ToolLoadingMode.MANAGED.value == "managed"
        assert ToolLoadingMode.ALL.value == "all"
        assert ToolLoadingMode.CUSTOM.value == "custom"

    def test_enum_creation_from_string(self) -> None:
        """Test creating enum from string values"""
        assert ToolLoadingMode("managed") == ToolLoadingMode.MANAGED
        assert ToolLoadingMode("all") == ToolLoadingMode.ALL
        assert ToolLoadingMode("custom") == ToolLoadingMode.CUSTOM

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
        assert config.get_tools_to_load() == []
        assert config.should_load_tool_manager() is True

    def test_all_configuration(self) -> None:
        """Test all mode configuration"""
        config = ServerConfig(tool_loading_mode=ToolLoadingMode.ALL)
        assert config.tool_loading_mode == ToolLoadingMode.ALL
        assert config.should_load_tool_manager() is False
        # get_tools_to_load() returns all available tools
        tools = config.get_tools_to_load()
        assert isinstance(tools, list)

    def test_custom_configuration(self) -> None:
        """Test custom mode configuration"""
        categories = ["orgs", "sites"]
        config = ServerConfig(
            tool_loading_mode=ToolLoadingMode.CUSTOM, tool_categories=categories
        )
        assert config.tool_loading_mode == ToolLoadingMode.CUSTOM
        assert config.tool_categories == categories
        assert config.should_load_tool_manager() is True

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
        assert "manageMcpTools" in suffix

        # Test all mode
        config = ServerConfig(tool_loading_mode=ToolLoadingMode.ALL)
        suffix = config.get_description_suffix()
        assert "ALL" in suffix

        # Test custom mode
        config = ServerConfig(
            tool_loading_mode=ToolLoadingMode.CUSTOM, tool_categories=["orgs", "sites"]
        )
        suffix = config.get_description_suffix()
        assert "CUSTOM" in suffix
        assert "orgs, sites" in suffix

    def test_should_load_tool_manager(self) -> None:
        """Test tool manager loading logic"""
        # Should load for minimal, managed, custom
        for mode in [
            ToolLoadingMode.MANAGED,
            ToolLoadingMode.CUSTOM,
        ]:
            config = ServerConfig(tool_loading_mode=mode)
            assert config.should_load_tool_manager() is True

        # Should not load for all mode
        config = ServerConfig(tool_loading_mode=ToolLoadingMode.ALL)
        assert config.should_load_tool_manager() is False

    def test_custom_mode_with_invalid_categories(self) -> None:
        """Test custom mode with invalid tool categories"""
        config = ServerConfig(
            tool_loading_mode=ToolLoadingMode.CUSTOM,
            tool_categories=["invalid_category", "another_invalid"],
        )
        # Should handle invalid categories gracefully
        tools = config.get_tools_to_load()
        assert isinstance(tools, list)
        # Invalid categories should be filtered out
        assert "invalid_category" not in tools
        assert "another_invalid" not in tools
