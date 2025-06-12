import sys


def debug(package: str, message: str) -> None:
    print(f"DEBUG: MIST MCP LOGGER - {package}: {message}", file=sys.stderr)


def info(package: str, message: str) -> None:
    print(f"DEBUG: MIST MCP LOGGER - {package}: {message}", file=sys.stderr)


def warning(package: str, message: str) -> None:
    print(f"DEBUG: MIST MCP LOGGER - {package}: {message}", file=sys.stderr)


def error(package: str, message: str) -> None:
    print(f"DEBUG: MIST MCP LOGGER - {package}: {message}", file=sys.stderr)
