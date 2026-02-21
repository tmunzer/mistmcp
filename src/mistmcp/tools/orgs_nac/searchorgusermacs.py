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
from typing import Annotated, Optional, List
from uuid import UUID


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
    org_id: Annotated[UUID, Field(description="""Organization ID""")],
    mac: Annotated[
        Optional[str | None], Field(description="""Partial/full MAC address""")
    ] = None,
    labels: Annotated[
        Optional[List[str] | None],
        Field(description="""Optional, array of strings of labels"""),
    ] = None,
    limit: Annotated[
        int, Field(description="""Max number of results per page""", default=100)
    ] = 100,
    page: Annotated[
        int, Field(description="""Page number for pagination""", ge=1, default=1)
    ] = 1,
    sort: Annotated[Optional[str | None], Field(description="""Sort field""")] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """Search Org User MACs"""

    logger.debug("Tool searchOrgUserMacs called")

    apisession, response_format = get_apisession()

    response = mistapi.api.v1.orgs.usermacs.searchOrgUserMacs(
        apisession,
        org_id=str(org_id),
        mac=mac if mac else None,
        labels=labels if labels else None,
        limit=limit,
        page=page,
        sort=sort if sort else None,
    )
    await process_response(response)

    return format_response(response, response_format)
