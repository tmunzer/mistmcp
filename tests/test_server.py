"""Tests for mistmcp server module"""

from unittest.mock import patch

from fastmcp import FastMCP

from mistmcp.config import ServerConfig
from mistmcp.server import create_mcp_server, mcp


class TestMcpInstance:
    """Test the module-level mcp instance"""

    def test_mcp_is_fastmcp_instance(self) -> None:
        """Test that mcp is a FastMCP instance"""
        assert isinstance(mcp, FastMCP)

    def test_mcp_is_singleton(self) -> None:
        """Test that importing mcp multiple times gives the same instance"""
        from mistmcp.server import mcp as mcp2

        assert mcp is mcp2


class TestCreateMcpServer:
    """Test create_mcp_server function"""

    @patch("mistmcp.server._load_tools")
    def test_create_mcp_server_returns_mcp(self, mock_load_tools) -> None:
        """Test that create_mcp_server returns the module-level mcp instance"""
        mock_load_tools.return_value = ["getSelf", "getOrg"]

        config = ServerConfig(transport_mode="stdio")
        result = create_mcp_server(config)

        mock_load_tools.assert_called_once_with(config)
        assert result is mcp

    @patch("mistmcp.server._load_tools")
    def test_create_mcp_server_with_debug(self, mock_load_tools, capsys) -> None:
        """Test creating MCP server with debug output"""
        mock_load_tools.return_value = ["getSelf", "getOrg"]

        config = ServerConfig(transport_mode="stdio", debug=True)
        create_mcp_server(config)

        captured = capsys.readouterr()
        assert "MCP Server ready with 2 tools" in captured.err

    @patch("mistmcp.server._load_tools")
    def test_create_mcp_server_without_debug(self, mock_load_tools, capsys) -> None:
        """Test that no debug output is emitted without debug mode"""
        mock_load_tools.return_value = []

        config = ServerConfig(transport_mode="stdio", debug=False)
        create_mcp_server(config)

        captured = capsys.readouterr()
        assert captured.err == ""
