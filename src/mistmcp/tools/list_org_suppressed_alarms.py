"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import mistapi
from fastmcp import Context
from fastmcp.exceptions import ToolError
from mistmcp.request_processor import get_apisession
from mistmcp.response_processor import process_response, handle_network_error
from mistmcp.response_formatter import format_response
from mistmcp.server import mcp
from mistmcp.logger import logger

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


class Scope(Enum):
    ORG = "org"
    SITE = "site"


@mcp.tool(
    name="mist_list_org_suppressed_alarms",
    description="""Get List of Org Alarms Currently Suppressed""",
    tags={"orgs"},
    annotations={
        "title": "List org suppressed alarms",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def list_org_suppressed_alarms(
    org_id: Annotated[UUID, Field(description="""Organization ID""")],
    scope: Annotated[
        Optional[Scope], Field(description="""Returns both scopes if not specified""")
    ] = Scope.SITE,
    ctx: Context | None = None,
) -> dict | list | str:
    """Get List of Org Alarms Currently Suppressed"""

    logger.debug("Tool list_org_suppressed_alarms called")

    apisession, response_format = await get_apisession()

    try:
        response = mistapi.api.v1.orgs.alarmtemplates.listOrgSuppressedAlarms(
            apisession,
            org_id=str(org_id),
            scope=scope.value if scope else Scope.SITE.value,
        )
        await process_response(response)
    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
