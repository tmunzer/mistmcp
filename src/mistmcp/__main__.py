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
import sys
from pathlib import Path

from dotenv import load_dotenv

from mistmcp.config import config
from mistmcp.server_factory import mcp


def print_help() -> None:
    """Print help message"""
    help_text = """
Mist MCP Server - Network Management Assistant

Usage: python -m mistmcp [OPTIONS]

OPTIONS:
    -h, --help              Show this help message
    -s, --streamable        Use streamable HTTP transport instead of stdio
    -d, --debug             Enable debug output

EXAMPLES:
    python -m mistmcp                                    # Default stdio mode
    python -m mistmcp --streamable --debug               # HTTP mode with debug
    """
    print(help_text)


def start(
    transport_mode: str,
    mcp_host: str,
    mcp_port: int,
    debug: bool = False,
) -> None:
    """
    Main entry point for the Mist MCP Server
    Args:
        transport_mode (str): Transport mode to use (e.g., "stdio", "streamable-http")
        debug (bool): Enable debug output
    Raises:
        SystemExit: If configuration is invalid or an error occurs
    """

    # Create server configuration
    config.transport_mode = transport_mode
    config.debug = debug

    if config.debug:
        print(" Starting Mist MCP Server with configuration ".center(80, "="))
        print(f"  TRANSPORT: {transport_mode}")
        print(f"  MIST_HOST: {config.mist_host}")
        print(f"  MISTMCP_TRANSPORT_MODE: {config.transport_mode}")
        print(f"  MISTMCP_HOST: {mcp_host}")
        print(f"  MISTMCP_PORT: {mcp_port}")
        print(f"  MISTMCP_DEBUG: {config.debug}")
        print("".center(80, "="))

    try:
        # Load all tools before starting the server

        # Create and start the MCP server
        mcp_server = mcp

        if transport_mode == "http":
            mcp_server.run(transport="streamable-http", host=mcp_host, port=mcp_port)
        else:
            mcp_server.run()

    except KeyboardInterrupt:
        print("Mist MCP Server stopped by user")

    except Exception as e:
        print(f"Mist MCP Error: {e}", file=sys.stderr)
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
            print(
                "Warning: python-dotenv not installed, skipping .env loading",
                file=sys.stderr,
            )
    else:
        try:
            load_dotenv(override=True)
        except ImportError:
            print(
                "Warning: python-dotenv not installed, skipping .env loading",
                file=sys.stderr,
            )


def load_env_var(
    transport_mode: str | None,
    mcp_host: str | None,
    mcp_port: int | None,
    debug: bool,
) -> tuple[str, str, int, bool]:
    """Load environment variables from MIST_ENV_FILE if set"""

    if transport_mode is None:
        transport_mode = os.getenv("MISTMCP_TRANSPORT_MODE", "stdio").lower()

    if mcp_host is None:
        mcp_host = os.getenv("MISTMCP_HOST", "127.0.0.1")
    if mcp_port is None:
        port = os.getenv("MISTMCP_PORT", "8000")
        try:
            mcp_port = int(port)
        except ValueError:
            print(f"Invalid port number: {port}. Using default 8000.", file=sys.stderr)
            mcp_port = 8000

    msitmcp_debug = os.getenv("MISTMCP_DEBUG", str(debug))
    debug = msitmcp_debug.lower() in ("true", "1", "yes")

    if transport_mode == "stdio":
        config.mist_apitoken = os.getenv("MIST_APITOKEN", "")
        config.mist_host = os.getenv("MIST_HOST", "")

    return transport_mode, mcp_host, mcp_port, debug


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
        help="Transport mode to use (default: stdio)",
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug output"
    )
    parser.add_argument(
        "-e",
        "--env-file",
        help="Path to .env file to load environment variables (default: MIST_ENV_FILE)",
    )
    parser.add_argument(
        "--host",
        help="When `transport`==`http`, host to bind the MCP server to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        help="Port to run the server on (default: 8080)",
    )

    try:
        args = parser.parse_args()
    except SystemExit:
        sys.exit(2)

    transport_mode: str | None = args.transport
    mcp_host: str | None = args.host
    mcp_port: int | None = args.port
    mcp_debug: bool = args.debug

    load_env_file(args.env_file)
    (
        transport_mode,
        mcp_host,
        mcp_port,
        mcp_debug,
    ) = load_env_var(
        transport_mode,
        mcp_host,
        mcp_port,
        mcp_debug,
    )
    start(
        transport_mode,
        mcp_host,
        mcp_port,
        mcp_debug,
    )


if __name__ == "__main__":
    main()
