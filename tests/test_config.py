"""Tests for mistmcp configuration module"""

from io import StringIO
from unittest.mock import patch

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
        assert config.tool_loading_mode == ToolLoadingMode.ALL
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


class TestServerConfigToolLoading:
    """Test suite for ServerConfig tool loading methods."""

    def test_load_tools_config_success_from_helper_without_debug(self) -> None:
        """Test successful loading from tool_helper.py without debug output."""
        # Arrange
        mock_tools = {
            "orgs": {
                "description": "Organisation tools",
                "tools": ["getOrg", "searchOrgSites"],
            },
            "devices": {
                "description": "Device management tools",
                "tools": ["searchOrgDevices", "listOrgDevicesSummary"],
            },
        }

        with patch("mistmcp.tool_helper.TOOLS", mock_tools):
            # Act
            config = ServerConfig(debug=False)

            # Assert
            assert config.available_tools == mock_tools
            assert len(config.available_tools) == 2
            assert "orgs" in config.available_tools
            assert "devices" in config.available_tools

    def test_load_tools_config_success_from_helper_with_debug(self) -> None:
        """Test successful loading from tool_helper.py with debug output."""
        # Arrange
        mock_tools = {
            "orgs": {
                "description": "Organisation tools",
                "tools": ["getOrg", "searchOrgSites"],
            }
        }

        # Capture stderr to verify debug output
        captured_output = StringIO()

        with (
            patch("mistmcp.tool_helper.TOOLS", mock_tools),
            patch("sys.stderr", captured_output),
        ):
            # Act
            config = ServerConfig(debug=True)

            # Assert
            assert config.available_tools == mock_tools

            # Verify debug output contains expected messages
            debug_output = captured_output.getvalue()
            assert "Loaded 1 tool categories from tool_helper.py" in debug_output
            assert "orgs: 2 tools" in debug_output

    def test_tool_loading_integration_with_get_tools_to_load(self) -> None:
        """Test integration between tool loading and get_tools_to_load method."""
        # Arrange
        mock_tools = {
            "orgs": {"tools": ["getOrg"]},
            "sites": {"tools": ["getSiteInfo"]},
        }

        with patch("mistmcp.tool_helper.TOOLS", mock_tools):
            # Test MANAGED mode
            config_managed = ServerConfig(tool_loading_mode=ToolLoadingMode.MANAGED)
            tools_managed = config_managed.get_tools_to_load()
            assert tools_managed == []  # Managed mode loads tools on demand

            # Test ALL mode
            config_all = ServerConfig(tool_loading_mode=ToolLoadingMode.ALL)
            tools_all = config_all.get_tools_to_load()
            assert set(tools_all) == {"orgs", "sites"}  # All mode loads everything

    def test_config_uses_available_tools_correctly(self) -> None:
        """Test that the config uses the loaded tools correctly."""
        # Arrange
        mock_tools = {
            "category1": {"tools": ["tool1", "tool2"]},
            "category2": {"tools": ["tool3"]},
        }

        with patch("mistmcp.tool_helper.TOOLS", mock_tools):
            # Act
            config = ServerConfig(tool_loading_mode=ToolLoadingMode.ALL)

            # Assert
            assert len(config.available_tools) == 2
            assert config.available_tools["category1"]["tools"] == ["tool1", "tool2"]
            assert config.available_tools["category2"]["tools"] == ["tool3"]

            # Test get_tools_to_load returns all categories
            tools_to_load = config.get_tools_to_load()
            assert set(tools_to_load) == {"category1", "category2"}

    def test_debug_mode_affects_tool_loading(self) -> None:
        """Test that debug mode is correctly passed through to tool loading."""
        # Arrange
        mock_tools = {"debug_test": {"tools": ["debug_tool"]}}
        captured_output = StringIO()

        with (
            patch("mistmcp.tool_helper.TOOLS", mock_tools),
            patch("sys.stderr", captured_output),
        ):
            # Act - Test with debug enabled
            ServerConfig(debug=True)

            # Assert
            debug_output = captured_output.getvalue()
            assert "Loaded 1 tool categories from tool_helper.py" in debug_output
            assert "debug_test: 1 tools" in debug_output

            # Act - Test with debug disabled (should not produce output)
            captured_output_no_debug = StringIO()
            with patch("sys.stderr", captured_output_no_debug):
                ServerConfig(debug=False)

            # Assert
            no_debug_output = captured_output_no_debug.getvalue()
            assert no_debug_output == ""
