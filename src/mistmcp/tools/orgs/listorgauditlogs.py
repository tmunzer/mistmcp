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
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


class Sort(Enum):
    _TIMESTAMP = "_timestamp"
    ADMIN_ID = "admin_id"
    SITE_ID = "site_id"
    TIMESTAMP = "timestamp"
    NONE = None


@mcp.tool(
    name="listOrgAuditLogs",
    description="""Get List of change logs for the current Org""",
    tags={"orgs"},
    annotations={
        "title": "listOrgAuditLogs",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def listOrgAuditLogs(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    site_id: Annotated[Optional[UUID | None], Field(description="""Site id""")] = None,
    admin_name: Annotated[
        Optional[str | None], Field(description="""Admin name or email""")
    ] = None,
    message: Annotated[Optional[str | None], Field(description="""Message""")] = None,
    sort: Annotated[
        Optional[Sort | None], Field(description="""Sort order""")
    ] = Sort.NONE,
    start: Annotated[
        Optional[str | None],
        Field(
            description="""Start time (epoch timestamp in seconds, or relative string like '-1d', '-1w')"""
        ),
    ] = None,
    end: Annotated[
        Optional[str | None],
        Field(
            description="""End time (epoch timestamp in seconds, or relative string like '-1d', '-2h', 'now')"""
        ),
    ] = None,
    duration: Annotated[
        Optional[str | None], Field(description="""Duration like 7d, 2w""")
    ] = None,
    limit: Optional[int | None] = None,
    page: Annotated[Optional[int | None], Field(ge=1)] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """Get List of change logs for the current Org"""

    logger.debug("Tool listOrgAuditLogs called")

    apisession, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.orgs.logs.listOrgAuditLogs(
        apisession,
        org_id=str(org_id),
        site_id=str(site_id) if site_id else None,
        admin_name=admin_name if admin_name else None,
        message=message if message else None,
        sort=sort.value if sort else None,
        start=start if start else None,
        end=end if end else None,
        duration=duration if duration else None,
        limit=limit if limit else None,
        page=page if page else None,
    )
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
