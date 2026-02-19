from fastmcp import Context
from fastmcp.client.elicitation import ElicitResult
from fastmcp.server.elicitation import (
    AcceptedElicitation,
    CancelledElicitation,
    DeclinedElicitation,
)

from mistmcp.logger import logger


async def config_elicitation_handler(message, ctx: Context):

    if await ctx.get_state("disable_elicitation") is True:
        logger.debug(
            "Elicitation middleware: elicitation is disabled for this client, automatically accepting without prompting"
        )
        return ElicitResult(action="accept")

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
