"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import logging
import sys

logger = logging.getLogger("mistmcp")


def mask_token(token: str) -> str:
    """Return a redacted version of an API token safe for logging."""
    if not token or len(token) < 8:
        return "***"
    return f"{token[:4]}...{token[-4:]}"


def setup_logging(debug: bool = False, log_file: str | None = None) -> None:
    """Configure the mistmcp logger.

    - Level: DEBUG if debug=True, else INFO
    - Handlers: stderr always; file if log_file is specified
    """
    level = logging.DEBUG if debug else logging.INFO
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    logger.setLevel(level)
    logger.handlers.clear()  # Avoid duplicate handlers if called multiple times

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(formatter)
    logger.addHandler(stderr_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
