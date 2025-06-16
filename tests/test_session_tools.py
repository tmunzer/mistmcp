"""Tests for mistmcp session_tools module"""

from unittest.mock import Mock, patch

import pytest

from mistmcp.session_tools import (
    get_session_tool_info,
    register_session_tool_with_mcp,
    require_session_tool,
    session_tool,
)


class TestSessionTool:
    """Test session_tool decorator"""

    @patch("mistmcp.session_tools.is_tool_enabled_for_current_session")
    @pytest.mark.asyncio
    async def test_session_tool_enabled(self, mock_is_enabled):
        """Test session_tool decorator when tool is enabled"""
        mock_is_enabled.return_value = True

        @session_tool(enabled=True, description="Test tool")
        async def test_tool():
            return "success"

        result = await test_tool()
        assert result == "success"
        mock_is_enabled.assert_called_once_with("test_tool")

    @patch("mistmcp.session_tools.is_tool_enabled_for_current_session")
    @pytest.mark.asyncio
    async def test_session_tool_disabled(self, mock_is_enabled):
        """Test session_tool decorator when tool is disabled"""
        mock_is_enabled.return_value = False

        @session_tool(enabled=True, description="Test tool")
        async def test_tool():
            return "success"

        with pytest.raises(Exception) as exc_info:
            await test_tool()

        error = exc_info.value
        assert "not enabled for this session" in str(error)
        mock_is_enabled.assert_called_once_with("test_tool")

    def test_session_tool_metadata(self):
        """Test that session_tool decorator adds metadata"""

        @session_tool(enabled=True, description="Test tool", category="test")
        async def test_tool():
            return "success"

        # Check metadata is added
        assert hasattr(test_tool, "_is_session_tool")
        assert test_tool._is_session_tool is True
        assert hasattr(test_tool, "_mcp_tool_config")
        assert test_tool._mcp_tool_config["enabled"] is True
        assert test_tool._mcp_tool_config["description"] == "Test tool"
        assert test_tool._mcp_tool_config["category"] == "test"
        assert hasattr(test_tool, "_original_func")

    def test_session_tool_default_params(self):
        """Test session_tool decorator with default parameters"""

        @session_tool()
        async def test_tool():
            return "success"

        assert test_tool._mcp_tool_config["enabled"] is False
        assert test_tool._is_session_tool is True

    @patch("mistmcp.session_tools.is_tool_enabled_for_current_session")
    @pytest.mark.asyncio
    async def test_session_tool_with_args(self, mock_is_enabled):
        """Test session_tool decorator with function arguments"""
        mock_is_enabled.return_value = True

        @session_tool(enabled=True)
        async def test_tool(arg1, arg2, kwarg1=None):
            return f"{arg1}-{arg2}-{kwarg1}"

        result = await test_tool("a", "b", kwarg1="c")
        assert result == "a-b-c"
        mock_is_enabled.assert_called_once_with("test_tool")


class TestRequireSessionTool:
    """Test require_session_tool decorator"""

    @patch("mistmcp.session_tools.is_tool_enabled_for_current_session")
    @pytest.mark.asyncio
    async def test_require_session_tool_enabled(self, mock_is_enabled):
        """Test require_session_tool when required tool is enabled"""
        mock_is_enabled.return_value = True

        @require_session_tool("orgs_getOrgs")
        async def helper_function():
            return "helper_result"

        result = await helper_function()
        assert result == "helper_result"
        mock_is_enabled.assert_called_once_with("orgs_getOrgs")

    @patch("mistmcp.session_tools.is_tool_enabled_for_current_session")
    @pytest.mark.asyncio
    async def test_require_session_tool_disabled(self, mock_is_enabled):
        """Test require_session_tool when required tool is disabled"""
        mock_is_enabled.return_value = False

        @require_session_tool("orgs_getOrgs")
        async def helper_function():
            return "helper_result"

        with pytest.raises(Exception) as exc_info:
            await helper_function()

        error = exc_info.value
        assert "requires the 'orgs_getOrgs' tool" in str(error)
        mock_is_enabled.assert_called_once_with("orgs_getOrgs")

    @patch("mistmcp.session_tools.is_tool_enabled_for_current_session")
    @pytest.mark.asyncio
    async def test_require_session_tool_with_args(self, mock_is_enabled):
        """Test require_session_tool with function arguments"""
        mock_is_enabled.return_value = True

        @require_session_tool("test_tool")
        async def helper_function(x, y, z=None):
            return x + y + (z or 0)

        result = await helper_function(1, 2, z=3)
        assert result == 6
        mock_is_enabled.assert_called_once_with("test_tool")


