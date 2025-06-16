"""Simple tests for mistmcp tool loader module"""

from mistmcp.config import ServerConfig, ToolLoadingMode
from mistmcp.tool_loader import ToolLoader


class TestToolLoaderSimple:
    """Simple test ToolLoader class"""

    def test_tool_loader_creation(self) -> None:
        """Test creating a new tool loader"""
        config = ServerConfig()
        loader = ToolLoader(config)

        assert loader.config == config
        assert isinstance(loader.loaded_tools, list)
        assert len(loader.loaded_tools) == 0

    def test_snake_case_conversion(self) -> None:
        """Test snake_case string conversion"""
        loader = ToolLoader(ServerConfig())

        assert loader.snake_case("CamelCase") == "camelcase"
        assert loader.snake_case("kebab-case") == "kebab_case"
        assert loader.snake_case("space case") == "space_case"
        assert loader.snake_case("mixed-Case String") == "mixed_case_string"
        assert loader.snake_case("already_snake_case") == "already_snake_case"

    def test_load_essential_tools_no_mcp(self) -> None:
        """Test loading essential tools with no MCP instance"""
        config = ServerConfig(debug=True)
        loader = ToolLoader(config)

        # Should not raise exception when mcp is None
        loader.load_essential_tools(None)

    def test_load_tool_manager_not_needed(self) -> None:
        """Test not loading tool manager when not needed"""
        config = ServerConfig(tool_loading_mode=ToolLoadingMode.ALL, debug=True)
        loader = ToolLoader(config)

        # Should not load for ALL mode
        loader.load_tool_manager()
        # No exception should be raised

    def test_get_loaded_tools_summary(self) -> None:
        """Test getting loaded tools summary"""
        config = ServerConfig()
        loader = ToolLoader(config)

        summary = loader.get_loaded_tools_summary()
        assert isinstance(summary, str)
        assert "Loaded 0 tools: " in summary
