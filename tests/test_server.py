"""Tests for mistmcp server module"""

from unittest.mock import Mock, patch

from mistmcp.config import ServerConfig
from mistmcp.server import create_mcp_server, get_mcp


class TestServer:
    """Test server functions"""

    def test_get_mcp_none(self) -> None:
        """Test getting MCP when none exists"""
        import mistmcp.server

        original = mistmcp.server._mcp_instance
        mistmcp.server._mcp_instance = None
        result = get_mcp()
        assert result is None
        mistmcp.server._mcp_instance = original

    def test_get_mcp_exists(self) -> None:
        """Test getting MCP when it exists"""
        import mistmcp.server

        mock_mcp = Mock()
        original = mistmcp.server._mcp_instance
        mistmcp.server._mcp_instance = mock_mcp
        result = get_mcp()
        assert result == mock_mcp
        mistmcp.server._mcp_instance = original

    @patch("mistmcp.server.FastMCP")
    @patch("mistmcp.server._load_tools")
    def test_create_mcp_server_success(
        self, mock_load_tools, mock_fastmcp_class
    ) -> None:
        """Test creating MCP server successfully"""
        mock_server = Mock()
        mock_fastmcp_class.return_value = mock_server
        mock_load_tools.return_value = ["getSelf", "getOrg"]

        config = ServerConfig(transport_mode="stdio")
        result = create_mcp_server(config)

        mock_fastmcp_class.assert_called_once()
        mock_load_tools.assert_called_once_with(config)
        assert result == mock_server

    @patch("mistmcp.server.FastMCP")
    @patch("mistmcp.server._load_tools")
    def test_create_mcp_server_with_debug(
        self, mock_load_tools, mock_fastmcp_class, capsys
    ) -> None:
        """Test creating MCP server with debug output"""
        mock_server = Mock()
        mock_fastmcp_class.return_value = mock_server
        mock_load_tools.return_value = ["getSelf", "getOrg"]

        config = ServerConfig(transport_mode="stdio", debug=True)
        result = create_mcp_server(config)

        assert result == mock_server
        captured = capsys.readouterr()
        assert "MCP Server ready with 2 tools" in captured.err

    @patch("mistmcp.server.FastMCP")
    def test_create_mcp_server_sets_global_instance(self, mock_fastmcp_class) -> None:
        """Test that create_mcp_server sets the global instance"""
        import mistmcp.server

        mock_server = Mock()
        mock_fastmcp_class.return_value = mock_server

        with patch("mistmcp.server._load_tools", return_value=[]):
            config = ServerConfig()
            create_mcp_server(config)

            assert mistmcp.server._mcp_instance == mock_server
