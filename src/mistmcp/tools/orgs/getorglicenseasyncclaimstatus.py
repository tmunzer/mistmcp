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
from fastmcp.exceptions import ToolError
from mistmcp.request_processor import get_apisession
from mistmcp.response_processor import process_response
from mistmcp.server import get_mcp

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID


mcp = get_mcp()

if not mcp:
    raise RuntimeError(
        "MCP instance not found. Make sure to initialize the MCP server before defining tools."
    )


@mcp.tool(
    enabled=True,
    name="GetOrgLicenseAsyncClaimStatus",
    description="""Get Processing Status for Async Claim""",
    tags={"orgs"},
    annotations={
        "title": "GetOrgLicenseAsyncClaimStatus",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def GetOrgLicenseAsyncClaimStatus(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    detail: Annotated[
        Optional[bool | None], Field(description="""Request license details""")
    ] = None,
) -> dict | list:
    """Get Processing Status for Async Claim"""

    apisession = get_apisession()
    data = {}

    response = mistapi.api.v1.orgs.claim.GetOrgLicenseAsyncClaimStatus(
        apisession,
        org_id=str(org_id),
        detail=detail if detail else None,
    )
    await process_response(response)

    data = response.data

    return data
