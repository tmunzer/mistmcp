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
from enum import Enum
from uuid import UUID


class Scope(Enum):
    SELF = "self"
    ORG = "org"


@mcp.tool(
    name="listAuditLogs",
    description="""This tool can be used to retrieve audit logs for the current account or an organization.""",
    tags={"events"},
    annotations={
        "title": "listAuditLogs",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def listAuditLogs(
    scope: Annotated[
        Scope,
        Field(
            description="""Whether to retrieve audit logs for the account or a specific organization. If `org` is selected, the `org_id` parameter is required."""
        ),
    ],
    org_id: Annotated[
        Optional[UUID | None],
        Field(description="""ID of the organization to retrieve audit logs for."""),
    ] = None,
    start_time: Annotated[
        Optional[str | None],
        Field(
            description="""Start time (epoch timestamp in seconds, or relative string like '-1d', '-1w')"""
        ),
    ] = None,
    end_time: Annotated[
        Optional[str | None],
        Field(
            description="""End time (epoch timestamp in seconds, or relative string like '-1d', '-2h', 'now')"""
        ),
    ] = None,
    limit: Annotated[
        Optional[int | None],
        Field(
            description="""Maximum number of audit entries to retrieve. If not specified, the API will return up to 100 entries (maximum allowed is 1000)."""
        ),
    ] = None,
    message: Annotated[
        Optional[str | None],
        Field(
            description="""Message to filter audit logs by (partial search). If not specified, logs will not be filtered by message."""
        ),
    ] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """This tool can be used to retrieve audit logs for the current account or an organization."""

    logger.debug("Tool listAuditLogs called")

    apisession, response_format = get_apisession()
    data = {}

    object_type = scope

    if object_type.value == "org":
        if not org_id:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`org_id` parameter is required when `object_type` is "org".',
                }
            )

    match object_type.value:
        case "self":
            response = mistapi.api.v1.self.logs.listSelfAuditLogs(
                apisession,
                start=str(start_time) if start_time else None,
                end=str(end_time) if end_time else None,
                message=str(message) if message else None,
                limit=limit if limit else None,
            )
            await process_response(response)
            data = response.data
        case "org":
            response = mistapi.api.v1.orgs.logs.listOrgAuditLogs(
                apisession,
                org_id=str(org_id),
                start=str(start_time) if start_time else None,
                end=str(end_time) if end_time else None,
                message=str(message) if message else None,
                limit=limit if limit else None,
            )
            await process_response(response)
            data = response.data

        case _:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Scope]}",
                }
            )

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
