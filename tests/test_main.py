"""Tests for mistmcp __main__ module"""

from unittest.mock import Mock, patch

import pytest

from mistmcp.__main__ import _run_stateless_http, main, start
from mistmcp.config import ConfigurationError, config


class TestStart:
    """Test start function"""

    @patch("mistmcp.__main__.create_mcp_server")
    def test_start_http(self, mock_create_server) -> None:
        """Test starting with HTTP transport"""
        mock_server = Mock()
        mock_create_server.return_value = mock_server

        start(
            "http",
            "127.0.0.1",
            8000,
            debug=True,
            enable_write_tools=False,
            disable_elicitation=False,
            response_format="json",
        )

        mock_create_server.assert_called_once()
        config_arg = mock_create_server.call_args[0][0]

        assert config_arg.debug is True
        assert config_arg.transport_mode == "http"
        mock_server.run.assert_called_once_with(
            transport="http", host="127.0.0.1", port=8000
        )

    @patch("mistmcp.__main__.create_mcp_server")
    def test_start_http_with_custom_host(self, mock_create_server) -> None:
        """Test starting with HTTP transport and custom host"""
        mock_server = Mock()
        mock_create_server.return_value = mock_server

        start(
            "http",
            "0.0.0.0",
            8000,
            debug=True,
            enable_write_tools=False,
            disable_elicitation=False,
            response_format="json",
        )

        mock_create_server.assert_called_once()
        config_arg = mock_create_server.call_args[0][0]

        assert config_arg.debug is True
        assert config_arg.transport_mode == "http"
        mock_server.run.assert_called_once_with(
            transport="http", host="0.0.0.0", port=8000
        )

    @patch("mistmcp.__main__.create_mcp_server")
    def test_start_stdio(self, mock_create_server) -> None:
        """Test starting with stdio transport"""
        mock_server = Mock()
        mock_create_server.return_value = mock_server

        start(
            "stdio",
            "127.0.0.1",
            8000,
            debug=False,
            enable_write_tools=False,
            disable_elicitation=False,
            response_format="json",
        )

        mock_create_server.assert_called_once()
        mock_server.run.assert_called_once_with()

    @patch("mistmcp.__main__.create_mcp_server")
    def test_start_keyboard_interrupt(self, mock_create_server, capsys) -> None:
        """Test handling of KeyboardInterrupt"""
        mock_server = Mock()
        mock_server.run.side_effect = KeyboardInterrupt()
        mock_create_server.return_value = mock_server

        start(
            "stdio",
            "127.0.0.1",
            8000,
            debug=False,
            enable_write_tools=False,
            disable_elicitation=False,
            response_format="json",
        )

        captured = capsys.readouterr()
        assert "stopped by user" in captured.err

    @patch("mistmcp.__main__.create_mcp_server")
    def test_start_exception_without_debug(self, mock_create_server, capsys) -> None:
        """Test handling of exceptions without debug mode"""
        mock_create_server.side_effect = Exception("Test error")

        start(
            "stdio",
            "127.0.0.1",
            8000,
            debug=False,
            enable_write_tools=False,
            disable_elicitation=False,
            response_format="json",
        )

        captured = capsys.readouterr()
        assert "Mist MCP Error: Test error" in captured.err

    @patch("mistmcp.__main__.create_mcp_server")
    @patch("traceback.print_exc")
    def test_start_exception_with_debug(
        self, mock_traceback, mock_create_server, capsys
    ) -> None:
        """Test handling of exceptions with debug mode"""
        mock_create_server.side_effect = Exception("Test error")

        start(
            "stdio",
            "127.0.0.1",
            8000,
            debug=True,
            enable_write_tools=False,
            disable_elicitation=False,
            response_format="json",
        )

        captured = capsys.readouterr()
        assert "Mist MCP Error: Test error" in captured.err
        mock_traceback.assert_called_once()

    @patch("mistmcp.__main__.create_mcp_server")
    def test_start_debug_output(self, mock_create_server, capsys) -> None:
        """Test debug output is printed"""
        mock_server = Mock()
        mock_create_server.return_value = mock_server

        start(
            "http",
            "127.0.0.1",
            8000,
            debug=True,
            enable_write_tools=False,
            disable_elicitation=False,
            response_format="json",
        )

        captured = capsys.readouterr()
        assert "Starting Mist MCP Server" in captured.err
        assert "transport: http" in captured.err


