"""Tests for mistmcp session_aware_server module"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from mistmcp.config import ServerConfig, ToolLoadingMode
from mistmcp.session_aware_server import (
    SessionAwareFastMCP,
    create_session_aware_mcp_server,
)


class TestSessionAwareFastMCP:
    """Test SessionAwareFastMCP class"""

    @pytest.fixture
    def mock_session(self):
        """Create a mock session for testing"""
        session = Mock()
        session.session_id = "test_session"
        session.enabled_tools = {"getSelf", "manageMcpTools", "orgs_getOrgs"}
        session.enabled_categories = {"orgs"}
        session.created_at = Mock()
        session.created_at.isoformat.return_value = "2025-01-01T00:00:00"
        session.last_activity = Mock()
        session.last_activity.isoformat.return_value = "2025-01-01T01:00:00"
        return session

    @pytest.fixture
    def server_config(self):
        """Create a test server configuration"""
        return ServerConfig(
            tool_loading_mode=ToolLoadingMode.MANAGED, tool_categories=[], debug=False
        )

    @pytest.fixture
    def session_aware_server(self, server_config):
        """Create a SessionAwareFastMCP instance for testing"""
        return SessionAwareFastMCP(config=server_config, transport_mode="stdio")

    def test_init(self, server_config):
        """Test SessionAwareFastMCP initialization"""
        server = SessionAwareFastMCP(config=server_config, transport_mode="http")
        assert server.config == server_config
        assert server.transport_mode == "http"

    @patch("mistmcp.session_aware_server.get_current_session")
    async def test_get_tools_with_session(
        self, mock_get_session, session_aware_server, mock_session
    ):
        """Test get_tools with valid session"""
        mock_get_session.return_value = mock_session

        # Mock the parent get_tools method
        all_tools = {
            "getSelf": Mock(),
            "manageMcpTools": Mock(),
            "orgs_getOrgs": Mock(),
            "sites_getSites": Mock(),  # Not in enabled_tools
        }

        with patch.object(SessionAwareFastMCP, "__bases__", (AsyncMock,)):
            with patch.object(
                super(SessionAwareFastMCP, session_aware_server),
                "get_tools",
                return_value=all_tools,
            ):
                filtered_tools = await session_aware_server.get_tools()

        # Should only return enabled tools
        assert len(filtered_tools) == 3
        assert "getSelf" in filtered_tools
        assert "manageMcpTools" in filtered_tools
        assert "orgs_getOrgs" in filtered_tools
        assert "sites_getSites" not in filtered_tools

    @patch("mistmcp.session_aware_server.get_current_session")
    @patch("mistmcp.session_aware_server.session_manager")
    async def test_get_tools_without_session(
        self, mock_session_manager, mock_get_session, session_aware_server
    ):
        """Test get_tools when session context is not available"""
        mock_get_session.side_effect = Exception("No session context")
        mock_session_manager.default_enabled_tools = {"getSelf", "manageMcpTools"}

        all_tools = {
            "getSelf": Mock(),
            "manageMcpTools": Mock(),
            "orgs_getOrgs": Mock(),
        }

        with patch.object(SessionAwareFastMCP, "__bases__", (AsyncMock,)):
            with patch.object(
                super(SessionAwareFastMCP, session_aware_server),
                "get_tools",
                return_value=all_tools,
            ):
                filtered_tools = await session_aware_server.get_tools()

        # Should only return default tools
        assert len(filtered_tools) == 2
        assert "getSelf" in filtered_tools
        assert "manageMcpTools" in filtered_tools
        assert "orgs_getOrgs" not in filtered_tools

    @patch("mistmcp.session_aware_server.get_http_request")
    @patch("mistmcp.session_aware_server.get_current_session")
    async def test_get_tools_http_mode_all(
        self, mock_get_session, mock_get_request, mock_session
    ):
        """Test get_tools in HTTP mode with 'all' parameter"""
        mock_session.enabled_tools = {"getSelf"}
        mock_get_session.return_value = mock_session

        # Mock HTTP request with mode=all
        mock_request = Mock()
        mock_request.query_params.get.return_value = "all"
        mock_get_request.return_value = mock_request

        server = SessionAwareFastMCP(
            config=ServerConfig(ToolLoadingMode.MANAGED), transport_mode="http"
        )

        all_tools = {
            "getSelf": Mock(),
            "manageMcpTools": Mock(),
            "orgs_getOrgs": Mock(),
        }

        with patch.object(SessionAwareFastMCP, "__bases__", (AsyncMock,)):
            with patch.object(
                super(SessionAwareFastMCP, server), "get_tools", return_value=all_tools
            ):
                filtered_tools = await server.get_tools()

        # Should return all tools when mode=all
        assert len(filtered_tools) == 3
        assert "getSelf" in filtered_tools
        assert "manageMcpTools" in filtered_tools
        assert "orgs_getOrgs" in filtered_tools

    @patch("mistmcp.session_aware_server.get_current_session")
    async def test_get_tool_enabled(
        self, mock_get_session, session_aware_server, mock_session
    ):
        """Test get_tool for an enabled tool"""
        mock_get_session.return_value = mock_session
        mock_tool = Mock()

        with patch.object(SessionAwareFastMCP, "__bases__", (AsyncMock,)):
            with patch.object(
                super(SessionAwareFastMCP, session_aware_server),
                "get_tool",
                return_value=mock_tool,
            ):
                result = await session_aware_server.get_tool("getSelf")

        assert result == mock_tool

    @patch("mistmcp.session_aware_server.get_current_session")
    async def test_get_tool_disabled(
        self, mock_get_session, session_aware_server, mock_session
    ):
        """Test get_tool for a disabled tool"""
        mock_get_session.return_value = mock_session

        with pytest.raises(Exception) as exc_info:
            await session_aware_server.get_tool("sites_getSites")

        assert "not enabled for your session" in str(exc_info.value)

    @patch("mistmcp.session_aware_server.get_current_session")
    @patch("mistmcp.session_aware_server.session_manager")
    async def test_get_tool_no_session(
        self, mock_session_manager, mock_get_session, session_aware_server
    ):
        """Test get_tool when session context is not available"""
        mock_get_session.side_effect = Exception("No session context")
        mock_session_manager.default_enabled_tools = {"getSelf", "manageMcpTools"}
        mock_tool = Mock()

        with patch.object(SessionAwareFastMCP, "__bases__", (AsyncMock,)):
            with patch.object(
                super(SessionAwareFastMCP, session_aware_server),
                "get_tool",
                return_value=mock_tool,
            ):
                result = await session_aware_server.get_tool("getSelf")

        assert result == mock_tool

    @patch("mistmcp.session_aware_server.get_current_session")
    async def test_get_session_info_success(
        self, mock_get_session, session_aware_server, mock_session
    ):
        """Test get_session_info with valid session"""
        mock_get_session.return_value = mock_session

        result = await session_aware_server.get_session_info()

        assert result["session_id"] == "test_session"
        assert result["enabled_tools"] == ["getSelf", "manageMcpTools", "orgs_getOrgs"]
        assert result["enabled_categories"] == ["orgs"]
        assert result["created_at"] == "2025-01-01T00:00:00"
        assert result["last_activity"] == "2025-01-01T01:00:00"

    @patch("mistmcp.session_aware_server.get_current_session")
    async def test_get_session_info_error(self, mock_get_session, session_aware_server):
        """Test get_session_info when session context fails"""
        mock_get_session.side_effect = Exception("Session error")

        result = await session_aware_server.get_session_info()

        assert "error" in result
        assert "Session error" in result["error"]

    @patch("mistmcp.session_aware_server.session_manager")
    async def test_list_all_sessions(
        self, mock_session_manager, session_aware_server, mock_session
    ):
        """Test list_all_sessions method"""
        # Mock session manager with test sessions
        mock_session2 = Mock()
        mock_session2.enabled_tools = {"getSelf"}
        mock_session2.enabled_categories = set()
        mock_session2.created_at.isoformat.return_value = "2025-01-01T02:00:00"
        mock_session2.last_activity.isoformat.return_value = "2025-01-01T03:00:00"
        mock_session2.is_expired.return_value = False

        mock_session.is_expired.return_value = False

        mock_session_manager.get_all_sessions.return_value = {
            "session1": mock_session,
            "session2": mock_session2,
        }
        mock_session_manager.session_timeout_minutes = 60
        mock_session_manager.default_enabled_tools = {"getSelf", "manageMcpTools"}

        result = await session_aware_server.list_all_sessions()

        assert result["total_sessions"] == 2
        assert "session1" in result["sessions"]
        assert "session2" in result["sessions"]
        assert result["default_tools"] == ["getSelf", "manageMcpTools"]

    async def test_mcp_list_tools(self, session_aware_server):
        """Test _mcp_list_tools method"""
        mock_tools = [Mock(), Mock()]

        with patch.object(SessionAwareFastMCP, "__bases__", (AsyncMock,)):
            with patch.object(
                super(SessionAwareFastMCP, session_aware_server),
                "_mcp_list_tools",
                return_value=mock_tools,
            ):
                result = await session_aware_server._mcp_list_tools()

        assert result == mock_tools


class TestCreateSessionAwareMcpServer:
    """Test create_session_aware_mcp_server function"""

    @patch("mistmcp.session_aware_server.get_mode_instructions")
    def test_create_server_stdio(self, mock_get_instructions):
        """Test creating server with stdio transport"""
        mock_get_instructions.return_value = "Test mode instructions"

        config = ServerConfig(
            tool_loading_mode=ToolLoadingMode.MINIMAL, tool_categories=[], debug=False
        )

        server = create_session_aware_mcp_server(config, "stdio")

        assert isinstance(server, SessionAwareFastMCP)
        assert server.config == config
        assert server.transport_mode == "stdio"
        mock_get_instructions.assert_called_once_with(config)

    @patch("mistmcp.session_aware_server.get_mode_instructions")
    def test_create_server_http(self, mock_get_instructions):
        """Test creating server with HTTP transport"""
        mock_get_instructions.return_value = "Test mode instructions"

        config = ServerConfig(
            tool_loading_mode=ToolLoadingMode.ALL,
            tool_categories=["orgs", "sites"],
            debug=True,
        )

        server = create_session_aware_mcp_server(config, "http")

        assert isinstance(server, SessionAwareFastMCP)
        assert server.config == config
        assert server.transport_mode == "http"
        mock_get_instructions.assert_called_once_with(config)
