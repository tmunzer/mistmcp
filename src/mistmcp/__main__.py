""" "
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

from mistmcp.config import config
from mistmcp.logger import logger, setup_logging
from mistmcp.server import create_mcp_server


def start(
    transport_mode: str,
    mcp_host: str,
    mcp_port: int,
    debug: bool = False,
    enable_write_tools: bool = False,
    disable_elicitation: bool = False,
    response_format: str = "json",
    log_file: str | None = None,
) -> None:
    """
    Main entry point for the Mist MCP Server

    Args:
        transport_mode: Transport mode to use ("stdio" or "http")
        mcp_host: Host to bind HTTP server to
        mcp_port: Port for HTTP server
        debug: Enable debug output
        enable_write_tools: Enable write tools. By default, only read tools are enabled for safety. This flag enabled the full set of tools including those that can modify configuration (secured with elicitation). Use with caution!
        disable_elicitation: DANGER ZONE!!! Disable elicitation for write tools. This will allow any AI App to modify configuration objects without confirmation. Use only for testing with non-malicious AI Apps or if you have other safeguards in place. Do NOT use this in production or with untrusted AI Apps!
        response_format: Response format for HTTP transport ("json" or "string")
        log_file: Optional path to write logs to a file
    """
    # Update global config
    config.transport_mode = transport_mode
    config.debug = debug
    config.enable_write_tools = enable_write_tools
    config.disable_elicitation = disable_elicitation
    config.response_format = response_format
    config.log_file = log_file

    setup_logging(debug=debug, log_file=log_file)

    logger.info("Starting Mist MCP Server — transport: %s", transport_mode)
    logger.debug("  MIST_HOST: %s", config.mist_host)
    logger.debug("  RESPONSE_FORMAT: %s", config.response_format)
    logger.debug("  ENABLE_WRITE_TOOLS: %s", config.enable_write_tools)
    logger.debug("  DISABLE_ELICITATION: %s", config.disable_elicitation)
    if transport_mode == "http":
        logger.debug("  MCP_HOST: %s", mcp_host)
        logger.debug("  MCP_PORT: %s", mcp_port)

    try:
        mcp_server = create_mcp_server(config)

        if transport_mode == "http":
            mcp_server.run(transport="http", host=mcp_host, port=mcp_port)
        else:
            mcp_server.run()

    except KeyboardInterrupt:
        logger.info("Mist MCP Server stopped by user")

    except Exception as e:
        logger.error("Mist MCP Error: %s", e)
        if debug:
            import traceback

            traceback.print_exc()


def load_env_file(env_file: str | None = None) -> None:
    """Load environment variables from .env file if it exists"""
    if not env_file and os.getenv("MIST_ENV_FILE"):
        env_file = os.getenv("MIST_ENV_FILE")

    if env_file:
        if env_file.startswith("~/"):
            env_file = os.path.join(os.path.expanduser("~"), env_file.replace("~/", ""))
        env_file = os.path.abspath(env_file)
        dotenv_path = Path(env_file)
        try:
            load_dotenv(dotenv_path=dotenv_path, override=True)
        except ImportError:
            logger.warning("python-dotenv not installed, skipping .env loading")
    else:
        try:
            load_dotenv(override=True)
        except ImportError:
            logger.warning("python-dotenv not installed, skipping .env loading")


def load_env_var(
    transport_mode: str | None,
    mcp_host: str | None,
    mcp_port: int | None,
    debug: bool,
    enable_write_tools: bool,
    disable_elicitation: bool,
    response_format: str | None,
    log_file: str | None,
) -> tuple[str, str, int, bool, bool, bool, str, str | None]:
    """Load configuration from environment variables"""

    if transport_mode is None:
        transport_mode = os.getenv("MISTMCP_TRANSPORT_MODE", "stdio").lower()

    if mcp_host is None:
        mcp_host = os.getenv("MISTMCP_HOST", "127.0.0.1")

    if mcp_port is None:
        port = os.getenv("MISTMCP_PORT", "8000")
        try:
            mcp_port = int(port)
        except ValueError:
            logger.warning("Invalid port number: %s. Using default 8000.", port)
            mcp_port = 8000

    env_debug = os.getenv("MISTMCP_DEBUG", str(debug))
    debug = env_debug.lower() in ("true", "1", "yes")

    env_enable_write_tools = os.getenv(
        "MISTMCP_ENABLE_WRITE_TOOLS", str(enable_write_tools)
    )
    enable_write_tools = env_enable_write_tools.lower() in ("true", "1", "yes")

    if response_format is None:
        response_format = "json"

    if log_file is None:
        log_file = os.getenv("MISTMCP_LOG_FILE") or None

    if transport_mode == "stdio":
        config.mist_apitoken = os.getenv("MIST_APITOKEN", "")
        config.mist_host = os.getenv("MIST_HOST", "")

    return (
        transport_mode,
        mcp_host,
        mcp_port,
        debug,
        enable_write_tools,
        disable_elicitation,
        response_format,
        log_file,
    )


def main() -> None:
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(
        description="Mist MCP Server - Network Management Assistant",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "-t",
        "--transport",
        choices=["stdio", "http"],
        help="Transport mode (default: stdio)",
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug output"
    )
    parser.add_argument(
        "-e",
        "--env-file",
        help="Path to .env file (default: MIST_ENV_FILE env var)",
    )
    parser.add_argument(
        "--host",
        help="HTTP server host (default: 127.0.0.1)",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        help="HTTP server port (default: 8000)",
    )
    parser.add_argument(
        "--enable-write-tools",
        action="store_true",
        help="Enable write tools. By default, only read tools are enabled for safety. This flag enabled the full set of tools including those that can modify configuration (secured with elicitation). Use with caution!",
    )
    parser.add_argument(
        "--disable-elicitation",
        action="store_true",
        help="DANGER ZONE!!! Disable elicitation for write tools. This will allow any AI App to modify configuration objects without confirmation. Use only for testing with non-malicious AI Apps or if you have other safeguards in place. Do NOT use this in production or with untrusted AI Apps!",
    )
    parser.add_argument(
        "-r",
        "--response_format",
        choices=["json", "string"],
        help="Response format for HTTP transport (default: json)",
    )
    parser.add_argument(
        "--log-file",
        metavar="PATH",
        help="Also write logs to a file (default: MISTMCP_LOG_FILE env var)",
    )

    args = parser.parse_args()

    load_env_file(args.env_file)

    (
        transport_mode,
        mcp_host,
        mcp_port,
        debug,
        enable_write_tools,
        disable_elicitation,
        response_format,
        log_file,
    ) = load_env_var(
        args.transport,
        args.host,
        args.port,
        args.debug,
        args.enable_write_tools,
        args.disable_elicitation,
        args.response_format,
        args.log_file,
    )

    start(
        transport_mode,
        mcp_host,
        mcp_port,
        debug,
        enable_write_tools,
        disable_elicitation,
        response_format,
        log_file,
    )


if __name__ == "__main__":
    main()
