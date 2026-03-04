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
    name="mist_search_alarms",
    description="""Search Alarms in an organization or site, with optional filters for alarm type, severity, and time range""",
    tags={"events"},
    annotations={
        "title": "Search alarms",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def search_alarms(
    org_id: Annotated[UUID, Field(description="""Organization ID""")],
    scope: Annotated[
        Scope,
        Field(
            description="""Whether to search for alarms in the entire organization or a specific site. If `site` is selected, the `site_id` parameter is required"""
        ),
    ],
    site_id: Annotated[Optional[UUID], Field(description="""Site ID""")],
    group: Annotated[
        Optional[str],
        Field(
            description="""Alarm group. enum: `infrastructure`, `marvis`, `security`.  The `marvis` group is used to retrieve AI-driven network issue detections.  Known Marvis alarm types include: `bad_cable`, `bad_wan_uplink`, `dns_failure`,  `arp_failure`, `auth_failure`, `dhcp_failure`, `missing_vlan`,  `negotiation_mismatch`, `port_flap`. Results include resolution status  (`status`, `resolved_time`) and affected entity details.'"""
        ),
    ],
    severity: Annotated[
        Optional[str],
        Field(
            description="""Severity of the alarm. enum: `critical`, `major`, `minor`, `warn`, `info`"""
        ),
    ],
    alarm_type: Annotated[
        Optional[str],
        Field(
            description="""Comma separated list of types of the alarm. IMPORTANT: use the `mist_get_constants` tool to get the list of possible alarm types"""
        ),
    ],
    acked: Annotated[
        Optional[bool],
        Field(
            description="""Whether to filter for acknowledged (true) or unacknowledged (false) alarms"""
        ),
    ],
    start: Annotated[
        Optional[int], Field(description="""Start of time range (epoch seconds)""")
    ],
    end: Annotated[
        Optional[int], Field(description="""End of time range (epoch seconds)""")
    ],
    limit: Annotated[
        int, Field(description="""Max number of results per page""", default=20)
    ] = 20,
    ctx: Context | None = None,
) -> dict | list | str:
    """Search Alarms in an organization or site, with optional filters for alarm type, severity, and time range"""

    logger.debug("Tool search_alarms called")

    apisession, response_format = await get_apisession()

    try:
        object_type = scope

        if object_type.value == "site":
            if not site_id:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": '`site_id` parameter is required when `scope` is "site".',
                    }
                )

        match object_type.value:
            case "org":
                response = mistapi.api.v1.orgs.alarms.searchOrgAlarms(
                    apisession,
                    org_id=str(org_id),
                    group=group if group else None,
                    severity=severity if severity else None,
                    type=alarm_type if alarm_type else None,
                    acked=acked if acked else None,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    limit=limit,
                )
                await process_response(response)
            case "site":
                response = mistapi.api.v1.sites.alarms.searchSiteAlarms(
                    apisession,
                    site_id=str(site_id),
                    group=group if group else None,
                    severity=severity if severity else None,
                    type=alarm_type if alarm_type else None,
                    acked=acked if acked else None,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    limit=limit,
                )
                await process_response(response)

            case _:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Scope]}",
                    }
                )

    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
