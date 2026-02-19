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
    if response.status_code == 200:
        return
    ctx = get_context()
    api_error = {"status_code": response.status_code, "message": ""}
    if response.data:
        await ctx.error(f"Got HTTP{response.status_code} with details {response.data}")
        api_error["message"] = json.dumps(response.data)
    else:
        message = STATUS_MESSAGES.get(response.status_code or 0, "Unknown error")
        await ctx.error(f"Got HTTP{response.status_code}")
        api_error["message"] = json.dumps(message)
    raise ToolError(api_error)
