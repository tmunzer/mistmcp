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
        enable_write_tools: bool = False,
        disable_elicitation: bool = False,
        response_format: str = "json",
    ) -> None:
        self.transport_mode: str = transport_mode
        self.mist_apitoken: str = ""
        self.mist_host: str = ""
        self.debug = debug
        self.enable_write_tools = enable_write_tools
        self.disable_elicitation = disable_elicitation
        self.response_format = response_format


# Global config instance
config = ServerConfig()
