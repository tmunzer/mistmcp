"""Tests for mistmcp session_middleware module"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from mistmcp.session_middleware import (
    SessionAwareToolHandler,
    create_session_aware_mcp_server,
)


class TestSessionAwareToolHandler:
    """Test SessionAwareToolHandler class"""

    @pytest.fixture
    def mock_mcp_instance(self):
        """Create a mock MCP instance"""
        mcp = Mock()
        mcp._tools = {
            "getSelf": Mock(),
            "manageMcpTools": Mock(),
            "orgs_getOrgs": Mock(),
            "sites_getSites": Mock(),
        }
        return mcp

    @pytest.fixture
    def tool_handler(self, mock_mcp_instance):
        """Create a SessionAwareToolHandler instance"""
        return SessionAwareToolHandler(mock_mcp_instance)

    def test_init(self, mock_mcp_instance):
        """Test SessionAwareToolHandler initialization"""
        handler = SessionAwareToolHandler(mock_mcp_instance)
        assert handler.mcp_instance == mock_mcp_instance
        assert handler.original_tool_handlers == {}

    @patch("mistmcp.session_middleware.is_tool_enabled_for_current_session")
    @pytest.mark.asyncio
    async def test_wrap_tool_enabled(self, mock_is_enabled, tool_handler):
        """Test wrapping a tool that is enabled for the session"""
        mock_is_enabled.return_value = True

        # Create a mock original handler
        original_handler = AsyncMock(return_value="test_result")

        # Wrap the handler
        wrapped_handler = tool_handler.wrap_tool_for_session_checking(
            "test_tool", original_handler
        )

        # Call the wrapped handler
        result = await wrapped_handler("arg1", kwarg1="value1")

        # Verify behavior
        mock_is_enabled.assert_called_once_with("test_tool")
        original_handler.assert_called_once_with("arg1", kwarg1="value1")
        assert result == "test_result"

    @patch("mistmcp.session_middleware.is_tool_enabled_for_current_session")
    @pytest.mark.asyncio
    async def test_wrap_tool_disabled(self, mock_is_enabled, tool_handler):
        """Test wrapping a tool that is disabled for the session"""
        mock_is_enabled.return_value = False

        # Create a mock original handler
        original_handler = AsyncMock()

        # Wrap the handler
        wrapped_handler = tool_handler.wrap_tool_for_session_checking(
            "test_tool", original_handler
        )

        # Call the wrapped handler and expect an error
        with pytest.raises(Exception) as exc_info:
            await wrapped_handler("arg1", kwarg1="value1")

        # Verify the error details
        error = exc_info.value
        assert "not enabled for your session" in str(error)

        # Verify the original handler was not called
        mock_is_enabled.assert_called_once_with("test_tool")
        original_handler.assert_not_called()

    def test_apply_session_middleware(self, tool_handler, mock_mcp_instance):
        """Test applying session middleware to tools"""
        # Mock tool objects with handlers
        for tool_name, tool_obj in mock_mcp_instance._tools.items():
            tool_obj.handler = AsyncMock()

        # Apply middleware
        tool_handler.apply_session_middleware()

        # Verify essential tools are not wrapped
        assert "getSelf" not in tool_handler.original_tool_handlers
        assert "manageMcpTools" not in tool_handler.original_tool_handlers

        # Verify other tools are wrapped
        assert "orgs_getOrgs" in tool_handler.original_tool_handlers
        assert "sites_getSites" in tool_handler.original_tool_handlers

        # Verify handlers have been replaced
        orgs_tool = mock_mcp_instance._tools["orgs_getOrgs"]
        sites_tool = mock_mcp_instance._tools["sites_getSites"]

        # The handler should have been replaced with wrapped version
        assert orgs_tool.handler != tool_handler.original_tool_handlers["orgs_getOrgs"]
        assert (
            sites_tool.handler != tool_handler.original_tool_handlers["sites_getSites"]
        )

    def test_apply_session_middleware_no_handler_attr(
        self, tool_handler, mock_mcp_instance
    ):
        """Test applying middleware when tools don't have handler attribute"""
        # Remove handler attributes
        for tool_obj in mock_mcp_instance._tools.values():
            if hasattr(tool_obj, "handler"):
                delattr(tool_obj, "handler")

        # This should not raise an error
        tool_handler.apply_session_middleware()

        # This is expected behavior - tools without handlers are skipped

    @patch("mistmcp.session_middleware.session_manager")
    def test_get_available_tools_with_session(
        self, mock_session_manager, tool_handler, mock_mcp_instance
    ):
        """Test getting available tools when session exists"""
        # Mock session with specific enabled tools
        mock_session = Mock()
        mock_session.enabled_tools = {"getSelf", "manageMcpTools", "orgs_getOrgs"}
        mock_session_manager.get_or_create_session.return_value = mock_session

        # Get available tools
        available_tools = tool_handler.get_available_tools_for_session()

        # Verify only enabled tools are returned
        assert len(available_tools) == 3
        assert "getSelf" in available_tools
        assert "manageMcpTools" in available_tools
        assert "orgs_getOrgs" in available_tools
        assert "sites_getSites" not in available_tools

    @patch("mistmcp.session_middleware.session_manager")
    def test_get_available_tools_no_session(
        self, mock_session_manager, tool_handler, mock_mcp_instance
    ):
        """Test getting available tools when no session exists"""
        # Mock no session available
        mock_session_manager.get_or_create_session.return_value = None
        mock_session_manager.default_enabled_tools = {"getSelf", "manageMcpTools"}

        # Get available tools
        available_tools = tool_handler.get_available_tools_for_session()

        # Verify only default tools are returned
        assert len(available_tools) == 2
        assert "getSelf" in available_tools
        assert "manageMcpTools" in available_tools
        assert "orgs_getOrgs" not in available_tools
        assert "sites_getSites" not in available_tools

    def test_get_available_tools_no_tools_attr(self, tool_handler, mock_mcp_instance):
        """Test getting available tools when MCP instance has no _tools attribute"""
        # Remove _tools attribute
        delattr(mock_mcp_instance, "_tools")

        with patch(
            "mistmcp.session_middleware.session_manager"
        ) as mock_session_manager:
            mock_session = Mock()
            mock_session.enabled_tools = {"getSelf"}
            mock_session_manager.get_or_create_session.return_value = mock_session

            # Get available tools
            available_tools = tool_handler.get_available_tools_for_session()

            # Should return empty dict when no tools are available
            assert available_tools == {}


