"""Test configuration and fixtures for mistmcp tests"""

from unittest.mock import Mock

import pytest

from mistmcp.config import ServerConfig


@pytest.fixture
def mock_mcp_instance():
    """Create a mock MCP instance for testing"""
    mock = Mock()
    mock.tool = Mock(return_value=lambda func: func)
    mock.get_tools = Mock(return_value={})
    mock.get_tool = Mock()
    return mock


@pytest.fixture
def basic_config():
    """Create a basic server configuration for testing"""
    return ServerConfig(debug=False)


@pytest.fixture
def debug_config():
    """Create a debug server configuration for testing"""
    return ServerConfig(debug=True)


@pytest.fixture
def mock_http_request():
    """Create a mock HTTP request for testing"""
    mock_request = Mock()
    mock_request.client = Mock()
    mock_request.client.host = "127.0.0.1"
    mock_request.client.port = 8080
    mock_request.query_params = {}
    mock_request.headers = {}
    return mock_request
