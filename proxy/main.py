import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import Client, FastMCP
from fastmcp.client.auth import BearerAuth


def start(
    mist_host: str,
    mist_apitoken: str,
) -> None:
    """Start the Mist MCP Server Proxy"""

    # Create authenticated client
    client = Client(
        f"http://mcp.mist-lab.fr/mcp/?cloud={mist_host}",
        auth=BearerAuth(token=mist_apitoken),
    )
    # Create proxy using the authenticated client
    proxy = FastMCP.as_proxy(client, name="Authenticated Proxy")
    proxy.run()


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
    mist_host: str | None,
    mist_apitoken: str | None,
) -> tuple[str, str]:
    """Load environment variables from MIST_ENV_FILE if set"""

    if mist_host is None:
        mist_host = os.getenv("MIST_HOST", "api.mist.com")
    if mist_apitoken is None:
        mist_apitoken = os.getenv("MIST_APITOKEN", "")

    if not mist_apitoken:
        raise ValueError(
            "Missing required parameter: 'MIST_APITOKEN' environment variable or --apitoken argument"
        )

    return mist_host, mist_apitoken


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Mist MCP Server Proxy",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-c",
        "--cloud",
        help="Cloud to connect to (default: api.mist.com)",
    )
    parser.add_argument(
        "-t",
        "--apitoken",
        help="API Token to use for authentication",
    )
    parser.add_argument(
        "-e",
        "--env-file",
        help="Path to .env file to load environment variable",
    )

    try:
        args = parser.parse_args()
    except SystemExit:
        sys.exit(2)

    MIST_HOST: str | None = args.cloud
    MIST_APITOKEN: str | None = args.apitopken
    ENV_FILE: str | None = args.env_file

    load_env_file(args.env_file)
    (
        MIST_HOST,
        MIST_APITOKEN,
    ) = load_env_var(
        MIST_HOST,
        MIST_APITOKEN,
    )
    start(
        MIST_HOST,
        MIST_APITOKEN,
    )
