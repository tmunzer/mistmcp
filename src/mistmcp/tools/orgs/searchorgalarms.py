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
from enum import Enum



mcp = get_mcp()

if not mcp:
    raise RuntimeError(
        "MCP instance not found. Make sure to initialize the MCP server before defining tools."
    )



class Group(Enum):
    INFRASTRUCTURE = "infrastructure"
    MARVIS = "marvis"
    SECURITY = "security"
    NONE = None

class Severity(Enum):
    CRITICAL = "critical"
    INFO = "info"
    WARN = "warn"
    NONE = None



@mcp.tool(
    enabled=True,
    name = "searchOrgAlarms",
    description = """Search Org Alarms""",
    tags = {"orgs"},
    annotations = {
        "title": "searchOrgAlarms",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchOrgAlarms(
    
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    site_id: Annotated[Optional[UUID | None], Field(description="""Site ID""")] = None,
    group: Annotated[Optional[Group | None], Field(description="""Alarm group. enum: `infrastructure`, `marvis`, `security`""")] = Group.NONE,
    severity: Annotated[Optional[Severity | None], Field(description="""Severity of the alarm. enum: `critical`, `info`, `warn`""")] = Severity.NONE,
    type: Annotated[Optional[str | None], Field(description="""Type of the alarm. Accepts multiple values separated by comma. Use [List Alarm Definitions](/#operations/listAlarmDefinitions) to get the list of possible alarm types.""")] = None,
    ack_admin_name: Annotated[Optional[str | None], Field(description="""Name of the admins who have acked the alarms; accepts multiple values separated by comma""")] = None,
    acked: Optional[bool | None] = None,
    start: Annotated[Optional[str | None], Field(description="""Start time (epoch timestamp in seconds, or relative string like '-1d', '-1w')""")] = None,
    end: Annotated[Optional[str | None], Field(description="""End time (epoch timestamp in seconds, or relative string like '-1d', '-2h', 'now')""")] = None,
    duration: Annotated[Optional[str | None], Field(description="""Duration like 7d, 2w""")] = None,
    limit: Optional[int | None] = None,
    sort: Annotated[Optional[str | None], Field(description="""On which field the list should be sorted, -prefix represents DESC order""")] = None,
    search_after: Annotated[Optional[str | None], Field(description="""Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed.""")] = None,
) -> dict|list:
    """Search Org Alarms"""

    apisession = get_apisession()
    data = {}
    
    
    response = mistapi.api.v1.orgs.alarms.searchOrgAlarms(
            apisession,
            org_id=str(org_id),
            site_id=str(site_id) if site_id else None,
            group=group.value if group else None,
            severity=severity.value if severity else None,
            type=type if type else None,
            ack_admin_name=ack_admin_name if ack_admin_name else None,
            acked=acked if acked else None,
            start=start if start else None,
            end=end if end else None,
            duration=duration if duration else None,
            limit=limit if limit else None,
            sort=sort if sort else None,
            search_after=search_after if search_after else None,
    )
    await process_response(response)
    
    data = response.data


    return data
