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
from mistmcp.response_formatter import format_response
from mistmcp.server import mcp
from mistmcp.logger import logger

from pydantic import Field
from typing import Annotated
from uuid import UUID


@mcp.tool(
    name="getOrgLicenses",
    description="""This tool can be used to retrieve information about the licenses of an org""",
    tags={"orgs"},
    annotations={
        "title": "getOrgLicenses",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getOrgLicenses(
    org_id: Annotated[UUID, Field(description="""Organization ID""")],
    ctx: Context | None = None,
) -> dict | list | str:
    """This tool can be used to retrieve information about the licenses of an org"""

    logger.debug("Tool getOrgLicenses called")

    apisession, response_format = get_apisession()

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

    return format_response(response, response_format)
