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
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


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
    name="searchOrgAlarms",
    description="""Search Org Alarms""",
    tags={"orgs"},
    annotations={
        "title": "searchOrgAlarms",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchOrgAlarms(
    org_id: Annotated[UUID, Field(description="""Organization ID""")],
    site_id: Annotated[Optional[UUID | None], Field(description="""Site ID""")] = None,
    group: Annotated[
        Optional[Group | None],
        Field(
            description="""Alarm group. enum: `infrastructure`, `marvis`, `security`.  The `marvis` group is used to retrieve AI-driven network issue detections.  Known Marvis alarm types include: `bad_cable`, `bad_wan_uplink`, `dns_failure`,  `arp_failure`, `auth_failure`, `dhcp_failure`, `missing_vlan`,  `negotiation_mismatch`, `port_flap`. Results include resolution status  (`status`, `resolved_time`) and affected entity details.'"""
        ),
    ] = Group.NONE,
    severity: Annotated[
        Optional[Severity | None],
        Field(
            description="""Severity of the alarm. enum: `critical`, `info`, `warn`"""
        ),
    ] = Severity.NONE,
    type: Annotated[
        Optional[str | None],
        Field(
            description="""Type of the alarm. Accepts multiple values separated by comma. Use [List Alarm Definitions](/#operations/listAlarmDefinitions) to get the list of possible alarm types."""
        ),
    ] = None,
    ack_admin_name: Annotated[
        Optional[str | None],
        Field(
            description="""Name of the admins who have acked the alarms; accepts multiple values separated by comma"""
        ),
    ] = None,
    acked: Optional[bool | None] = None,
    start: Annotated[
        Optional[str | None],
        Field(description="""Start of time range (epoch seconds)"""),
    ] = None,
    end: Annotated[
        Optional[str | None], Field(description="""End of time range (epoch seconds)""")
    ] = None,
    duration: Annotated[
        Optional[str | None],
        Field(description="""Time range duration (e.g. 1d, 1h, 10m)"""),
    ] = None,
    limit: Annotated[
        int, Field(description="""Max number of results per page""", default=100)
    ] = 100,
    sort: Annotated[Optional[str | None], Field(description="""Sort field""")] = None,
    search_after: Annotated[
        Optional[str | None],
        Field(
            description="""Pagination cursor from '_next' URL of previous response"""
        ),
    ] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """Search Org Alarms"""

    logger.debug("Tool searchOrgAlarms called")

    apisession, response_format = get_apisession()

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
        limit=limit,
        sort=sort if sort else None,
        search_after=search_after if search_after else None,
    )
    await process_response(response)

    return format_response(response, response_format)
