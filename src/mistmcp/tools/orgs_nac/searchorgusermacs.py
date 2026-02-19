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
from mistmcp.server import get_mcp

from pydantic import Field
from typing import Annotated, Optional, List
from uuid import UUID


mcp = get_mcp()

if not mcp:
    raise RuntimeError(
        "MCP instance not found. Make sure to initialize the MCP server before defining tools."
    )


@mcp.tool(
    name="searchOrgUserMacs",
    description="""Search Org User MACs""",
    tags={"orgs_nac"},
    annotations={
        "title": "searchOrgUserMacs",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchOrgUserMacs(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    mac: Annotated[
        Optional[str | None], Field(description="""Partial/full MAC address""")
    ] = None,
    labels: Annotated[
        Optional[List[str] | None],
        Field(description="""Optional, array of strings of labels"""),
    ] = None,
    limit: Optional[int | None] = None,
    page: Annotated[Optional[int | None], Field(ge=1)] = None,
    sort: Annotated[
        Optional[str | None],
        Field(
            description="""On which field the list should be sorted, -prefix represents DESC order"""
        ),
    ] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """Search Org User MACs"""

    apisession, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.orgs.usermacs.searchOrgUserMacs(
        apisession,
        org_id=str(org_id),
        mac=mac if mac else None,
        labels=labels if labels else None,
        limit=limit if limit else None,
        page=page if page else None,
        sort=sort if sort else None,
    )
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
