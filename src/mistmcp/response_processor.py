"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import json

from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_context
from mistapi.__api_response import APIResponse

STATUS_MESSAGES = {
    400: "Bad Request. The API endpoint exists but its syntax/payload is incorrect, detail may be given",
    401: "Unauthorized",
    403: "Permission Denied",
    404: "Not found. The API endpoint doesn't exist or resource doesn't exist",
    429: "Too Many Request. The API Token used for the request reached the 5000 API Calls per hour threshold",
}


async def process_response(response: APIResponse):
    if response.status_code is None:
        raise ToolError(
            {
                "status_code": 503,
                "message": "No response received from Mist API. Check network connectivity and host configuration.",
            }
        )
    if response.status_code == 200:
        return
    ctx = get_context()
    api_error = {"status_code": response.status_code, "message": ""}
    if response.status_code == 403:
        await ctx.error(f"Got HTTP{response.status_code} with details {response.data}")
        raise ToolError(
            {
                "status_code": 403,
                "message": "Permission Denied. This usually means the you are trying to use a tool with an invalid id (e.g. `org_id`, `site_id`, ...). Do not assume the ids, make sure to retrieve them from another tool (e.g. use the `mist_get_self` tool to retrieve the correct `org_id`)",
            }
        )
    elif response.data:
        await ctx.error(f"Got HTTP{response.status_code} with details {response.data}")
        api_error["message"] = json.dumps(response.data)
    else:
        message = STATUS_MESSAGES.get(response.status_code or 0, "Unknown error")
        await ctx.error(f"Got HTTP{response.status_code}")
        api_error["message"] = json.dumps(message)
    raise ToolError(api_error)


async def handle_network_error(exc: Exception) -> None:
    """Convert network-level exceptions to clean ToolError messages."""
    raise ToolError(
        {
            "status_code": 503,
            "message": f"API call failed: {type(exc).__name__}: {exc}",
        }
    ) from exc
