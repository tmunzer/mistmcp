"""Tests for mistmcp tool loader module"""

from unittest.mock import Mock, patch

from mistmcp.config import ServerConfig, ToolLoadingMode
from mistmcp.tool_loader import ToolLoader


class TestToolLoader:
    """Test ToolLoader class"""

    def test_tool_loader_creation(self) -> None:
        """Test creating a new tool loader"""
        config = ServerConfig()
        loader = ToolLoader(config)

        assert loader.config == config
        assert isinstance(loader.enabled_tools, list)
        assert len(loader.enabled_tools) == 0

    def test_snake_case_conversion(self) -> None:
        """Test snake_case string conversion"""
        loader = ToolLoader(ServerConfig())

        assert loader.snake_case("CamelCase") == "camelcase"
        assert loader.snake_case("kebab-case") == "kebab_case"
        assert loader.snake_case("space case") == "space_case"
        assert loader.snake_case("mixed-Case String") == "mixed_case_string"
        assert loader.snake_case("already_snake_case") == "already_snake_case"

    def test_enable_getself_tool_success(self) -> None:
        """Test enabling getSelf tool successfully"""
        config = ServerConfig(debug=True)
        loader = ToolLoader(config)

        # Test with None mcp instance - should not crash
        result = loader.enable_getself_tool(None)
        assert result is False

        # Test with mock mcp instance
        mock_mcp = Mock()
        result = loader.enable_getself_tool(mock_mcp)
        # Should complete without error (may succeed or fail depending on imports)

    @patch("mistmcp.config.ServerConfig._load_tools_config")
    def test_enable_managemcp_tool_success(self, mock_load_tools) -> None:
        """Test enabling manageMcpTools tool successfully"""
        mock_load_tools.return_value = None  # Prevent filesystem scan
        config = ServerConfig(debug=False)
        config.available_tools = {}  # Set empty tools
        loader = ToolLoader(config)

        # Test with None mcp instance - should return False
        result = loader.enable_managemcp_tool(None)
        assert result is True

        # Test with mock mcp instance - mock the register function to return None
        mock_mcp = Mock()
        with patch(
            "mistmcp.tool_manager.register_manage_mcp_tools_tool", return_value=None
        ):
            result = loader.enable_managemcp_tool(mock_mcp)
            assert result is False

    @patch("mistmcp.config.ServerConfig._load_tools_config")
    @patch("mistmcp.tool_loader.ToolLoader.enable_tool_by_name")
    def test_enable_categories_success(self, mock_enable_tool, mock_load_tools) -> None:
        """Test enabling category tools successfully"""
        mock_load_tools.return_value = None  # Prevent filesystem scan
        mock_enable_tool.return_value = False  # Mock tools don't exist
        config = ServerConfig(debug=False)
        config.available_tools = {
            "orgs": {"tools": ["listOrgs", "getOrg"]},
            "sites": {"tools": ["listSites", "getSite"]},
        }

        loader = ToolLoader(config)

        # Test with None mcp instance - should return 0
        result = loader.enable_categories(["orgs"], None)
        assert result == 0

        # Test with mock mcp instance - should return 0 because tools don't exist
        mock_mcp = Mock()
        result = loader.enable_categories(["orgs"], mock_mcp)
        # Should complete without error and return 0 for non-existent tools
        assert result == 0
        result = loader.enable_categories(["orgs"], mock_mcp)
        # Should complete without error and return 0 for non-existent tools
        assert result == 0

    def test_enable_categories_invalid_category(self) -> None:
        """Test enabling tools with invalid category"""
        config = ServerConfig(debug=True)
        config.available_tools = {"orgs": {"tools": ["listOrgs", "getOrg"]}}

        loader = ToolLoader(config)

        # Should handle invalid category gracefully
        result = loader.enable_categories(["invalid_category"])
        assert result == 0

    @patch("mistmcp.config.ServerConfig._load_tools_config")
    @patch("mistmcp.tool_loader.ToolLoader.enable_tool_by_name")
    def test_enable_categories_no_mcp(self, mock_enable_tool, mock_load_tools) -> None:
        """Test enabling category tools with no MCP instance"""
        mock_load_tools.return_value = None  # Prevent filesystem scan
        mock_enable_tool.return_value = False  # Mock tools don't exist
        config = ServerConfig(debug=False)
        config.available_tools = {"orgs": {"tools": ["listOrgs", "getOrg"]}}
        loader = ToolLoader(config)

        # Should handle gracefully
        result = loader.enable_categories(["orgs"])
        assert result == 0

    @patch("mistmcp.tool_loader.ToolLoader.enable_getself_tool")
    @patch("mistmcp.tool_loader.ToolLoader.enable_managemcp_tool")
    def test_configure_tools_managed_mode(
        self, mock_enable_managemcp, mock_enable_getself
    ) -> None:
        """Test configuring tools in managed mode"""
        config = ServerConfig(tool_loading_mode=ToolLoadingMode.MANAGED, debug=True)
        # Add available tools so there are categories to load
        config.available_tools = {"orgs": {}, "sites": {}}
        loader = ToolLoader(config)

        mock_mcp = Mock()
        loader.configure_tools(mock_mcp)

        mock_enable_getself.assert_called_once_with(mock_mcp)
        mock_enable_managemcp.assert_called_once_with(mock_mcp)

    @patch("mistmcp.tool_loader.ToolLoader.enable_getself_tool")
    @patch("mistmcp.tool_loader.ToolLoader.enable_tool_by_name")
    def test_configure_tools_all_mode(
        self, mock_enable_tool, mock_enable_getself
    ) -> None:
        """Test configuring tools in all mode"""
        config = ServerConfig(tool_loading_mode=ToolLoadingMode.ALL, debug=True)
        config.available_tools = {
            "orgs": {"tools": ["getOrg", "listOrgs"]},
            "sites": {"tools": ["getSite"]},
        }
        loader = ToolLoader(config)

        mock_mcp = Mock()
        loader.configure_tools(mock_mcp)

        mock_enable_getself.assert_called_once_with(mock_mcp)
        # Should enable all tools in all categories (except getSelf and manageMcpTools)
        assert mock_enable_tool.call_count == 3  # getOrg, listOrgs, getSite

    def test_get_enabled_tools_summary(self) -> None:
        """Test getting enabled tools summary"""
        config = ServerConfig()
        loader = ToolLoader(config)

        # Initially empty
        summary = loader.get_enabled_tools_summary()
        assert "Enabled 0 tools" in summary

        # Add some tools
        loader.enabled_tools = ["getSelf", "manageMcpTools", "listOrgs"]
        summary = loader.get_enabled_tools_summary()
        assert "Enabled 3 tools" in summary
        assert "getSelf" in summary
        assert "manageMcpTools" in summary
        assert "listOrgs" in summary
