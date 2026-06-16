from fastmcp import Context
from fastmcp.client.elicitation import ElicitResult
from fastmcp.server.elicitation import (
    AcceptedElicitation,
    CancelledElicitation,
    DeclinedElicitation,
)

from mistmcp.config import config
from mistmcp.logger import logger


class ElicitationUnavailableError(RuntimeError):
    """Raised when elicitation is required but cannot be performed (stateless HTTP has
    no server->client channel). The tool wrappers convert this into a clean ToolError."""


async def config_elicitation_handler(message, ctx: Context):

    if await ctx.get_state("disable_elicitation") is True:
        logger.debug(
            "Elicitation middleware: elicitation is disabled for this client, automatically accepting without prompting"
        )
        return ElicitResult(action="accept")

    if config.stateless and config.transport_mode == "http":
        # No live session / server->client channel in stateless: in-band elicitation
        # cannot complete. Fail closed deterministically instead of calling ctx.elicit().
        raise ElicitationUnavailableError(
            "In-band elicitation is unavailable in stateless HTTP mode; this action "
            "requires disable_elicitation (DANGER ZONE) or a stateful transport."
        )

    logger.debug(
        "Elicitation middleware: prompting user with message: %s",
        message,
    )
    result = await ctx.elicit(message, response_type=None)
    match result:
        case AcceptedElicitation():
            return ElicitResult(action="accept")
        case DeclinedElicitation():
            return ElicitResult(action="decline")
        case CancelledElicitation():
            return ElicitResult(action="cancel")
        case _:
            # Default to cancel on unexpected result
            return ElicitResult(action="cancel")
