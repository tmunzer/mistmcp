"""Events, alarms, and audit-log search facade tool."""

from enum import Enum
from typing import Annotated
from uuid import UUID

import mistapi
from fastmcp.exceptions import ToolError
from fastmcp.tools import ToolResult
from pydantic import Field

from mistmcp.logger import logger
from mistmcp.request_processor import get_apisession
from mistmcp.response_formatter import format_response
from mistmcp.response_processor import handle_network_error, process_response
from mistmcp.server import mcp
from mistmcp.tools._facade import arguments, internal_tool, run_internal_tool


class ActivityType(Enum):
    EVENT = "event"
    ALARM = "alarm"
    SUPPRESSED_ALARM = "suppressed_alarm"
    AUDIT = "audit"


class SearchType(Enum):
    EVENT = "event"
    ALARM = "alarm"
    SUPPRESSED_ALARM = "suppressed_alarm"


class EventSource(Enum):
    DEVICE = "device"
    MXEDGE = "mxedge"
    WAN_CLIENT = "wan_client"
    WIRELESS_CLIENT = "wireless_client"
    NAC_CLIENT = "nac_client"
    ROAMING = "roaming"
    ROGUE = "rogue"


async def search_events(
    search_type: Annotated[
        SearchType,
        Field(
            description="Type of event-like data to search: `event`, `alarm`, or `suppressed_alarm`"
        ),
    ],
    org_id: Annotated[UUID, Field(description="Organization ID")],
    event_source: Annotated[
        EventSource,
        Field(
            description="Required when search_type is `event`. Event source type: device, mxedge, wan_client, wireless_client, nac_client, roaming (requires site_id), or rogue (requires site_id)",
            default=None,
        ),
    ],
    event_type: Annotated[
        str,
        Field(
            description="Only for search_type=event. Comma-separated event types to filter by. Use `mist_describe(subject=constant)` to discover the constant for the selected event_source",
            default=None,
        ),
    ],
    site_id: Annotated[
        UUID,
        Field(
            description="Site ID. For search_type=alarm, providing site_id searches site alarms; omitting it searches org alarms. Required for event_source=roaming or rogue. Optional for other event sources to narrow results to a site",
            default=None,
        ),
    ],
    mac: Annotated[
        str,
        Field(
            description="Only for search_type=event. MAC address filter for device, mxedge, WAN client, NAC client, or rogue events",
            default=None,
        ),
    ],
    text: Annotated[
        str,
        Field(
            description="Only for search_type=event with event_source=device or nac_client. Text search in event details",
            default=None,
        ),
    ],
    ssid: Annotated[
        str,
        Field(
            description="Only for search_type=event with event_source=wireless_client, nac_client, or rogue. SSID filter",
            default=None,
        ),
    ],
    group: Annotated[
        str,
        Field(
            description="Only for search_type=alarm. Alarm group: `infrastructure`, `marvis`, or `security`",
            default=None,
        ),
    ],
    severity: Annotated[
        str,
        Field(
            description="Only for search_type=alarm. Alarm severity: `critical`, `major`, `minor`, `warn`, or `info`",
            default=None,
        ),
    ],
    alarm_type: Annotated[
        str,
        Field(
            description="Only for search_type=alarm. Comma-separated alarm types (e.g., `bad_cable,auth_failure`). Use `mist_describe(subject=constant, name=alarm_definitions)` to discover available alarm types",
            default=None,
        ),
    ],
    acked: Annotated[
        bool,
        Field(
            description="Only for search_type=alarm. Filter acknowledged (true) or unacknowledged (false) alarms",
            default=None,
        ),
    ],
    start: Annotated[
        int,
        Field(
            description="Start of time range (epoch seconds). Used for search_type=event or alarm; ignored for suppressed_alarm",
            default=None,
        ),
    ],
    end: Annotated[
        int,
        Field(
            description="End of time range (epoch seconds). Used for search_type=event or alarm; ignored for suppressed_alarm",
            default=None,
        ),
    ],
    limit: Annotated[
        int,
        Field(
            description="Max number of results per page. Used for search_type=event or alarm; ignored for suppressed_alarm",
            default=20,
        ),
    ],
) -> dict | list | str:
    """Search for Mist events and alarms across an organization or site."""
    logger.debug("Tool search_events called")
    logger.debug(
        "Input Parameters: search_type: %s, org_id: %s, event_source: %s, event_type: %s, site_id: %s, mac: %s, text: %s, ssid: %s, group: %s, severity: %s, alarm_type: %s, acked: %s, start: %s, end: %s, limit: %s",
        search_type,
        org_id,
        event_source,
        event_type,
        site_id,
        mac,
        text,
        ssid,
        group,
        severity,
        alarm_type,
        acked,
        start,
        end,
        limit,
    )
    apisession, response_format = await get_apisession()
    try:
        match search_type:
            case SearchType.EVENT:
                _validate_alarm_params_not_used(
                    group=group, severity=severity, alarm_type=alarm_type, acked=acked
                )
                response = await _search_event(
                    apisession=apisession,
                    org_id=org_id,
                    event_source=event_source,
                    event_type=event_type,
                    site_id=site_id,
                    mac=mac,
                    text=text,
                    ssid=ssid,
                    start=start,
                    end=end,
                    limit=limit if limit else 20,
                )
            case SearchType.ALARM:
                _validate_event_params_not_used(
                    event_source=event_source,
                    event_type=event_type,
                    mac=mac,
                    text=text,
                    ssid=ssid,
                )
                response = await _search_alarm(
                    apisession=apisession,
                    org_id=org_id,
                    site_id=site_id,
                    group=group,
                    severity=severity,
                    alarm_type=alarm_type,
                    acked=acked,
                    start=start,
                    end=end,
                    limit=limit if limit else 20,
                )
            case SearchType.SUPPRESSED_ALARM:
                _validate_event_params_not_used(
                    event_source=event_source,
                    event_type=event_type,
                    mac=mac,
                    text=text,
                    ssid=ssid,
                )
                _validate_alarm_params_not_used(
                    group=group, severity=severity, alarm_type=alarm_type, acked=acked
                )
                response = mistapi.api.v1.orgs.alarmtemplates.listOrgSuppressedAlarms(
                    apisession, org_id=str(org_id)
                )
                await process_response(response)
            case _:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": f"Invalid search_type: {search_type.value}. Valid values are: {[e.value for e in SearchType]}",
                    }
                )
    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)
    return format_response(response, response_format)


