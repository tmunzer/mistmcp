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

from mistmcp.config import ToolLoadingMode, config
from mistmcp.server_factory import create_mcp_server


def print_help() -> None:
    """Print help message"""
    help_text = """
Mist MCP Server - AI-Powered Network Management Assistant

Usage: uv run mistmcp [OPTIONS]

OPTIONS:
    -t, --transport MODE    Transport mode: stdio (default) or http
    -m, --mode MODE         Only when `transport`==`stdio`, Tool loading mode: managed, all (default)
    --host HOST             Only when `transport`==`http`, HTTP server host (default: 127.0.0.1)
    -p, --port PORT         Only when `transport`==`http`, HTTP server port (default: 8000)
    -e, --env-file PATH     Path to .env file
    -d, --debug             Enable debug output
    -h, --help              Show help message

TOOL LOADING MODES:
    managed    - Essential tools loaded at startup
    all        - All tools loaded at startup (default)

TRANSPORT MODES:
    stdio      - Standard input/output (for Claude Desktop, VS Code)
    http       - HTTP server (for remote access)

EXAMPLES:
    uv run mistmcp                                    # Default: stdio + all mode
    uv run mistmcp --mode managed --debug            # Managed mode with debug
    uv run mistmcp --transport http --host 0.0.0.0    # HTTP on all interfaces
    uv run mistmcp --env-file ~/.mist.env             # Custom env file
    """
    print(help_text)


def start(
    transport_mode: str,
    tool_loading_mode: ToolLoadingMode,
    tool_categories: list[str],
    mcp_host: str,
    mcp_port: int,
    debug: bool = False,
) -> None:
    """
    Main entry point for the Mist MCP Server
    Args:
        transport_mode (str): Transport mode to use (e.g., "stdio", "streamable-http")
        tool_mode (ToolLoadingMode): Tool loading mode to use
        tool_categories (list[str]): List of tool categories to load (unused in simplified version)
        debug (bool): Enable debug output
    Raises:
        SystemExit: If configuration is invalid or an error occurs
    """

    # Create server configuration
    config.transport_mode = transport_mode
    config.tool_loading_mode = tool_loading_mode
    config.tool_categories = tool_categories
    config.debug = debug

    if config.debug:
        print(" Starting Mist MCP Server with configuration ".center(80, "="))
        print(f"  TRANSPORT: {transport_mode}")
        print(f"  TOOL LOADING MODE: {tool_loading_mode.value}")
        if tool_categories:
            print(f"  CATEGORIES: {', '.join(tool_categories)}")

        print(f"  MIST_HOST: {config.mist_host}")
        print(f"  MISTMCP_TRANSPORT_MODE: {config.transport_mode}")
        print(f"  MISTMCP_TOOL_LOADING_MODE: {config.tool_loading_mode.value}")
        print(f"  MISTMCP_TOOL_CATEGORIES: {', '.join(config.tool_categories)}")
        print(f"  MISTMCP_HOST: {mcp_host}")
        print(f"  MISTMCP_PORT: {mcp_port}")
        print(f"  MISTMCP_DEBUG: {config.debug}")
        print("".center(80, "="))

    try:
        # Create and start the MCP server

        mcp_server = create_mcp_server(config)
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
    tool_loading_mode: ToolLoadingMode | None,
    tool_categories: list[str] | None,
    mcp_host: str | None,
    mcp_port: int | None,
    debug: bool,
) -> tuple[str, ToolLoadingMode, list[str], str, int, bool]:
    """Load environment variables from MIST_ENV_FILE if set"""

    if transport_mode is None:
        transport_mode = os.getenv("MISTMCP_TRANSPORT_MODE", "stdio").lower()

    if tool_loading_mode is None:
        msitmcp_tool_loading_mode = os.getenv(
            "MISTMCP_TOOL_LOADING_MODE", "all"
        ).lower()
        try:
            tool_loading_mode = ToolLoadingMode(msitmcp_tool_loading_mode.lower())
        except ValueError:
            tool_loading_mode = ToolLoadingMode.ALL

    if tool_categories is None:
        msitmcp_tool_categories = os.getenv("MISTMCP_TOOL_CATEGORIES", "")
        tool_categories = [
            cat.strip() for cat in msitmcp_tool_categories.split(",") if cat.strip()
        ]

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

    return transport_mode, tool_loading_mode, tool_categories, mcp_host, mcp_port, debug


def main() -> None:
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(
        description="Mist MCP Server - Modular Network Management Assistant",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "-t",
        "--transport",
        choices=["stdio", "http"],
        help="Transport mode to use (default: stdio)",
    )
    parser.add_argument(
        "-m",
        "--mode",
        choices=["managed", "all"],
        help="Tool loading mode (default: all)",
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
    tool_loading_mode: ToolLoadingMode | None = None
    # tool_categories no longer used in simplified version
    tool_categories: list[str] = []
    mcp_host: str | None = args.host
    mcp_port: int | None = args.port
    mcp_debug: bool

    if args.mode:
        try:
            tool_loading_mode = ToolLoadingMode(args.mode.lower())
        except ValueError:
            print(
                f"Error: Invalid mode '{args.mode}'. Valid modes: managed, all",
                file=sys.stderr,
            )
            sys.exit(1)

    if transport_mode == "http" and tool_loading_mode:
        raise ValueError(
            "Tool loading mode is not applicable for HTTP transport. Use stdio transport instead."
        )
    elif transport_mode == "http":
        tool_loading_mode = ToolLoadingMode("all")
    mcp_debug = args.debug

    load_env_file(args.env_file)
    (
        transport_mode,
        tool_loading_mode,
        tool_categories,
        mcp_host,
        mcp_port,
        mcp_debug,
    ) = load_env_var(
        transport_mode,
        tool_loading_mode,
        tool_categories,
        mcp_host,
        mcp_port,
        mcp_debug,
    )
    start(
        transport_mode,
        tool_loading_mode,
        tool_categories,
        mcp_host,
        mcp_port,
        mcp_debug,
    )


if __name__ == "__main__":
    main()
