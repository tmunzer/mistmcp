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
from uuid import UUID


@mcp.tool(
    name="getOrgLicensesSummary",
    description="""Get the list of licenses""",
    tags={"orgs"},
    annotations={
        "title": "getOrgLicensesSummary",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getOrgLicensesSummary(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    ctx: Context | None = None,
) -> dict | list | str:
    """Get the list of licenses"""

    logger.debug("Tool getOrgLicensesSummary called")

    apisession, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.orgs.licenses.getOrgLicensesSummary(
        apisession,
        org_id=str(org_id),
    )
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
