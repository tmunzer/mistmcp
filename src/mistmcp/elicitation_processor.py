from fastmcp import Context
from fastmcp.client.elicitation import ElicitResult
from fastmcp.server.elicitation import (
    AcceptedElicitation,
    CancelledElicitation,
    DeclinedElicitation,
)


async def config_elicitation_handler(message, ctx: Context):

    if ctx.get_state("disable_elicitation"):
        return ElicitResult(action="accept")

    result = await ctx.elicit(message, response_type=str)
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
