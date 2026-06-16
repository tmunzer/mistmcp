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
        log_file: str | None = None,
        stateless: bool = False,
    ) -> None:
        self.transport_mode: str = transport_mode
        self.mist_apitoken: str = ""
        self.mist_host: str = ""
        self.debug = debug
        self.enable_write_tools = enable_write_tools
        self.disable_elicitation = disable_elicitation
        self.response_format = response_format
        self.log_file: str | None = log_file
        self.stateless = stateless


class ConfigurationError(Exception):
    """Raised when the server configuration is invalid and startup must be refused."""


def validate_stateless_config(config: "ServerConfig") -> None:
    """Refuse stateless when it collides with in-band elicitation.

    Stateless HTTP has no live session and no server->client channel, so the
    ctx.elicit() handshake cannot work. The only config that needs that handshake is
    write tools enabled over HTTP without disable_elicitation. Everything else
    (read-only HTTP, write + disable_elicitation, stdio) is stateless-safe.
    """
    if not config.stateless:
        return
    if (
        config.transport_mode == "http"
        and config.enable_write_tools
        and not config.disable_elicitation
    ):
        raise ConfigurationError(
            "Stateless HTTP mode is incompatible with in-band elicitation "
            "(write tools enabled without disable_elicitation), which needs a live "
            "session. Add --disable-elicitation / MISTMCP_DISABLE_ELICITATION=true, "
            "drop --enable-write-tools, or unset --stateless / MISTMCP_STATELESS."
        )


# Global config instance
config = ServerConfig()
