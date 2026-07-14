"""Tests for mistmcp server module"""

from unittest.mock import patch

from fastmcp import FastMCP

from mistmcp.config import ServerConfig
from mistmcp.server import (
    _PROTECTED_WRITE_TAGS,
    _configure_write_visibility,
    _write_visible_tags,
    create_mcp_server,
    mcp,
)


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
    def test_create_mcp_server_with_debug(self, mock_load_tools, caplog) -> None:
        """Test creating MCP server with debug output"""
        import logging

        mock_load_tools.return_value = ["getSelf", "getOrg"]

        config = ServerConfig(transport_mode="stdio", debug=True)
        with caplog.at_level(logging.DEBUG, logger="mistmcp"):
            create_mcp_server(config)

        assert "MCP Server ready with 2 tools" in caplog.text

    @patch("mistmcp.server._load_tools")
    def test_create_mcp_server_without_debug(self, mock_load_tools, caplog) -> None:
        """Test that no debug output is emitted without debug mode"""
        import logging

        mock_load_tools.return_value = []

        config = ServerConfig(transport_mode="stdio", debug=False)
        with caplog.at_level(logging.INFO, logger="mistmcp"):
            create_mcp_server(config)

        assert "MCP Server ready" not in caplog.text


def _build_fresh_mcp() -> FastMCP:
    m = FastMCP(name="test_visibility")

    @m.tool(name="w_tool", tags={"write"})
    def w_tool() -> str:
        return "w"

    @m.tool(name="wd_tool", tags={"write_delete"})
    def wd_tool() -> str:
        return "wd"

    @m.tool(name="up_tool", tags={"utilities_upgrade"})
    def up_tool() -> str:
        return "up"

    @m.tool(name="read_tool", tags={"info"})
    def read_tool() -> str:
        return "r"

    return m


async def _visible_names(m: FastMCP) -> set[str]:
    tools = await m.list_tools()  # public path applies Visibility transforms
    return {t.name for t in tools}


_FACADE_TOOL_NAMES = {
    "mist_get_account",
    "mist_describe",
    "mist_search_assets",
    "mist_get_configuration",
    "mist_search_activity",
    "mist_search_security",
    "mist_get_site_insights",
}

_REMOVED_TOOL_NAMES = {
    "mist_get_self",
    "mist_get_org_licenses",
    "mist_get_constants",
    "mist_get_configuration_object_schema",
    "mist_search_device",
    "mist_search_client",
    "mist_get_configuration_objects",
    "mist_search_device_config_history",
    "mist_search_events",
    "mist_search_audit_logs",
    "mist_search_nac_user_macs",
    "mist_list_rogue_devices",
    "mist_get_insight_metrics",
    "mist_get_site_rrm_info",
}


class TestFacadeCatalog:
    async def test_actual_catalog_has_expected_tools(self) -> None:
        configured = create_mcp_server(ServerConfig())
        visible = await _visible_names(configured)

        assert len(visible) == 14
        assert _FACADE_TOOL_NAMES <= visible
        assert "mist_get_next_page" in visible
        assert "mist_topology" in visible
        assert not (_REMOVED_TOOL_NAMES & visible)


class TestWriteVisibleTags:
    def test_protected_tags_are_write_and_write_delete(self) -> None:
        assert _PROTECTED_WRITE_TAGS == {"write", "write_delete"}

    def test_readonly_hides_all(self) -> None:
        cfg = ServerConfig(enable_write_tools=False, disable_elicitation=False)
        assert _write_visible_tags(cfg) == set()

    def test_danger_zone_shows_write_only(self) -> None:
        cfg = ServerConfig(enable_write_tools=True, disable_elicitation=True)
        assert _write_visible_tags(cfg) == {"write"}

    def test_write_without_disable_shows_nothing_at_build(self) -> None:
        cfg = ServerConfig(enable_write_tools=True, disable_elicitation=False)
        assert _write_visible_tags(cfg) == set()


class TestConfigureWriteVisibility:
    async def test_readonly_hides_write_and_write_delete(self) -> None:
        m = _build_fresh_mcp()
        _configure_write_visibility(m, ServerConfig(enable_write_tools=False))
        visible = await _visible_names(m)
        assert "w_tool" not in visible
        assert "wd_tool" not in visible
        assert "up_tool" in visible  # utilities_upgrade untouched
        assert "read_tool" in visible

    async def test_danger_zone_shows_write_hides_write_delete(self) -> None:
        m = _build_fresh_mcp()
        _configure_write_visibility(
            m, ServerConfig(enable_write_tools=True, disable_elicitation=True)
        )
        visible = await _visible_names(m)
        assert "w_tool" in visible
        assert "wd_tool" not in visible
        assert "up_tool" in visible

    async def test_idempotent_last_config_wins(self) -> None:
        m = _build_fresh_mcp()
        _configure_write_visibility(
            m, ServerConfig(enable_write_tools=True, disable_elicitation=True)
        )
        _configure_write_visibility(m, ServerConfig(enable_write_tools=False))
        visible = await _visible_names(m)
        assert "w_tool" not in visible
        assert "wd_tool" not in visible

    async def test_idempotent_last_config_wins_reverse(self) -> None:
        m = _build_fresh_mcp()
        _configure_write_visibility(m, ServerConfig(enable_write_tools=False))
        _configure_write_visibility(
            m, ServerConfig(enable_write_tools=True, disable_elicitation=True)
        )
        visible = await _visible_names(m)
        assert "w_tool" in visible
        assert "wd_tool" not in visible
