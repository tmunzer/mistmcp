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

        # DANGER ZONE: If both enable_write_tools and disable_elicitation config flags are set, enable write tools
        # without elicitation safeguards. This is not recommended and should only be used for testing with non-malicious
        # AI Apps or if you have other safeguards in place. Do NOT use this in production or with untrusted AI Apps!
        if config.enable_write_tools and config.disable_elicitation:
            enable_write_tools = True
            # During on_initialize, ctx.info() is not available (request_id not set yet)
            # Log to stderr only for debugging
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
                    caps is not None and caps.elicitation is not None
                    # and caps.elicitation.form is not None
                ):
                    enable_write_tools = True
                    if ctx is not None:
                        await ctx.set_state("disable_elicitation", False)
                    if config.debug:
                        print(
                            "Elicitation middleware: client supports elicitation",
                            file=sys.stderr,
                        )
            except Exception as exc:
                if config.debug:
                    print(
                        f"Elicitation middleware: error checking capabilities for elicitation support: {exc}",
                        file=sys.stderr,
                    )
                pass

            # Check 2: Transport-specific elicitation bypass
            if config.transport_mode == "http":
                try:
                    from fastmcp.server.dependencies import get_http_request

                    request = get_http_request()
                    print(request.headers, file=sys.stderr)
                    if (
                        request.headers.get("X-Disable-Elicitation", "false").lower()
                        == "true"
                    ):
                        enable_write_tools = True
                        if ctx is not None:
                            await ctx.set_state("disable_elicitation", True)
                        if config.debug:
                            print(
                                "Elicitation middleware: X-Disable-Elicitation header detected",
                                file=sys.stderr,
                            )
                except Exception as exc:
                    if config.debug:
                        print(
                            f"Elicitation middleware: error checking X-Disable-Elicitation header: {exc}",
                            file=sys.stderr,
                        )

        if enable_write_tools:
            if ctx is not None:
                await ctx.enable_components(tags={"write"}, components={"tool"})
            if config.debug:
                print(
                    "Elicitation middleware: write tools enabled for this session",
                    file=sys.stderr,
                )
        else:
            if config.debug:
                print(
                    "Elicitation middleware: write tools disabled (no elicitation support detected)",
                    file=sys.stderr,
                )

        return result