async def _search_event(
    apisession,
    org_id: UUID,
    event_source: EventSource | None,
    event_type: str | None,
    site_id: UUID | None,
    mac: str | None,
    text: str | None,
    ssid: str | None,
    start: int | None,
    end: int | None,
    limit: int,
):
    if not event_source:
        raise ToolError(
            {
                "status_code": 400,
                "message": "`event_source` is required when `search_type` is `event`.",
            }
        )
    if event_source in [EventSource.ROAMING, EventSource.ROGUE] and (not site_id):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"`site_id` parameter is required when `event_source` is `{event_source.value}`.",
            }
        )
    if text and event_source not in [EventSource.DEVICE, EventSource.NAC_CLIENT]:
        raise ToolError(
            {
                "status_code": 400,
                "message": '`text` parameter can only be used when `event_source` is in "device", "nac_client".',
            }
        )
    if ssid and event_source not in [
        EventSource.WIRELESS_CLIENT,
        EventSource.NAC_CLIENT,
        EventSource.ROGUE,
    ]:
        raise ToolError(
            {
                "status_code": 400,
                "message": '`ssid` parameter can only be used when `event_source` is in "wireless_client", "nac_client", "rogue".',
            }
        )
    match event_source:
        case EventSource.DEVICE:
            if site_id:
                response = mistapi.api.v1.sites.devices.searchSiteDeviceEvents(
                    apisession,
                    site_id=str(site_id),
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    type=str(event_type) if event_type else None,
                    mac=str(mac) if mac else None,
                    text=str(text) if text else None,
                    limit=limit,
                )
            else:
                response = mistapi.api.v1.orgs.devices.searchOrgDeviceEvents(
                    apisession,
                    org_id=str(org_id),
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    type=str(event_type) if event_type else None,
                    mac=str(mac) if mac else None,
                    text=str(text) if text else None,
                    limit=limit,
                )
        case EventSource.MXEDGE:
            mxedge_id = _mxedge_id_from_mac(mac)
            if site_id:
                response = mistapi.api.v1.sites.mxedges.searchSiteMistEdgeEvents(
                    apisession,
                    site_id=str(site_id),
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    type=str(event_type) if event_type else None,
                    mxedge_id=mxedge_id,
                    limit=limit,
                )
            else:
                response = mistapi.api.v1.orgs.mxedges.searchOrgMistEdgeEvents(
                    apisession,
                    org_id=str(org_id),
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    type=str(event_type) if event_type else None,
                    mxedge_id=mxedge_id,
                    limit=limit,
                )
        case EventSource.WAN_CLIENT:
            if site_id:
                response = mistapi.api.v1.sites.wan_clients.searchSiteWanClientEvents(
                    apisession,
                    site_id=str(site_id),
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    type=str(event_type) if event_type else None,
                    mac=str(mac) if mac else None,
                    limit=limit,
                )
            else:
                response = mistapi.api.v1.orgs.wan_clients.searchOrgWanClientEvents(
                    apisession,
                    org_id=str(org_id),
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    type=str(event_type) if event_type else None,
                    mac=str(mac) if mac else None,
                    limit=limit,
                )
        case EventSource.WIRELESS_CLIENT:
            if site_id:
                response = mistapi.api.v1.sites.clients.searchSiteWirelessClientEvents(
                    apisession,
                    site_id=str(site_id),
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    type=str(event_type) if event_type else None,
                    ssid=str(ssid) if ssid else None,
                    limit=limit,
                )
            else:
                response = mistapi.api.v1.orgs.clients.searchOrgWirelessClientEvents(
                    apisession,
                    org_id=str(org_id),
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    type=str(event_type) if event_type else None,
                    ssid=str(ssid) if ssid else None,
                    limit=limit,
                )
        case EventSource.NAC_CLIENT:
            if site_id:
                response = mistapi.api.v1.sites.nac_clients.searchSiteNacClientEvents(
                    apisession,
                    site_id=str(site_id),
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    type=str(event_type) if event_type else None,
                    mac=str(mac) if mac else None,
                    text=str(text) if text else None,
                    ssid=str(ssid) if ssid else None,
                    limit=limit,
                )
            else:
                response = mistapi.api.v1.orgs.nac_clients.searchOrgNacClientEvents(
                    apisession,
                    org_id=str(org_id),
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    type=str(event_type) if event_type else None,
                    mac=str(mac) if mac else None,
                    text=str(text) if text else None,
                    ssid=str(ssid) if ssid else None,
                    limit=limit,
                )
        case EventSource.ROAMING:
            response = mistapi.api.v1.sites.events.listSiteRoamingEvents(
                apisession,
                site_id=str(site_id),
                start=str(start) if start else None,
                end=str(end) if end else None,
                type=str(event_type) if event_type else None,
                limit=limit,
            )
        case EventSource.ROGUE:
            response = mistapi.api.v1.sites.rogues.searchSiteRogueEvents(
                apisession,
                site_id=str(site_id),
                start=str(start) if start else None,
                end=str(end) if end else None,
                type=str(event_type) if event_type else None,
                ssid=str(ssid) if ssid else None,
                ap_mac=str(mac) if mac else None,
                limit=limit,
            )
        case _:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": f"Invalid event_source: {event_source.value}. Valid values are: {[e.value for e in EventSource]}",
                }
            )
    await process_response(response)
    return response


