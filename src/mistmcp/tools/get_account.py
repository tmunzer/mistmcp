"""Account and organization-license facade tool."""

from enum import Enum
from typing import Annotated
from uuid import UUID

import mistapi
from fastmcp.exceptions import ToolError
from fastmcp.tools import ToolResult
from pydantic import Field

from mistmcp.logger import logger
from mistmcp.request_processor import get_apisession
from mistmcp.response_formatter import format_response
from mistmcp.response_processor import handle_network_error, process_response
from mistmcp.server import mcp
from mistmcp.tools._facade import internal_tool, run_internal_tool


class AccountInformation(Enum):
    ACCOUNT_INFO = "account_info"
    API_USAGE = "api_usage"
    LOGIN_FAILURES = "login_failures"
    LICENSE_SUMMARY = "license_summary"
    LICENSES_BY_SITE = "licenses_by_site"
    LICENSE_CLAIM_STATUS = "license_claim_status"


class Action_type(Enum):
    ACCOUNT_INFO = "account_info"
    API_USAGE = "api_usage"
    LOGIN_FAILURES = "login_failures"


async def get_self(
    action_type: Annotated[
        Action_type,
        Field(
            description="Type of information to retrieve about the current user and account. Possible values are `account_info`, `api_usage`, and `login_failures`"
        ),
    ],
) -> dict | list | str:
    """This tool can be used to retrieve information about the current user and account
    The information provided will depend on the `action_type` attribute:
    * `account_info`: will return information about the account including account ID, account name, and the list of orgs (and their respective `org_id`) the account has access to, with the permissions level (read or write) for each org
    * `api_usage`: will return information about the API usage of the account including the number of API calls made in the current hour cycle and the API call limit for the account
    * `login_failures`: will return information about the recent login failures for the account including the timestamp of the failure, the source IP address, and the reason for the failure"""
    logger.debug("Tool get_self called")
    logger.debug("Input Parameters: action_type: %s", action_type)
    apisession, response_format = await get_apisession()
    try:
        object_type = action_type
        match object_type.value:
            case "account_info":
                response = mistapi.api.v1.self.self.getSelf(apisession)
                await process_response(response)
            case "api_usage":
                response = mistapi.api.v1.self.usage.getSelfApiUsage(
                    apisession)
                await process_response(response)
            case "login_failures":
                response = mistapi.api.v1.self.login_failures.getSelfLoginFailures(
                    apisession
                )
                await process_response(response)
            case _:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Action_type]}",
                    }
                )
    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)
    return format_response(response, response_format)


class Response_type(Enum):
    CLAIM_STATUS = "claim_status"
    BY_SITE = "by_site"
    SUMMARY = "summary"


async def get_org_licenses(
    org_id: Annotated[UUID, Field(description="Organization ID")],
    response_type: Annotated[
        Response_type,
        Field(
            description="Type of license information to retrieve. `claim_status` returns the status of an asynchronous license claim operation, `by_site` returns the list of licenses for each site in the org, and `summary` returns a summary of the licenses in the org including total count and count by license type"
        ),
    ],
) -> dict | list | str:
    """This tool can be used to retrieve information about the licenses of an org"""
    logger.debug("Tool get_org_licenses called")
    logger.debug(
        "Input Parameters: org_id: %s, response_type: %s", org_id, response_type
    )
    apisession, response_format = await get_apisession()
    try:
        object_type = response_type
        match object_type.value:
            case "claim_status":
                response = mistapi.api.v1.orgs.claim.GetOrgLicenseAsyncClaimStatus(
                    apisession, org_id=str(org_id)
                )
                await process_response(response)
            case "by_site":
                response = mistapi.api.v1.orgs.licenses.getOrgLicensesBySite(
                    apisession, org_id=str(org_id)
                )
                await process_response(response)
            case "summary":
                response = mistapi.api.v1.orgs.licenses.getOrgLicensesSummary(
                    apisession, org_id=str(org_id)
                )
                await process_response(response)
            case _:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Response_type]}",
                    }
                )
    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)
    return format_response(response, response_format)


_GET_SELF = internal_tool(get_self)
_GET_ORG_LICENSES = internal_tool(get_org_licenses)


@mcp.tool(
    name="mist_get_account",
    description="""Get current-account details, API usage, login failures, or organization licenses.

The information provided depends on `information`:
* `account_info`: will return information about the account including account ID, account name, and the list of orgs (and their respective `org_id`) the account has access to, with the permissions level (read or write) for each org
* `api_usage`: will return information about the API usage of the account including the number of API calls made in the current hour cycle and the API call limit for the account
* `login_failures`: will return information about the recent login failures for the account including the timestamp of the failure, the source IP address, and the reason for the failure
* `license_summary`: returns a summary of the licenses in the org including total count and count by license type
* `licenses_by_site`: returns the list of licenses for each site in the org
* `license_claim_status`: returns the status of an asynchronous license claim operation.

License operations require `org_id`; account-level operations do not.""",
    tags={"self_account"},
    annotations={
        "title": "Get account information",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def get_account(
    information: Annotated[
        AccountInformation,
        Field(
            description="Account information to retrieve: account_info, api_usage, login_failures, license_summary, licenses_by_site, or license_claim_status."
        ),
    ],
    org_id: Annotated[
        UUID,
        Field(
            description="Organization ID; required for license information.",
            default=None,
        ),
    ],
) -> ToolResult:
    if (
        information.value.startswith("license_")
        or information.value == "licenses_by_site"
    ):
        if org_id is None:
            raise ToolError(
                f"org_id is required for information='{information.value}'."
            )
        response_type = {
            AccountInformation.LICENSE_SUMMARY: "summary",
            AccountInformation.LICENSES_BY_SITE: "by_site",
            AccountInformation.LICENSE_CLAIM_STATUS: "claim_status",
        }[information]
        return await run_internal_tool(
            _GET_ORG_LICENSES,
            {"org_id": org_id, "response_type": response_type},
        )
    return await run_internal_tool(_GET_SELF, {"action_type": information.value})
