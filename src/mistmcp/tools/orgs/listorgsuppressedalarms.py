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

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


class Scope(Enum):
    ORG = "org"
    SITE = "site"


@mcp.tool(
    name="listOrgSuppressedAlarms",
    description="""Get List of Org Alarms Currently Suppressed""",
    tags={"orgs"},
    annotations={
        "title": "listOrgSuppressedAlarms",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def listOrgSuppressedAlarms(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    scope: Annotated[
        Optional[Scope | None],
        Field(description="""Returns both scopes if not specified"""),
    ] = Scope.SITE,
    ctx: Context | None = None,
) -> dict | list | str:
    """Get List of Org Alarms Currently Suppressed"""

    apisession, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.orgs.alarmtemplates.listOrgSuppressedAlarms(
        apisession,
        org_id=str(org_id),
        scope=scope.value if scope else Scope.SITE.value,
    )
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
