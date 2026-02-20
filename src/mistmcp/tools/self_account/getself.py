"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import json
import mistapi
from fastmcp import Context
from fastmcp.exceptions import ToolError
from mistmcp.request_processor import get_apisession
from mistmcp.response_processor import process_response
from mistmcp.server import mcp
from mistmcp.logger import logger

from pydantic import Field
from typing import Annotated
from enum import Enum


class Action_type(Enum):
    ACCOUNT_INFO = "account_info"
    API_USAGE = "api_usage"
    LOGIN_FAILURES = "login_failures"


@mcp.tool(
    name="getSelf",
    description="""This tool can be used to retrieve information about the current user and account.The information provided will depend on the `action_type` attribute:* `account_info`: will return information about the account including account ID, account name, and the list of orgs (and their respective `org_id`) the account has access to, with the permissions level (read or write) for each org.* `api_usage`: will return information about the API usage of the account including the number of API calls made in the current hour cycle and the API call limit for the account.* `login_failures`: will return information about the recent login failures for the account including the timestamp of the failure, the source IP address, and the reason for the failure.""",
    tags={"self_account"},
    annotations={
        "title": "getSelf",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getSelf(
    action_type: Annotated[
        Action_type,
        Field(
            description="""Type of information to retrieve about the current user and account. Possible values are `account_info`, `api_usage`, and `login_failures`."""
        ),
    ],
    ctx: Context | None = None,
) -> dict | list | str:
    """This tool can be used to retrieve information about the current user and account.The information provided will depend on the `action_type` attribute:* `account_info`: will return information about the account including account ID, account name, and the list of orgs (and their respective `org_id`) the account has access to, with the permissions level (read or write) for each org.* `api_usage`: will return information about the API usage of the account including the number of API calls made in the current hour cycle and the API call limit for the account.* `login_failures`: will return information about the recent login failures for the account including the timestamp of the failure, the source IP address, and the reason for the failure."""

    logger.debug("Tool getSelf called")

    apisession, response_format = get_apisession()
    data = {}

    object_type = action_type
    match object_type.value:
        case "account_info":
            response = mistapi.api.v1.self.self.getSelf(apisession)
            await process_response(response)
            data = response.data
        case "api_usage":
            response = mistapi.api.v1.self.usage.getSelfApiUsage(apisession)
            await process_response(response)
            data = response.data
        case "login_failures":
            response = mistapi.api.v1.self.login_failures.getSelfLoginFailures(
                apisession
            )
            await process_response(response)
            data = response.data

        case _:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Action_type]}",
                }
            )

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
