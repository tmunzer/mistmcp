""" "
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import argparse
import sys

from mistmcp.config import ServerConfig, ToolLoadingMode
from mistmcp.server_factory import create_mcp_server


def print_help() -> None:
    """Print help message"""
    help_text = """
Mist MCP Server - Modular Network Management Assistant

Usage: python -m mistmcp [OPTIONS]

OPTIONS:
    -h, --help              Show this help message
    -s, --streamable        Use streamable HTTP transport instead of stdio
    -m, --mode MODE         Tool loading mode (minimal, managed, all, custom)
    -c, --categories LIST   Comma-separated list of tool categories (for custom mode)
    -d, --debug             Enable debug output

TOOL LOADING MODES:
    minimal    - Load only essential tools (getSelf, manageMcpTools)
    managed    - Use dynamic tool management (default)
    all        - Load all available tools at startup
    custom     - Load specific categories (requires --categories)

EXAMPLES:
    python -m mistmcp                                    # Default managed mode
    python -m mistmcp --mode minimal                     # Minimal tools only
    python -m mistmcp --mode all                         # All tools loaded
    python -m mistmcp --mode custom --categories orgs,sites --debug
    """
    print(help_text)


def start(
    transport_mode: str,
    tool_mode: ToolLoadingMode,
    tool_categories: list[str],
    debug: bool = False,
) -> None:
    """
    Main entry point for the Mist MCP Server
    Args:
        transport_mode (str): Transport mode to use (e.g., "stdio", "streamable-http")
        tool_mode (ToolLoadingMode): Tool loading mode to use
        tool_categories (list[str]): List of tool categories to load in custom mode
        debug (bool): Enable debug output
    Raises:
        SystemExit: If configuration is invalid or an error occurs
    """

    # Validate configuration
    if tool_mode == ToolLoadingMode.CUSTOM and not tool_categories:
        print(
            "Error: Custom mode requires at least one category. Use --categories",
            file=sys.stderr,
        )
        sys.exit(1)

    # Create server configuration
    config = ServerConfig(
        tool_loading_mode=tool_mode,
        tool_categories=tool_categories,
        debug=debug,
    )

    if debug:
        print("Starting Mist MCP Server with configuration:")
        print(f"  Transport: {transport_mode}")
        print(f"  Tool mode: {tool_mode.value}")
        if tool_categories:
            print(f"  Categories: {', '.join(tool_categories)}")

    try:
        # Create and start the MCP server
        mcp_server = create_mcp_server(config, transport_mode)

        if transport_mode == "http":
            mcp_server.run(transport="streamable-http", host="127.0.0.1")
        else:
            mcp_server.run()

    except KeyboardInterrupt:
        print("Mist MCP Server stopped by user")

    except Exception as e:
        print(f"Mist MCP Error: {e}", file=sys.stderr)
        if debug:
            import traceback

            traceback.print_exc()


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
        default="stdio",
        help="Transport mode to use (default: stdio)",
    )
    parser.add_argument(
        "-m",
        "--mode",
        choices=["minimal", "managed", "all", "custom"],
        default="managed",
        help="Tool loading mode (default: managed)",
    )
    parser.add_argument(
        "-c",
        "--categories",
        help="Comma-separated list of tool categories, only when mode is custom",
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug output"
    )

    try:
        args = parser.parse_args()
    except SystemExit:
        sys.exit(1)

    # Set configuration from parsed arguments
    transport_mode = args.transport.lower()

    try:
        tool_mode = ToolLoadingMode(args.mode.lower())
    except ValueError:
        print(
            f"Error: Invalid mode '{args.mode}'. Valid modes: minimal, managed, all, custom",
            file=sys.stderr,
        )
        sys.exit(1)

    tool_categories = []
    if args.categories:
        tool_categories = [
            cat.strip() for cat in args.categories.split(",") if cat.strip()
        ]

    debug = args.debug
    start(transport_mode, tool_mode, tool_categories, debug)


if __name__ == "__main__":
    main()
