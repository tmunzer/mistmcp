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
    SUPPRESSED = "suppressed"


@mcp.tool(
    name="mist_search_alarms",
    description="""Search for raised alarms in an organization or site with optional filtering. 
  
Scopes:
- `org`: Search all alarms across the organization
- `site`: Search alarms in a specific site (requires `site_id`)
- `suppressed`: View temporarily disabled alarms across the organization

Alarm groups: `infrastructure` (network device/connectivity issues), `marvis` (AI-driven network detections), `security` (security events)

Common Marvis alarm types: `bad_cable`, `bad_wan_uplink`, `dns_failure`, `arp_failure`, `auth_failure`, `dhcp_failure`, `missing_vlan`, `negotiation_mismatch`, `port_flap`

For a complete list of alarm types, use `mist_get_constants` with `object_type=alarm_definitions`.""",
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
            description="""Search scope: `org` (organization-wide), `site` (specific site, requires site_id), or `suppressed` (disabled alarms)"""
        ),
    ],
    site_id: Annotated[Optional[UUID], Field(description="""Site ID""")],
    group: Annotated[
        Optional[str],
        Field(
            description="""Only for org/site scope. Alarm group. enum: `infrastructure`, `marvis`, `security`.  The `marvis` group is used to retrieve AI-driven network issue detections."""
        ),
    ],
    severity: Annotated[
        Optional[str],
        Field(
            description="""Only for org/site scope.Severity of the alarm. enum: `critical`, `major`, `minor`, `warn`, `info`"""
        ),
    ],
    alarm_type: Annotated[
        Optional[str],
        Field(
            description="""Only for org/site scope. Comma separated list of types of the alarm (e.g., 'bad_cable,auth_failure'). IMPORTANT: use the `mist_get_constants` tool with `object_type=alarm_definitions`to get the list of possible alarm types"""
        ),
    ],
    acked: Annotated[
        Optional[bool],
        Field(
            description="""Only for org/site scope. Whether to filter for acknowledged (true) or unacknowledged (false) alarms"""
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
) -> dict | list | str:
    """Search for raised alarms in an organization or site with optional filtering.

    Scopes:
    - `org`: Search all alarms across the organization
    - `site`: Search alarms in a specific site (requires `site_id`)
    - `suppressed`: View temporarily disabled alarms across the organization

    Alarm groups: `infrastructure` (network device/connectivity issues), `marvis` (AI-driven network detections), `security` (security events)

    Common Marvis alarm types: `bad_cable`, `bad_wan_uplink`, `dns_failure`, `arp_failure`, `auth_failure`, `dhcp_failure`, `missing_vlan`, `negotiation_mismatch`, `port_flap`

    For a complete list of alarm types, use `mist_get_constants` with `object_type=alarm_definitions`."""

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

        if group and scope.value not in ["org", "site"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`group` parameter can only be used when `scope` is in "org", "site".',
                }
            )

        if severity and scope.value not in ["org", "site"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`severity` parameter can only be used when `scope` is in "org", "site".',
                }
            )

        if alarm_type and scope.value not in ["org", "site"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`alarm_type` parameter can only be used when `scope` is in "org", "site".',
                }
            )

        if acked and scope.value not in ["org", "site"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`acked` parameter can only be used when `scope` is in "org", "site".',
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
            case "suppressed":
                response = mistapi.api.v1.orgs.alarmtemplates.listOrgSuppressedAlarms(
                    apisession, org_id=str(org_id)
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
