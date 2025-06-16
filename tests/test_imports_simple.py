"""Simple import tests for session modules"""


def test_config_import() -> None:
    """Test importing config module"""
    from mistmcp.config import ServerConfig, ToolLoadingMode

    assert ServerConfig is not None
    assert ToolLoadingMode is not None


def test_session_manager_import() -> None:
    """Test importing session_manager module"""
    from mistmcp.session_manager import SessionManager, session_manager

    assert SessionManager is not None
    assert session_manager is not None


def test_session_middleware_import() -> None:
    """Test importing session_middleware module"""
    from mistmcp.session_middleware import SessionAwareToolHandler

    assert SessionAwareToolHandler is not None


def test_tool_manager_import() -> None:
    """Test importing tool_manager module"""
    from mistmcp.tool_manager import manageMcpTools, register_manage_mcp_tools_tool

    assert manageMcpTools is not None
    assert register_manage_mcp_tools_tool is not None


def test_session_aware_server_basic() -> None:
    """Test creating SessionAwareFastMCP instance"""
    from mistmcp.config import ServerConfig, ToolLoadingMode
    from mistmcp.session_aware_server import SessionAwareFastMCP

    config = ServerConfig(tool_loading_mode=ToolLoadingMode.MANAGED)
    server = SessionAwareFastMCP(config=config, transport_mode="stdio")

    assert server.config == config
    assert server.transport_mode == "stdio"
