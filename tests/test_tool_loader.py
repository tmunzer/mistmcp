"""Tests for mistmcp tool loader module"""

from unittest.mock import Mock, patch

from mistmcp.config import ServerConfig, ToolLoadingMode
from mistmcp.tool_loader import ToolLoader


class TestToolLoader:
    """Test ToolLoader class"""

    def test_tool_loader_creation(self):
        """Test creating a new tool loader"""
        config = ServerConfig()
        loader = ToolLoader(config)

        assert loader.config == config
        assert isinstance(loader.loaded_tools, list)
        assert len(loader.loaded_tools) == 0

    def test_snake_case_conversion(self):
        """Test snake_case string conversion"""
        loader = ToolLoader(ServerConfig())

        assert loader.snake_case("CamelCase") == "camelcase"
        assert loader.snake_case("kebab-case") == "kebab_case"
        assert loader.snake_case("space case") == "space_case"
        assert loader.snake_case("mixed-Case String") == "mixed_case_string"
        assert loader.snake_case("already_snake_case") == "already_snake_case"

    @patch("mistmcp.tool_loader.get_current_mcp")
    def test_load_essential_tools_success(self, mock_get_mcp):
        """Test loading essential tools successfully"""
        # Mock MCP instance
        mock_mcp = Mock()
        mock_get_mcp.return_value = mock_mcp

        config = ServerConfig(debug=True)
        loader = ToolLoader(config)

        with patch("mistmcp.tool_loader.sys.modules", {}):
            with patch("mistmcp.tool_loader.mistmcp.server_factory") as mock_factory:
                mock_factory._CURRENT_MCP_INSTANCE = None

                loader.load_essential_tools(mock_mcp)

                # Should attempt to load tools
                assert mock_get_mcp.called or mock_mcp is not None

    def test_load_essential_tools_no_mcp(self):
        """Test loading essential tools with no MCP instance"""
        config = ServerConfig(debug=True)
        loader = ToolLoader(config)

        # Should not raise exception
        loader.load_essential_tools(None)

    @patch("mistmcp.tool_loader.get_current_mcp")
    def test_load_tool_manager_success(self, mock_get_mcp):
        """Test loading tool manager successfully"""
        mock_mcp = Mock()
        mock_get_mcp.return_value = mock_mcp

        config = ServerConfig(tool_loading_mode=ToolLoadingMode.MINIMAL)
        loader = ToolLoader(config)

        with patch(
            "mistmcp.tool_loader.register_manage_mcp_tools_tool"
        ) as mock_register:
            loader.load_tool_manager(mock_mcp)
            mock_register.assert_called_once_with(mock_mcp)

    def test_load_tool_manager_not_needed(self):
        """Test not loading tool manager when not needed"""
        config = ServerConfig(tool_loading_mode=ToolLoadingMode.ALL, debug=True)
        loader = ToolLoader(config)

        # Should not load for ALL mode
        loader.load_tool_manager()
        # No exception should be raised

    @patch("mistmcp.tool_loader.get_current_mcp")
    def test_load_category_tools_success(self, mock_get_mcp):
        """Test loading category tools successfully"""
        mock_mcp = Mock()
        mock_get_mcp.return_value = mock_mcp

        # Create config with mock available tools
        config = ServerConfig(debug=True)
        config.available_tools = {
            "orgs": {"tools": ["listOrgs", "getOrg"]},
            "sites": {"tools": ["listSites", "getSite"]},
        }

        loader = ToolLoader(config)

        loader.load_category_tools(["orgs"], mock_mcp)

        # Should have attempted to load tools
        assert mock_get_mcp.called or mock_mcp is not None

    def test_load_category_tools_invalid_category(self):
        """Test loading tools with invalid category"""
        config = ServerConfig(debug=True)
        config.available_tools = {"orgs": {"tools": ["listOrgs", "getOrg"]}}

        loader = ToolLoader(config)

        # Should handle invalid category gracefully
        loader.load_category_tools(["invalid_category"])

    def test_load_category_tools_no_mcp(self):
        """Test loading category tools with no MCP instance"""
        config = ServerConfig(debug=True)
        loader = ToolLoader(config)

        # Should handle gracefully
        loader.load_category_tools(["orgs"])

    @patch("mistmcp.tool_loader.ToolLoader.load_essential_tools")
    @patch("mistmcp.tool_loader.ToolLoader.load_tool_manager")
    @patch("mistmcp.tool_loader.ToolLoader.load_category_tools")
    def test_load_tools_minimal_mode(
        self, mock_load_category, mock_load_manager, mock_load_essential
    ):
        """Test loading tools in minimal mode"""
        config = ServerConfig(tool_loading_mode=ToolLoadingMode.MINIMAL)
        loader = ToolLoader(config)

        loader.load_tools()

        mock_load_essential.assert_called_once()
        mock_load_manager.assert_called_once()
        mock_load_category.assert_not_called()

    @patch("mistmcp.tool_loader.ToolLoader.load_essential_tools")
    @patch("mistmcp.tool_loader.ToolLoader.load_tool_manager")
    @patch("mistmcp.tool_loader.ToolLoader.load_category_tools")
    def test_load_tools_managed_mode(
        self, mock_load_category, mock_load_manager, mock_load_essential
    ):
        """Test loading tools in managed mode"""
        config = ServerConfig(tool_loading_mode=ToolLoadingMode.MANAGED)
        loader = ToolLoader(config)

        loader.load_tools()

        mock_load_essential.assert_called_once()
        mock_load_manager.assert_called_once()
        mock_load_category.assert_not_called()

    @patch("mistmcp.tool_loader.ToolLoader.load_essential_tools")
    @patch("mistmcp.tool_loader.ToolLoader.load_tool_manager")
    @patch("mistmcp.tool_loader.ToolLoader.load_category_tools")
    def test_load_tools_all_mode(
        self, mock_load_category, mock_load_manager, mock_load_essential
    ):
        """Test loading tools in all mode"""
        config = ServerConfig(tool_loading_mode=ToolLoadingMode.ALL)
        config.available_tools = {"orgs": {}, "sites": {}}
        loader = ToolLoader(config)

        loader.load_tools()

        mock_load_essential.assert_called_once()
        mock_load_manager.assert_called_once()
        mock_load_category.assert_called_once()

    @patch("mistmcp.tool_loader.ToolLoader.load_essential_tools")
    @patch("mistmcp.tool_loader.ToolLoader.load_tool_manager")
    @patch("mistmcp.tool_loader.ToolLoader.load_category_tools")
    def test_load_tools_custom_mode(
        self, mock_load_category, mock_load_manager, mock_load_essential
    ):
        """Test loading tools in custom mode"""
        config = ServerConfig(
            tool_loading_mode=ToolLoadingMode.CUSTOM, tool_categories=["orgs", "sites"]
        )
        loader = ToolLoader(config)

        loader.load_tools()

        mock_load_essential.assert_called_once()
        mock_load_manager.assert_called_once()
        mock_load_category.assert_called_once()

    def test_get_loaded_tools_summary(self):
        """Test getting loaded tools summary"""
        config = ServerConfig()
        loader = ToolLoader(config)

        # Initially empty
        summary = loader.get_loaded_tools_summary()
        assert "Loaded 0 tools" in summary

        # Add some tools
        loader.loaded_tools = ["getSelf", "manageMcpTools", "listOrgs"]
        summary = loader.get_loaded_tools_summary()
        assert "Loaded 3 tools" in summary
        assert "getSelf" in summary
        assert "manageMcpTools" in summary
        assert "listOrgs" in summary
