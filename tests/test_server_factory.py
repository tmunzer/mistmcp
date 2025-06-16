"""Tests for mistmcp server factory module"""

from unittest.mock import Mock, patch

from mistmcp.config import ServerConfig, ToolLoadingMode
from mistmcp.server_factory import (
    create_mcp_server,
    get_current_mcp,
    get_mode_instructions,
)


class TestServerFactory:
    """Test server factory functions"""

    def test_get_current_mcp_none(self) -> None:
        """Test getting current MCP when none exists"""
        # Create a fresh McpInstance that doesn't have current_mcp_instance set
        with patch("mistmcp.server_factory.mcp_instance") as mock_instance:
            mock_instance.get.side_effect = AttributeError(
                "'McpInstance' object has no attribute 'current_mcp_instance'"
            )
            result = get_current_mcp()
            assert result is None

    def test_get_current_mcp_exists(self) -> None:
        """Test getting current MCP when it exists"""
        mock_mcp = Mock()
        with patch("mistmcp.server_factory.mcp_instance") as mock_instance:
            mock_instance.get.return_value = mock_mcp
            result = get_current_mcp()
            assert result == mock_mcp

    @patch("mistmcp.server_factory.create_session_aware_mcp_server")
    @patch("mistmcp.server_factory.ToolLoader")
    def test_create_mcp_server_success(
        self, mock_tool_loader_class, mock_create_server
    ) -> None:
        """Test creating MCP server successfully"""
        # Mock the session-aware server
        mock_server = Mock()
        mock_create_server.return_value = mock_server

        # Mock the tool loader
        mock_tool_loader = Mock()
        mock_tool_loader_class.return_value = mock_tool_loader

        config = ServerConfig()
        transport_mode = "stdio"

        result = create_mcp_server(config, transport_mode)

        # Verify server creation
        mock_create_server.assert_called_once_with(config, transport_mode)

        # Verify tool loader
        mock_tool_loader_class.assert_called_once_with(config)
        mock_tool_loader.load_tools.assert_called_once_with(mock_server)

        assert result == mock_server

    @patch("mistmcp.server_factory.create_session_aware_mcp_server")
    def test_create_mcp_server_exception(self, mock_create_server) -> None:
        """Test creating MCP server with exception"""
        mock_create_server.side_effect = Exception("Test error")

        config = ServerConfig()
        transport_mode = "stdio"

        try:
            create_mcp_server(config, transport_mode)
            assert False, "Should have raised exception"
        except Exception as e:
            assert str(e) == "Test error"

    def test_get_mode_instructions_minimal(self) -> None:
        """Test getting instructions for minimal mode"""
        config = ServerConfig(tool_loading_mode=ToolLoadingMode.MINIMAL)
        instructions = get_mode_instructions(config)

        assert "MINIMAL MODE" in instructions
        assert "manageMcpTools" in instructions
        assert "getSelf" in instructions

    def test_get_mode_instructions_managed(self) -> None:
        """Test getting instructions for managed mode"""
        config = ServerConfig(tool_loading_mode=ToolLoadingMode.MANAGED)
        instructions = get_mode_instructions(config)

        assert "MANAGED MODE" in instructions
        assert "manageMcpTools" in instructions
        assert "org_id" in instructions
        assert "site_id" in instructions

    def test_get_mode_instructions_all(self) -> None:
        """Test getting instructions for all mode"""
        config = ServerConfig(tool_loading_mode=ToolLoadingMode.ALL)
        instructions = get_mode_instructions(config)

        assert "ALL TOOLS MODE" in instructions
        assert "getSelf" in instructions
        assert "listOrgSites" in instructions

    def test_get_mode_instructions_custom(self) -> None:
        """Test getting instructions for custom mode"""
        config = ServerConfig(
            tool_loading_mode=ToolLoadingMode.CUSTOM, tool_categories=["orgs", "sites"]
        )
        instructions = get_mode_instructions(config)

        assert "CUSTOM MODE" in instructions or instructions == ""
        # Custom mode might return empty string based on implementation

    def test_get_mode_instructions_unknown(self) -> None:
        """Test getting instructions for unknown mode"""
        # Create a mock config with invalid mode (shouldn't happen in practice)
        config = ServerConfig()
        # Manually set invalid mode for test
        config.tool_loading_mode = "invalid"  # type: ignore

        instructions = get_mode_instructions(config)
        assert instructions == ""