class TestGetSessionToolInfo:
    """Test get_session_tool_info function"""

    def test_get_session_tool_info_with_session_tool(self):
        """Test getting info from a session tool"""

        @session_tool(enabled=True, description="Test tool", category="test")
        async def test_tool():
            return "success"

        info = get_session_tool_info(test_tool)

        assert info is not None
        assert info["name"] == "test_tool"
        assert info["config"]["enabled"] is True
        assert info["config"]["description"] == "Test tool"
        assert info["config"]["category"] == "test"
        assert "original_func" in info

    def test_get_session_tool_info_with_regular_function(self):
        """Test getting info from a regular function (not session tool)"""

        async def regular_function():
            return "success"

        info = get_session_tool_info(regular_function)
        assert info is None

    def test_get_session_tool_info_with_partial_metadata(self):
        """Test getting info from function with partial session tool metadata"""

        async def partial_tool():
            return "success"

        # Add partial metadata
        partial_tool._is_session_tool = True
        # Don't add _mcp_tool_config

        info = get_session_tool_info(partial_tool)

        assert info is not None
        assert info["name"] == "partial_tool"
        assert info["config"] == {}  # Default empty config
        assert (
            info["original_func"] == partial_tool
        )  # Falls back to the function itself

    def test_get_session_tool_info_false_flag(self):
        """Test getting info from function with _is_session_tool = False"""

        async def fake_tool():
            return "success"

        fake_tool._is_session_tool = False
        fake_tool._mcp_tool_config = {"enabled": True}

        info = get_session_tool_info(fake_tool)
        assert info is None


class TestRegisterSessionToolWithMcp:
    """Test register_session_tool_with_mcp function"""

    def test_register_session_tool_success(self):
        """Test registering a session tool with MCP instance"""
        # Create a mock MCP instance
        mock_mcp = Mock()
        mock_tool_decorator = Mock()
        mock_mcp.tool.return_value = mock_tool_decorator
        mock_registered_tool = Mock()
        mock_tool_decorator.return_value = mock_registered_tool

        @session_tool(enabled=True, description="Test tool")
        async def test_tool():
            return "success"

        result = register_session_tool_with_mcp(test_tool, mock_mcp)

        assert result == mock_registered_tool
        mock_mcp.tool.assert_called_once_with(enabled=True, description="Test tool")
        mock_tool_decorator.assert_called_once_with(test_tool)

    def test_register_session_tool_with_regular_function(self):
        """Test registering a regular function (should return None)"""
        mock_mcp = Mock()

        async def regular_function():
            return "success"

        result = register_session_tool_with_mcp(regular_function, mock_mcp)

        assert result is None
        mock_mcp.tool.assert_not_called()

    def test_register_session_tool_with_empty_config(self):
        """Test registering a session tool with empty config"""
        mock_mcp = Mock()
        mock_tool_decorator = Mock()
        mock_mcp.tool.return_value = mock_tool_decorator
        mock_registered_tool = Mock()
        mock_tool_decorator.return_value = mock_registered_tool

        @session_tool()  # No config provided
        async def test_tool():
            return "success"

        result = register_session_tool_with_mcp(test_tool, mock_mcp)

        assert result == mock_registered_tool
        mock_mcp.tool.assert_called_once_with(enabled=False)  # Default enabled=False
        mock_tool_decorator.assert_called_once_with(test_tool)

    def test_register_session_tool_with_complex_config(self):
        """Test registering a session tool with complex configuration"""
        mock_mcp = Mock()
        mock_tool_decorator = Mock()
        mock_mcp.tool.return_value = mock_tool_decorator
        mock_registered_tool = Mock()
        mock_tool_decorator.return_value = mock_registered_tool

        @session_tool(
            enabled=True,
            description="Complex tool",
            category="advanced",
            timeout=30,
            custom_param="value",
        )
        async def complex_tool():
            return "success"

        result = register_session_tool_with_mcp(complex_tool, mock_mcp)

        assert result == mock_registered_tool
        expected_config = {
            "enabled": True,
            "description": "Complex tool",
            "category": "advanced",
            "timeout": 30,
            "custom_param": "value",
        }
        mock_mcp.tool.assert_called_once_with(**expected_config)
        mock_tool_decorator.assert_called_once_with(complex_tool)
