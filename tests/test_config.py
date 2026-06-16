"""Tests for mistmcp configuration module"""

import pytest

from mistmcp.config import (
    ConfigurationError,
    ServerConfig,
    validate_stateless_config,
)


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


class TestStatelessConfig:
    """Test the stateless config field"""

    def test_stateless_defaults_false(self) -> None:
        assert ServerConfig().stateless is False

    def test_stateless_can_be_set(self) -> None:
        assert ServerConfig(stateless=True).stateless is True


class TestValidateStatelessConfig:
    """Test validate_stateless_config refusal matrix"""

    def test_noop_when_not_stateless(self) -> None:
        # Otherwise-refused combo, but stateless=False -> never raises
        cfg = ServerConfig(
            transport_mode="http",
            enable_write_tools=True,
            disable_elicitation=False,
            stateless=False,
        )
        validate_stateless_config(cfg)  # must not raise

    def test_refuses_http_write_without_disable(self) -> None:
        cfg = ServerConfig(
            transport_mode="http",
            enable_write_tools=True,
            disable_elicitation=False,
            stateless=True,
        )
        with pytest.raises(ConfigurationError):
            validate_stateless_config(cfg)

    def test_allows_http_write_with_disable(self) -> None:
        cfg = ServerConfig(
            transport_mode="http",
            enable_write_tools=True,
            disable_elicitation=True,
            stateless=True,
        )
        validate_stateless_config(cfg)  # must not raise

    def test_allows_http_readonly(self) -> None:
        cfg = ServerConfig(
            transport_mode="http",
            enable_write_tools=False,
            disable_elicitation=False,
            stateless=True,
        )
        validate_stateless_config(cfg)  # must not raise

    def test_allows_stdio_even_with_write(self) -> None:
        cfg = ServerConfig(
            transport_mode="stdio",
            enable_write_tools=True,
            disable_elicitation=False,
            stateless=True,
        )
        validate_stateless_config(cfg)  # must not raise (combo needs http)