def _mxedge_id_from_mac(mac: str | None) -> str | None:
    if not mac:
        return None
    normalized_mac = str(mac).replace(":", "").replace("-", "").replace(".", "").lower()
    if len(normalized_mac) != 12 or not all(
        (char in "0123456789abcdef" for char in normalized_mac)
    ):
        raise ToolError(
            {
                "status_code": 400,
                "message": "`mac` must be a 12-character MAC address when `event_source` is `mxedge`.",
            }
        )
    return f"00000000-0000-0000-1000-{normalized_mac}"


async def _search_alarm(
    apisession,
    org_id: UUID,
    site_id: UUID | None,
    group: str | None,
    severity: str | None,
    alarm_type: str | None,
    acked: bool | None,
    start: int | None,
    end: int | None,
    limit: int,
):
    if site_id:
        response = mistapi.api.v1.sites.alarms.searchSiteAlarms(
            apisession,
            site_id=str(site_id),
            group=group if group else None,
            severity=severity if severity else None,
            type=alarm_type if alarm_type else None,
            acked=acked if acked is not None else None,
            start=str(start) if start else None,
            end=str(end) if end else None,
            limit=limit,
        )
    else:
        response = mistapi.api.v1.orgs.alarms.searchOrgAlarms(
            apisession,
            org_id=str(org_id),
            group=group if group else None,
            severity=severity if severity else None,
            type=alarm_type if alarm_type else None,
            acked=acked if acked is not None else None,
            start=str(start) if start else None,
            end=str(end) if end else None,
            limit=limit,
        )
    await process_response(response)
    return response


