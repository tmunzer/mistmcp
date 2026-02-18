from fastmcp.client.elicitation import ElicitResult
from fastmcp.server.elicitation import (
    AcceptedElicitation,
    CancelledElicitation,
    DeclinedElicitation,
)

from mistmcp.server import get_mcp

mcp = get_mcp()


async def config_elicitation_handler(message, context):

    result = await context.elicit(f"{message}")
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
