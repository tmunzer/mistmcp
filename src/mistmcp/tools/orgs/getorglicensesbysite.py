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
from typing import Annotated
from uuid import UUID


mcp = get_mcp()

if not mcp:
    raise RuntimeError(
        "MCP instance not found. Make sure to initialize the MCP server before defining tools."
    )


@mcp.tool(
    enabled=True,
    name="getOrgLicensesBySite",
    description="""Get Licenses Usage by SitesThis shows license usage (i.e. needed) based on the features enabled for the site.""",
    tags={"orgs"},
    annotations={
        "title": "getOrgLicensesBySite",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getOrgLicensesBySite(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
) -> dict | list | str:
    """Get Licenses Usage by SitesThis shows license usage (i.e. needed) based on the features enabled for the site."""

    apisession, _, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.orgs.licenses.getOrgLicensesBySite(
        apisession,
        org_id=str(org_id),
    )
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