def _validate_event_params_not_used(
    event_source: EventSource | None,
    event_type: str | None,
    mac: str | None,
    text: str | None,
    ssid: str | None,
) -> None:
    if event_source or event_type or mac or text or ssid:
        raise ToolError(
            {
                "status_code": 400,
                "message": "`event_source`, `event_type`, `mac`, `text`, and `ssid` can only be used when `search_type` is `event`.",
            }
        )


def _validate_alarm_params_not_used(
    group: str | None, severity: str | None, alarm_type: str | None, acked: bool | None
) -> None:
    if group or severity or alarm_type or (acked is not None):
        raise ToolError(
            {
                "status_code": 400,
                "message": "`group`, `severity`, `alarm_type`, and `acked` can only be used when `search_type` is `alarm`.",
            }
        )


class Scope(Enum):
    SELF = "self"
    ORG = "org"


async def search_audit_logs(
    scope: Annotated[
        Scope,
        Field(
            description="Whether to retrieve audit logs for the account or a specific organization. If `org` is selected, the `org_id` parameter is required"
        ),
    ],
    org_id: Annotated[UUID, Field(description="Organization ID", default=None)],
    start: Annotated[
        int, Field(description="Start of time range (epoch seconds)", default=None)
    ],
    end: Annotated[
        int, Field(description="End of time range (epoch seconds)", default=None)
    ],
    message: Annotated[
        str,
        Field(
            description="Message to filter audit logs by (partial search)", default=None
        ),
    ],
    limit: Annotated[
        int, Field(description="Max number of results per page", default=20)
    ] = 20,
) -> dict | list | str:
    """Search audit logs for the current account or an organization"""
    logger.debug("Tool search_audit_logs called")
    logger.debug(
        "Input Parameters: scope: %s, org_id: %s, start: %s, end: %s, message: %s, limit: %s",
        scope,
        org_id,
        start,
        end,
        message,
        limit,
    )
    apisession, response_format = await get_apisession()
    try:
        object_type = scope
        if object_type.value == "org":
            if not org_id:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": '`org_id` parameter is required when `scope` is "org".',
                    }
                )
        match object_type.value:
            case "self":
                response = mistapi.api.v1.self.logs.listSelfAuditLogs(
                    apisession,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    message=str(message) if message else None,
                    limit=limit,
                )
                await process_response(response)
            case "org":
                response = mistapi.api.v1.orgs.logs.listOrgAuditLogs(
                    apisession,
                    org_id=str(org_id),
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    message=str(message) if message else None,
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


AuditScope = Scope

_SEARCH_EVENTS = internal_tool(search_events)
_SEARCH_AUDIT_LOGS = internal_tool(search_audit_logs)


@mcp.tool(
    name="mist_search_activity",
    description="""Search Mist events, alarms, suppressed alarms, or audit logs.

For `activity_type=event`, provide `org_id` and `source`. Filter by `event_type`,
`site_id`, `mac`, `query`, or `ssid` where supported. `source` accepts device, mxedge,
wan_client, wireless_client, nac_client, roaming, or rogue; roaming and rogue require
`site_id`. `query` applies to device and NAC-client events. `ssid` applies to
wireless-client, NAC-client, and rogue events. Discover
valid event types with `mist_describe(subject=constant)` and the corresponding
device_events, mxedge_events, client_events, or nac_events constant.

For `activity_type=alarm`, provide `org_id`; add `site_id` for site rather than
organization alarms. Filter with `group`, `severity`, `alarm_type`, and `acked`.
Discover alarm types from the alarm_definitions constant. Suppressed alarms require
only `org_id`; event-only filters and time bounds do not apply to them.

For `activity_type=audit`, `scope=self` searches the current account and `scope=org`
requires `org_id`. If omitted, scope is inferred from whether `org_id` is supplied.
`query` filters the audit message. Event, alarm, and audit searches accept `start`,
`end`, and `limit` where applicable and may return `next` for pagination.""",
    tags={"events"},
    annotations={
        "title": "Search events and audit activity",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def search_activity(
    activity_type: Annotated[
        ActivityType, Field(description="Activity type to search.")
    ],
    org_id: Annotated[
        UUID,
        Field(
            description="Organization ID; optional only for self audit logs.",
            default=None,
        ),
    ] = None,
    site_id: Annotated[
        UUID,
        Field(
            description="Optional or required site scope, depending on source.",
            default=None,
        ),
    ] = None,
    source: Annotated[
        EventSource,
        Field(
            description="Event source; required for activity_type=event.", default=None
        ),
    ] = None,
    scope: Annotated[
        AuditScope, Field(description="Audit scope: self or org.", default=None)
    ] = None,
    query: Annotated[
        str, Field(description="Event text or audit-message filter.", default=None)
    ] = None,
    event_type: Annotated[
        str,
        Field(
            description="Comma-separated event types. Discover values with mist_describe.",
            default=None,
        ),
    ] = None,
    mac: Annotated[
        str,
        Field(description="Event device, client, MX Edge, or rogue MAC.", default=None),
    ] = None,
    ssid: Annotated[
        str,
        Field(
            description="Wireless-client, NAC-client, or rogue-event SSID.",
            default=None,
        ),
    ] = None,
    group: Annotated[
        str,
        Field(
            description="Alarm group: infrastructure, marvis, or security.",
            default=None,
        ),
    ] = None,
    severity: Annotated[
        str,
        Field(
            description="Alarm severity: critical, major, minor, warn, or info.",
            default=None,
        ),
    ] = None,
    alarm_type: Annotated[
        str,
        Field(
            description="Comma-separated alarm types. Discover values with mist_describe.",
            default=None,
        ),
    ] = None,
    acked: Annotated[
        bool,
        Field(
            description="Filter acknowledged or unacknowledged alarms.", default=None
        ),
    ] = None,
    start: Annotated[
        int, Field(description="Start time in epoch seconds.", default=None)
    ] = None,
    end: Annotated[
        int, Field(description="End time in epoch seconds.", default=None)
    ] = None,
    limit: Annotated[int, Field(description="Maximum results per page.")] = 20,
) -> ToolResult:
    if activity_type is ActivityType.AUDIT:
        audit_scope = scope or ("org" if org_id is not None else "self")
        return await run_internal_tool(
            _SEARCH_AUDIT_LOGS,
            arguments(
                {
                    "scope": audit_scope,
                    "org_id": org_id,
                    "message": query,
                    "start": start,
                    "end": end,
                    "limit": limit,
                }
            ),
        )
    if org_id is None:
        raise ToolError("org_id is required for event and alarm searches.")
    if activity_type is ActivityType.EVENT and source is None:
        raise ToolError("source is required for activity_type='event'.")
    return await run_internal_tool(
        _SEARCH_EVENTS,
        arguments(
            {
                "search_type": activity_type.value,
                "org_id": org_id,
                "event_source": source,
                "event_type": event_type,
                "site_id": site_id,
                "mac": mac,
                "text": query,
                "ssid": ssid,
                "group": group,
                "severity": severity,
                "alarm_type": alarm_type,
                "acked": acked,
                "start": start,
                "end": end,
                "limit": limit,
            }
        ),
    )
