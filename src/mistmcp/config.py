"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""


class ServerConfig:
    """Configuration class for the MCP server"""

    def __init__(
        self,
        transport_mode: str = "stdio",
        debug: bool = False,
    ) -> None:
        self.transport_mode: str = transport_mode
        self.mist_apitoken: str = ""
        self.mist_host: str = ""
        self.debug = debug


# Global config instance
config = ServerConfig()
