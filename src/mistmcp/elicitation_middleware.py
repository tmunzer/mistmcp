"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import sys

import mcp.types
from fastmcp.server.middleware import Middleware, MiddlewareContext

from mistmcp.config import config


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

        if config.enable_write_tools and config.disable_elicitation:
            enable_write_tools = True
            # Log warning to FastMCP logs (visible in Docker)
            if ctx is not None:
                await ctx.info(
                    "Elicitation middleware: WARNING - both enable_write_tools and disable_elicitation config flags are set. "
                    "This is not recommended as it will enable write tools without elicitation safeguards. Proceed with caution!"
                )
            if config.debug:
                print(
                    "Elicitation middleware: WARNING - both enable_write_tools and disable_elicitation config flags are set. This is not recommended as it will enable write tools without elicitation safeguards. Proceed with caution!",
                    file=sys.stderr,
                )

        # Check 1: Does the client declare elicitation support in its MCP capabilities?
        elif config.enable_write_tools:
            try:
                caps = context.message.params.capabilities
                if (
                    caps is not None
                    and caps.elicitation is not None
                    and caps.elicitation.form is not None
                ):
                    enable_write_tools = True
                    if ctx is not None:
                        await ctx.info(
                            "Elicitation middleware: client supports elicitation"
                        )
                    if config.debug:
                        print(
                            "Elicitation middleware: client supports elicitation",
                            file=sys.stderr,
                        )
            except Exception:
                pass

            # Check 2: Transport-specific elicitation bypass
            if not enable_write_tools and config.transport_mode == "http":
                try:
                    from fastmcp.server.dependencies import get_http_request

                    request = get_http_request()
                    if (
                        request.headers.get("X-Disable-Elicitation", "false").lower()
                        == "true"
                    ):
                        enable_write_tools = True
                        if ctx is not None:
                            await ctx.info(
                                "Elicitation middleware: X-Disable-Elicitation header detected"
                            )
                        if config.debug:
                            print(
                                "Elicitation middleware: X-Disable-Elicitation header detected",
                                file=sys.stderr,
                            )
                except Exception:
                    pass

        if enable_write_tools:
            await ctx.enable_components(tags={"write"}, components={"tool"})
            if ctx is not None:
                await ctx.info(
                    "Elicitation middleware: write tools enabled for this session"
                )
            if config.debug:
                print(
                    "Elicitation middleware: write tools enabled for this session",
                    file=sys.stderr,
                )
        else:
            if ctx is not None:
                await ctx.info(
                    "Elicitation middleware: write tools disabled (no elicitation support detected)"
                )
            if config.debug:
                print(
                    "Elicitation middleware: write tools disabled (no elicitation support detected)",
                    file=sys.stderr,
                )

        return result
