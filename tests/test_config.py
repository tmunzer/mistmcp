"""Tests for mistmcp configuration module"""

from mistmcp.config import ServerConfig


class TestServerConfig:
    """Test ServerConfig class"""

    def test_default_configuration(self) -> None:
        """Test default configuration values"""
        config = ServerConfig()
        assert config.transport_mode == "stdio"
        assert config.debug is False
        assert config.mist_apitoken == ""
        assert config.mist_host == ""

    def test_custom_transport_mode(self) -> None:
        """Test custom transport mode configuration"""
        config = ServerConfig(transport_mode="http")
        assert config.transport_mode == "http"

    def test_debug_configuration(self) -> None:
        """Test debug mode configuration"""
        config = ServerConfig(debug=True)
        assert config.debug is True

    def test_config_attributes_can_be_set(self) -> None:
        """Test that config attributes can be modified"""
        config = ServerConfig()
        config.mist_apitoken = "test-token"
        config.mist_host = "api.mist.com"

        assert config.mist_apitoken == "test-token"
        assert config.mist_host == "api.mist.com"