class TestCreateSessionAwareMcpServer:
    """Test create_session_aware_mcp_server function"""

    def test_create_session_aware_server(self):
        """Test creating a session-aware MCP server"""
        # Create mock base server with tools
        base_server = Mock()
        base_server._tools = {
            "getSelf": Mock(),
            "orgs_getOrgs": Mock(),
        }

        # Add handler attributes to tools
        for tool_obj in base_server._tools.values():
            tool_obj.handler = AsyncMock()

        # Create session-aware server
        result_server = create_session_aware_mcp_server(base_server)

        # Verify the same server instance is returned
        assert result_server is base_server

        # Verify session handler was added
        assert hasattr(result_server, "_session_handler")
        assert isinstance(result_server._session_handler, SessionAwareToolHandler)

        # Verify session-aware method was added
        assert hasattr(result_server, "get_available_tools_for_session")
        assert callable(result_server.get_available_tools_for_session)

        # Verify the session handler has the correct MCP instance
        assert result_server._session_handler.mcp_instance is base_server

    def test_create_session_aware_server_middleware_applied(self):
        """Test that middleware is properly applied during server creation"""
        base_server = Mock()
        base_server._tools = {
            "getSelf": Mock(),
            "orgs_getOrgs": Mock(),
        }

        # Add handler attributes
        for tool_obj in base_server._tools.values():
            tool_obj.handler = AsyncMock()

        # Store original handlers for comparison
        original_orgs_handler = base_server._tools["orgs_getOrgs"].handler

        # Create session-aware server
        result_server = create_session_aware_mcp_server(base_server)

        # Verify middleware was applied (handler should be wrapped)
        current_orgs_handler = base_server._tools["orgs_getOrgs"].handler

        # The handler should have been replaced with the wrapped version
        # (We can't easily test the exact wrapper, but we can verify it changed)
        assert (
            current_orgs_handler != original_orgs_handler
            or len(result_server._session_handler.original_tool_handlers) > 0
        )