class TestMain:
    """Test main function"""

    @patch("mistmcp.__main__.start")
    def test_main_default_args(self, mock_start) -> None:
        """Test main with default arguments"""
        with patch("sys.argv", ["mistmcp"]):
            main()

        mock_start.assert_called_once_with(
            "stdio", "127.0.0.1", 8000, False, False, False, "json", None, False
        )

    @patch("mistmcp.__main__.start")
    def test_main_with_debug(self, mock_start) -> None:
        """Test main with debug flag"""
        with patch("sys.argv", ["mistmcp", "--debug"]):
            main()

        mock_start.assert_called_once_with(
            "stdio", "127.0.0.1", 8000, True, False, False, "json", None, False
        )

    def test_main_help_exits(self) -> None:
        """Test that --help exits appropriately"""
        with patch("sys.argv", ["mistmcp", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 0

    @patch("sys.argv", ["mistmcp", "--invalid-arg"])
    def test_main_invalid_arg_exits(self) -> None:
        """Test that invalid arguments cause exit"""
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 2

    @patch("mistmcp.__main__.start")
    def test_main_custom_host_and_port(self, mock_start) -> None:
        """Test main with custom host and port"""
        with patch(
            "sys.argv",
            ["mistmcp", "--transport", "http", "--host", "0.0.0.0", "--port", "9000"],
        ):
            main()

        mock_start.assert_called_once_with(
            "http", "0.0.0.0", 9000, False, False, False, "json", None, False
        )

    @patch("mistmcp.__main__.start")
    def test_main_stateless_flag(self, mock_start) -> None:
        with patch("sys.argv", ["mistmcp", "--transport", "http", "--stateless"]):
            main()
        mock_start.assert_called_once_with(
            "http", "127.0.0.1", 8000, False, False, False, "json", None, True
        )

    @patch("mistmcp.__main__.start", side_effect=ConfigurationError("bad combo"))
    def test_main_exits_2_on_config_error(self, mock_start) -> None:
        with patch(
            "sys.argv",
            ["mistmcp", "--transport", "http", "--stateless", "--enable-write-tools"],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
        assert exc_info.value.code == 2


class TestStatelessStart:
    """Test stateless threading and launch path in start()"""

    @pytest.fixture(autouse=True)
    def _reset_stateless(self):
        # start() mutates the global config singleton; restore after each test
        # so visibility/launch state never leaks across tests.
        yield
        config.stateless = False

    @patch("mistmcp.__main__._run_stateless_http")
    @patch("mistmcp.__main__.create_mcp_server")
    def test_http_stateless_uses_stateless_launch(
        self, mock_create, mock_run_stateless
    ) -> None:
        mock_server = Mock()
        mock_create.return_value = mock_server

        start(
            "http",
            "127.0.0.1",
            8000,
            enable_write_tools=False,
            disable_elicitation=False,
            stateless=True,
        )

        mock_run_stateless.assert_called_once_with(mock_server, "127.0.0.1", 8000)
        mock_server.run.assert_not_called()

    @patch("mistmcp.__main__._run_stateless_http")
    @patch("mistmcp.__main__.create_mcp_server")
    def test_http_non_stateless_uses_run(self, mock_create, mock_run_stateless) -> None:
        mock_server = Mock()
        mock_create.return_value = mock_server

        start("http", "127.0.0.1", 8000, stateless=False)

        mock_run_stateless.assert_not_called()
        mock_server.run.assert_called_once_with(
            transport="http", host="127.0.0.1", port=8000
        )

    @patch("mistmcp.__main__.create_mcp_server")
    def test_stateless_stdio_downgrades_with_warning(self, mock_create, capsys) -> None:
        mock_server = Mock()
        mock_create.return_value = mock_server

        start("stdio", "127.0.0.1", 8000, stateless=True)

        captured = capsys.readouterr()
        assert "stateless applies only to http" in captured.err
        mock_server.run.assert_called_once_with()

    def test_start_does_not_swallow_config_error(self) -> None:
        with pytest.raises(ConfigurationError):
            start(
                "http",
                "127.0.0.1",
                8000,
                enable_write_tools=True,
                disable_elicitation=False,
                stateless=True,
            )

    @patch("uvicorn.run")
    def test_run_stateless_http_builds_stateless_app(self, mock_uvicorn_run) -> None:
        mock_server = Mock()
        app = mock_server.http_app.return_value

        _run_stateless_http(mock_server, "0.0.0.0", 9000)

        # no event_store kwarg — only stateless_http=True
        mock_server.http_app.assert_called_once_with(stateless_http=True)
        mock_uvicorn_run.assert_called_once_with(
            app,
            host="0.0.0.0",
            port=9000,
            lifespan="on",
            timeout_graceful_shutdown=2,
            ws="websockets-sansio",
        )
