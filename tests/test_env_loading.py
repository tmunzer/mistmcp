"""Tests for mistmcp.__main__ environment variable loading"""

import os
from unittest.mock import patch

from mistmcp.__main__ import load_env_file, load_env_var
from mistmcp.config import config


class TestLoadEnvFile:
    """Test load_env_file function"""

    def test_load_env_file_with_explicit_path(self, tmp_path) -> None:
        """Test loading .env file with explicit path"""
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_VAR=test_value\nANOTHER_VAR=another_value\n")

        with patch.dict(os.environ, {}, clear=False):
            if "TEST_VAR" in os.environ:
                del os.environ["TEST_VAR"]
            if "ANOTHER_VAR" in os.environ:
                del os.environ["ANOTHER_VAR"]

            load_env_file(str(env_file))

            assert os.getenv("TEST_VAR") == "test_value"
            assert os.getenv("ANOTHER_VAR") == "another_value"

    def test_load_env_file_with_tilde_path(self, tmp_path) -> None:
        """Test loading .env file with tilde (~) in path"""
        env_dir = tmp_path / "test_env"
        env_dir.mkdir()
        env_file = env_dir / ".env"
        env_file.write_text("TILDE_TEST=tilde_value\n")

        with patch("os.path.expanduser") as mock_expanduser:
            mock_expanduser.return_value = str(tmp_path)

            with patch.dict(os.environ, {}, clear=False):
                if "TILDE_TEST" in os.environ:
                    del os.environ["TILDE_TEST"]

                load_env_file("~/test_env/.env")
                mock_expanduser.assert_called_once_with("~")
                assert os.getenv("TILDE_TEST") == "tilde_value"

    def test_load_env_file_from_mist_env_file_var(self, tmp_path) -> None:
        """Test loading .env file from MIST_ENV_FILE environment variable"""
        env_file = tmp_path / ".env"
        env_file.write_text("ENV_FILE_VAR=env_file_value\n")

        with patch.dict(os.environ, {"MIST_ENV_FILE": str(env_file)}, clear=False):
            if "ENV_FILE_VAR" in os.environ:
                del os.environ["ENV_FILE_VAR"]

            load_env_file()
            assert os.getenv("ENV_FILE_VAR") == "env_file_value"

    def test_load_env_file_default_behavior(self) -> None:
        """Test loading .env file with default behavior"""
        with patch("mistmcp.__main__.load_dotenv") as mock_load_dotenv:
            load_env_file()
            mock_load_dotenv.assert_called_once_with(override=True)

    def test_load_env_file_dotenv_import_error(self, tmp_path, capsys) -> None:
        """Test handling of ImportError when dotenv is not available"""
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_VAR=test_value\n")

        with patch("mistmcp.__main__.load_dotenv", side_effect=ImportError):
            load_env_file(str(env_file))
            captured = capsys.readouterr()
            assert "Warning: python-dotenv not installed" in captured.err


class TestLoadEnvVar:
    """Test load_env_var function"""

    def test_load_env_var_stdio_mode(self) -> None:
        """Test loading environment variables for stdio mode"""
        test_env = {
            "MIST_APITOKEN": "test-api-token",
            "MIST_HOST": "api.mist.com",
            "MISTMCP_TRANSPORT_MODE": "stdio",
            "MISTMCP_DEBUG": "true",
        }

        with patch.dict(os.environ, test_env, clear=False):
            transport_mode, mcp_host, mcp_port, debug = load_env_var(
                "stdio", None, None, True
            )

            assert config.mist_apitoken == "test-api-token"
            assert config.mist_host == "api.mist.com"
            assert transport_mode == "stdio"
            assert debug is True
            assert mcp_host == "127.0.0.1"
            assert mcp_port == 8000

    def test_load_env_var_http_mode(self) -> None:
        """Test loading environment variables for http mode"""
        test_env = {
            "MISTMCP_TRANSPORT_MODE": "http",
            "MISTMCP_DEBUG": "false",
            "MISTMCP_HOST": "0.0.0.0",
        }

        with patch.dict(os.environ, test_env, clear=False):
            transport_mode, mcp_host, mcp_port, debug = load_env_var(
                "http", None, None, False
            )

            assert transport_mode == "http"
            assert debug is False
            assert mcp_host == "0.0.0.0"
            assert mcp_port == 8000

    def test_load_env_var_debug_variations(self) -> None:
        """Test different debug flag variations"""
        test_cases = [
            ("true", True),
            ("TRUE", True),
            ("1", True),
            ("yes", True),
            ("false", False),
            ("0", False),
            ("no", False),
            ("", False),
        ]

        base_env = {
            "MIST_APITOKEN": "test-token",
            "MIST_HOST": "api.mist.com",
        }

        for debug_value, expected in test_cases:
            test_env = {**base_env, "MISTMCP_DEBUG": debug_value}

            with patch.dict(os.environ, test_env, clear=False):
                _, _, _, debug = load_env_var("stdio", None, None, False)
                assert debug == expected, f"Failed for debug_value='{debug_value}'"

    def test_load_env_var_port_parsing(self) -> None:
        """Test parsing of MISTMCP_PORT environment variable"""
        test_cases = [
            ("8080", 8080),
            ("3000", 3000),
            ("invalid", 8000),
            ("", 8000),
        ]

        base_env = {
            "MIST_APITOKEN": "test-token",
            "MIST_HOST": "api.mist.com",
        }

        for port_value, expected in test_cases:
            test_env = {**base_env, "MISTMCP_PORT": port_value}

            with patch.dict(os.environ, test_env, clear=False):
                _, _, mcp_port, _ = load_env_var("stdio", None, None, False)
                assert mcp_port == expected, f"Failed for port='{port_value}'"

    def test_load_env_var_host_and_port_from_env(self) -> None:
        """Test loading host and port from environment variables"""
        test_env = {
            "MIST_APITOKEN": "test-token",
            "MIST_HOST": "api.mist.com",
            "MISTMCP_HOST": "0.0.0.0",
            "MISTMCP_PORT": "9000",
        }

        with patch.dict(os.environ, test_env, clear=False):
            _, mcp_host, mcp_port, _ = load_env_var("stdio", None, None, False)

            assert mcp_host == "0.0.0.0"
            assert mcp_port == 9000
