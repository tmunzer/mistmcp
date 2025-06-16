"""Tests for mistmcp tool_manager module"""

import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from mistmcp.tool_manager import (
    manageMcpTools,
    register_manage_mcp_tools_tool,
    snake_case,
)
from mistmcp.tools_helper import McpToolsCategory


class TestSnakeCase:
    """Test snake_case function"""

    def test_snake_case_basic(self) -> None:
        """Test basic snake_case conversion"""
        assert snake_case("Hello World") == "hello_world"
        assert snake_case("Test-String") == "test_string"
        assert snake_case("MixedCASE") == "mixedcase"

    def test_snake_case_already_snake(self) -> None:
        """Test snake_case with already snake_case string"""
        assert snake_case("already_snake") == "already_snake"

    def test_snake_case_empty(self) -> None:
        """Test snake_case with empty string"""
        assert snake_case("") == ""

    def test_snake_case_special_chars(self) -> None:
        """Test snake_case with various special characters"""
        assert snake_case("test string-name") == "test_string_name"
        assert snake_case("org sites") == "org_sites"


class TestManageMcpTools:
    """Test manageMcpTools function"""

    @pytest.fixture
    def mock_context(self):
        """Create mock context"""
        ctx = Mock()
        ctx.warning = AsyncMock()
        ctx.info = AsyncMock()
        ctx.session = Mock()
        ctx.session.send_tool_list_changed = AsyncMock()
        return ctx

    @pytest.fixture
    def mock_session(self):
        """Create mock session"""
        session = Mock()
        session.enabled_tools = {"getSelf", "manageMcpTools"}
        session.enabled_categories = set()
        return session

    @patch("mistmcp.tool_manager.TOOLS")
    @patch("mistmcp.tool_manager.session_manager")
    @patch("mistmcp.tool_manager.get_current_session")
    @patch("mistmcp.tool_manager.get_context")
    @patch("asyncio.sleep", new_callable=AsyncMock)
    async def test_manage_mcp_tools_single_category(
        self,
        mock_sleep,
        mock_get_context,
        mock_get_session,
        mock_session_manager,
        mock_tools,
    ) -> None:
        """Test manageMcpTools with single category"""
        # Create mock objects
        mock_context = Mock()
        mock_context.warning = AsyncMock()
        mock_context.info = AsyncMock()
        mock_context.session = Mock()
        mock_context.session.send_tool_list_changed = AsyncMock()

        mock_session = Mock()
        mock_session.enabled_tools = {"getSelf", "manageMcpTools"}
        mock_session.enabled_categories = set()

        mock_get_context.return_value = mock_context
        mock_get_session.return_value = mock_session

        # Mock available tools
        mock_tools_data = {"orgs": {"tools": ["getOrgs", "getSites"]}}
        mock_tools.get = Mock(
            side_effect=lambda key, default=None: mock_tools_data.get(key, default)
        )

        await manageMcpTools([McpToolsCategory.ORGS])

        # Verify session was updated
        mock_session_manager.update_session_tools.assert_called_once()
        call_args = mock_session_manager.update_session_tools.call_args
        assert "orgs" in call_args.kwargs["enabled_categories"]
        assert "getOrgs" in call_args.kwargs["enabled_tools"]
        assert "getSites" in call_args.kwargs["enabled_tools"]
        assert "getSelf" in call_args.kwargs["enabled_tools"]
        assert "manageMcpTools" in call_args.kwargs["enabled_tools"]

        # Verify tool list changed notification
        mock_context.session.send_tool_list_changed.assert_called_once()

    @patch("mistmcp.tool_manager.TOOLS")
    @patch("mistmcp.tool_manager.session_manager")
    @patch("mistmcp.tool_manager.get_current_session")
    @patch("mistmcp.tool_manager.get_context")
    @patch("asyncio.sleep", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_manage_mcp_tools_string_category(
        self,
        mock_sleep,
        mock_get_context,
        mock_get_session,
        mock_session_manager,
        mock_tools,
        mock_context,
        mock_session,
    ) -> None:
        """Test manageMcpTools with string category"""
        mock_get_context.return_value = mock_context
        mock_get_session.return_value = mock_session

        # Mock available tools
        mock_tools_data = {"sites": {"tools": ["getSites", "getDevices"]}}
        mock_tools.get = Mock(
            side_effect=lambda key, default=None: mock_tools_data.get(key, default)
        )

        await manageMcpTools("sites")

        # Verify session was updated
        mock_session_manager.update_session_tools.assert_called_once()
        call_args = mock_session_manager.update_session_tools.call_args
        assert "sites" in call_args.kwargs["enabled_categories"]
        assert "getSites" in call_args.kwargs["enabled_tools"]

    @patch("mistmcp.tool_manager.TOOLS")
    @patch("mistmcp.tool_manager.session_manager")
    @patch("mistmcp.tool_manager.get_current_session")
    @patch("mistmcp.tool_manager.get_context")
    @patch("asyncio.sleep", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_manage_mcp_tools_comma_separated(
        self,
        mock_sleep,
        mock_get_context,
        mock_get_session,
        mock_session_manager,
        mock_tools,
        mock_context,
        mock_session,
    ) -> None:
        """Test manageMcpTools with comma-separated categories"""
        mock_get_context.return_value = mock_context
        mock_get_session.return_value = mock_session

        # Mock available tools
        mock_tools_data = {
            "orgs": {"tools": ["getOrgs"]},
            "sites": {"tools": ["getSites"]},
        }
        mock_tools.get = Mock(
            side_effect=lambda key, default=None: mock_tools_data.get(key, default)
        )

        await manageMcpTools("orgs, sites")

        # Verify both categories were processed
        mock_session_manager.update_session_tools.assert_called_once()
        call_args = mock_session_manager.update_session_tools.call_args
        assert "orgs" in call_args.kwargs["enabled_categories"]
        assert "sites" in call_args.kwargs["enabled_categories"]

    @patch("mistmcp.tool_manager.TOOLS")
    @patch("mistmcp.tool_manager.session_manager")
    @patch("mistmcp.tool_manager.get_current_session")
    @patch("mistmcp.tool_manager.get_context")
    @patch("asyncio.sleep", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_manage_mcp_tools_json_string(
        self,
        mock_sleep,
        mock_get_context,
        mock_get_session,
        mock_session_manager,
        mock_tools,
        mock_context,
        mock_session,
    ) -> None:
        """Test manageMcpTools with JSON string categories"""
        mock_get_context.return_value = mock_context
        mock_get_session.return_value = mock_session

        # Mock available tools
        mock_tools_data = {
            "orgs": {"tools": ["getOrgs"]},
            "sites": {"tools": ["getSites"]},
        }
        mock_tools.get = Mock(
            side_effect=lambda key, default=None: mock_tools_data.get(key, default)
        )

        json_categories = json.dumps(["orgs", "sites"])
        await manageMcpTools(json_categories)

        # Verify both categories were processed
        mock_session_manager.update_session_tools.assert_called_once()
        call_args = mock_session_manager.update_session_tools.call_args
        assert "orgs" in call_args.kwargs["enabled_categories"]
        assert "sites" in call_args.kwargs["enabled_categories"]

    @patch("mistmcp.tool_manager.TOOLS")
    @patch("mistmcp.tool_manager.session_manager")
    @patch("mistmcp.tool_manager.get_current_session")
    @patch("mistmcp.tool_manager.get_context")
    @patch("asyncio.sleep", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_manage_mcp_tools_unknown_category(
        self,
        mock_sleep,
        mock_get_context,
        mock_get_session,
        mock_session_manager,
        mock_tools,
        mock_context,
        mock_session,
    ) -> None:
        """Test manageMcpTools with unknown category"""
        mock_get_context.return_value = mock_context
        mock_get_session.return_value = mock_session

        # Mock empty available tools
        mock_tools_data: dict = {}
        mock_tools.get = Mock(
            side_effect=lambda key, default=None: mock_tools_data.get(key, default)
        )

        # This will cause warnings for unknown categories
        await manageMcpTools("unknown_category")

        # Verify warning was called
        mock_context.warning.assert_called()

        # Verify session was still updated with essential tools
        mock_session_manager.update_session_tools.assert_called_once()

    @patch("mistmcp.tool_manager.TOOLS")
    @patch("mistmcp.tool_manager.session_manager")
    @patch("mistmcp.tool_manager.get_current_session")
    @patch("mistmcp.tool_manager.get_context")
    @patch("asyncio.sleep", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_manage_mcp_tools_invalid_category_type(
        self,
        mock_sleep,
        mock_get_context,
        mock_get_session,
        mock_session_manager,
        mock_tools,
        mock_context,
        mock_session,
    ) -> None:
        """Test manageMcpTools with invalid category type"""
        mock_get_context.return_value = mock_context
        mock_get_session.return_value = mock_session

        # Test with invalid types (this will be handled by the function's type checking)
        await manageMcpTools(
            "invalid,123"
        )  # These will trigger warnings in the function

        # Verify warnings were called for invalid types
        assert mock_context.warning.call_count >= 2

    @patch("mistmcp.tool_manager.TOOLS")
    @patch("mistmcp.tool_manager.session_manager")
    @patch("mistmcp.tool_manager.get_current_session")
    @patch("mistmcp.tool_manager.get_context")
    @patch("asyncio.sleep", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_manage_mcp_tools_notification_failure(
        self,
        mock_sleep,
        mock_get_context,
        mock_get_session,
        mock_session_manager,
        mock_tools,
        mock_context,
        mock_session,
    ) -> None:
        """Test manageMcpTools when tool list changed notification fails"""
        mock_get_context.return_value = mock_context
        mock_get_session.return_value = mock_session
        mock_context.session.send_tool_list_changed.side_effect = Exception(
            "Notification failed"
        )

        # Mock available tools
        mock_tools_data = {
            "orgs": {"tools": ["getOrgs"]},
        }
        mock_tools.get = Mock(
            side_effect=lambda key, default=None: mock_tools_data.get(key, default)
        )

        await manageMcpTools([McpToolsCategory.ORGS])

        # Verify warning was called about notification failure
        mock_context.warning.assert_called()
        warning_call = mock_context.warning.call_args[0][0]
        assert "Failed to send tool list changed notification" in warning_call

    @patch("mistmcp.tool_manager.TOOLS")
    @patch("mistmcp.tool_manager.session_manager")
    @patch("mistmcp.tool_manager.get_current_session")
    @patch("mistmcp.tool_manager.get_context")
    @patch("asyncio.sleep", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_manage_mcp_tools_preserve_existing_tools(
        self,
        mock_sleep,
        mock_get_context,
        mock_get_session,
        mock_session_manager,
        mock_tools,
        mock_context,
        mock_session,
    ) -> None:
        """Test manageMcpTools preserves existing enabled tools"""
        mock_get_context.return_value = mock_context

        # Session already has some tools enabled
        mock_session.enabled_tools = {"getSelf", "manageMcpTools", "existing_tool"}
        mock_session.enabled_categories = {"existing_category"}
        mock_get_session.return_value = mock_session

        # Mock available tools
        mock_tools_data = {
            "orgs": {"tools": ["getOrgs"]},
        }
        mock_tools.get = Mock(
            side_effect=lambda key, default=None: mock_tools_data.get(key, default)
        )

        await manageMcpTools([McpToolsCategory.ORGS])

        # Verify existing tools and categories are preserved
        mock_session_manager.update_session_tools.assert_called_once()
        call_args = mock_session_manager.update_session_tools.call_args
        assert "existing_tool" in call_args.kwargs["enabled_tools"]
        assert "existing_category" in call_args.kwargs["enabled_categories"]
        assert "orgs" in call_args.kwargs["enabled_categories"]


class TestRegisterManageMcpToolsTool:
    """Test register_manage_mcp_tools_tool function"""

    def test_register_with_mcp_instance(self) -> None:
        """Test registering with provided MCP instance"""
        mock_mcp = Mock()
        mock_tool_decorator = Mock()
        mock_mcp.tool.return_value = mock_tool_decorator
        mock_registered_tool = Mock()
        mock_tool_decorator.return_value = mock_registered_tool

        result = register_manage_mcp_tools_tool(mock_mcp)

        assert result == mock_registered_tool
        mock_mcp.tool.assert_called_once()
        call_kwargs = mock_mcp.tool.call_args.kwargs
        assert call_kwargs["enabled"] is True
        assert call_kwargs["name"] == "manageMcpTools"
        assert "reconfigure the MCP server" in call_kwargs["description"]
        mock_tool_decorator.assert_called_once_with(manageMcpTools)
