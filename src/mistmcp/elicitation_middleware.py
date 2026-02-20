"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import mcp.types
from fastmcp.server.middleware import Middleware, MiddlewareContext

from mistmcp.config import config
from mistmcp.logger import logger


class ElicitationMiddleware(Middleware):
    """Middleware to detect elicitation support and enable write tools accordingly.

    During MCP initialization, detects whether the client supports elicitation
    (via MCP capabilities) or has explicitly opted out via the X-Disable-Elicitation
    HTTP header (HTTP transport) or the --disable-elicitation flag (stdio transport).

    Write tools are disabled by default (via the server-level Visibility transform).
    If either condition is detected, they are enabled for this session only.
    """

    async def on_initialize(
        self,
        context: MiddlewareContext[mcp.types.InitializeRequest],
        call_next,
    ) -> mcp.types.InitializeResult | None:
        # Process initialization first so client capabilities are available
        result = await call_next(context)

        ctx = context.fastmcp_context
        if ctx is None:
            return result

        enable_write_tools = False
        enable_write_delete_tools = False

        # DANGER ZONE: If both enable_write_tools and disable_elicitation config flags are set, enable write tools
        # without elicitation safeguards. This is not recommended and should only be used for testing with non-malicious
        # AI Apps or if you have other safeguards in place. Do NOT use this in production or with untrusted AI Apps!
        if config.enable_write_tools and config.disable_elicitation:
            enable_write_tools = True
            logger.warning(
                "Elicitation middleware: WARNING - both enable_write_tools and disable_elicitation config flags are set. This is not recommended as it will enable write tools without elicitation safeguards. Proceed with caution!"
            )

        # Check 1: Does the client declare elicitation support in its MCP capabilities?
        elif config.enable_write_tools:
            try:
                caps = context.message.params.capabilities
                if (
                    caps is not None and caps.elicitation is not None
                    # and caps.elicitation.form is not None
                ):
                    enable_write_tools = True
                    if ctx is not None:
                        await ctx.set_state("disable_elicitation", False)
                    logger.debug("Elicitation middleware: client supports elicitation")
            except Exception as exc:
                logger.error(
                    "Elicitation middleware: error checking capabilities for elicitation support: %s",
                    exc,
                )

            # Check 2: Transport-specific elicitation bypass
            if config.transport_mode == "http":
                try:
                    from fastmcp.server.dependencies import get_http_request

                    request = get_http_request()
                    if (
                        request.headers.get("X-Disable-Elicitation", "false").lower()
                        == "true"
                    ):
                        enable_write_tools = True
                        if ctx is not None:
                            await ctx.set_state("disable_elicitation", True)
                        logger.debug(
                            "Elicitation middleware: X-Disable-Elicitation header detected"
                        )
                    elif (
                        request.query_params.get("disable_elicitation", "false").lower()
                        == "true"
                    ):
                        enable_write_tools = True
                        if ctx is not None:
                            await ctx.set_state("disable_elicitation", True)
                        logger.debug(
                            "Elicitation middleware: disable_elicitation query parameter detected"
                        )
                    elif (
                        request.query_params.get("experimental", "false").lower()
                        == "true"
                    ):
                        enable_write_delete_tools = True
                        if ctx is not None:
                            await ctx.set_state("disable_elicitation", True)
                        logger.debug(
                            "Elicitation middleware: experimental query parameter detected (elicitation bypass)"
                        )
                except Exception as exc:
                    logger.error(
                        "Elicitation middleware: error checking X-Disable-Elicitation header: %s",
                        exc,
                    )
        else:
            logger.debug(
                "Elicitation middleware: write tools not enabled in config, skipping elicitation checks"
            )

        if enable_write_delete_tools:
            if ctx is not None:
                await ctx.enable_components(tags={"write_delete"}, components={"tool"})
                await ctx.disable_components(tags={"write"}, components={"tool"})
            logger.debug(
                "Elicitation middleware: write_delete tools enabled for this session"
            )
        elif enable_write_tools:
            if ctx is not None:
                await ctx.enable_components(tags={"write"}, components={"tool"})
                await ctx.disable_components(tags={"write_delete"}, components={"tool"})
            logger.debug("Elicitation middleware: write tools enabled for this session")
        else:
            await ctx.disable_components(
                tags={"write", "write_delete"}, components={"tool"}
            )
            logger.debug(
                "Elicitation middleware: write tools disabled (no elicitation support detected)"
            )

        return result
