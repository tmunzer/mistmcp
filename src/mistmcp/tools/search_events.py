"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import mistapi
from fastmcp.exceptions import ToolError
from mistmcp.request_processor import get_apisession
from mistmcp.response_processor import process_response, handle_network_error
from mistmcp.response_formatter import format_response
from mistmcp.server import mcp
from mistmcp.logger import logger

from pydantic import Field
from typing import Annotated
from enum import Enum
from uuid import UUID


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


@mcp.tool(
    name="mist_search_events",
    description="""Search for Mist events and alarms across an organization or site.

Use `search_type=event` to search event streams from devices, MX Edge instances, clients, roaming, or rogue APs.
Use `search_type=alarm` to search raised alarms. If `site_id` is provided, site alarms are searched; otherwise org alarms are searched.
Use `search_type=suppressed_alarm` to list temporarily disabled alarms for the organization.

For event types, use `mist_get_constants` with:
- `object_type=device_events` for device events
- `object_type=mxedge_events` for MX Edge events
- `object_type=client_events` for WAN/wireless client events
- `object_type=nac_events` for NAC client events

For alarm types, use `mist_get_constants` with `object_type=alarm_definitions`.""",
    tags={"events"},
    annotations={
        "title": "Search events",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def search_events(
    search_type: Annotated[
        SearchType,
        Field(
            description="""Type of event-like data to search: `event`, `alarm`, or `suppressed_alarm`"""
        ),
    ],
    org_id: Annotated[UUID, Field(description="""Organization ID""")],
    event_source: Annotated[
        EventSource,
        Field(
            description="""Required when search_type is `event`. Event source type: device, mxedge, wan_client, wireless_client, nac_client, roaming (requires site_id), or rogue (requires site_id)""",
            default=None,
        ),
    ],
    event_type: Annotated[
        str,
        Field(
            description="""Only for search_type=event. Comma-separated event types to filter by. Use `mist_get_constants` to discover available values for the selected event_source""",
            default=None,
        ),
    ],
    site_id: Annotated[
        UUID,
        Field(
            description="""Site ID. For search_type=alarm, providing site_id searches site alarms; omitting it searches org alarms. Required for event_source=roaming or rogue. Optional for other event sources to narrow results to a site""",
            default=None,
        ),
    ],
    mac: Annotated[
        str,
        Field(
            description="""Only for search_type=event. MAC address filter for device, mxedge, WAN client, NAC client, or rogue events""",
            default=None,
        ),
    ],
    text: Annotated[
        str,
        Field(
            description="""Only for search_type=event with event_source=device or nac_client. Text search in event details""",
            default=None,
        ),
    ],
    ssid: Annotated[
        str,
        Field(
            description="""Only for search_type=event with event_source=wireless_client, nac_client, or rogue. SSID filter""",
            default=None,
        ),
    ],
    group: Annotated[
        str,
        Field(
            description="""Only for search_type=alarm. Alarm group: `infrastructure`, `marvis`, or `security`""",
            default=None,
        ),
    ],
    severity: Annotated[
        str,
        Field(
            description="""Only for search_type=alarm. Alarm severity: `critical`, `major`, `minor`, `warn`, or `info`""",
            default=None,
        ),
    ],
    alarm_type: Annotated[
        str,
        Field(
            description="""Only for search_type=alarm. Comma-separated alarm types (e.g., `bad_cable,auth_failure`). Use `mist_get_constants` with `object_type=alarm_definitions` to discover available alarm types""",
            default=None,
        ),
    ],
    acked: Annotated[
        bool,
        Field(
            description="""Only for search_type=alarm. Filter acknowledged (true) or unacknowledged (false) alarms""",
            default=None,
        ),
    ],
    start: Annotated[
        int,
        Field(
            description="""Start of time range (epoch seconds). Used for search_type=event or alarm; ignored for suppressed_alarm""",
            default=None,
        ),
    ],
    end: Annotated[
        int,
        Field(
            description="""End of time range (epoch seconds). Used for search_type=event or alarm; ignored for suppressed_alarm""",
            default=None,
        ),
    ],
    limit: Annotated[
        int,
        Field(
            description="""Max number of results per page. Used for search_type=event or alarm; ignored for suppressed_alarm""",
            default=20,
        ),
    ] = 20,
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
                    limit=limit,
                )
            case SearchType.ALARM:
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
                    limit=limit,
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
                    group=group,
                    severity=severity,
                    alarm_type=alarm_type,
                    acked=acked,
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
    event_source: EventSource,
    event_type: str,
    site_id: UUID,
    mac: str,
    text: str,
    ssid: str,
    start: int,
    end: int,
    limit: int,
):
    if not event_source:
        raise ToolError(
            {
                "status_code": 400,
                "message": "`event_source` is required when `search_type` is `event`.",
            }
        )

    if event_source in [EventSource.ROAMING, EventSource.ROGUE] and not site_id:
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
            mxedge_id = f"00000000-0000-0000-1000-{str(mac)}" if mac else None
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


async def _search_alarm(
    apisession,
    org_id: UUID,
    site_id: UUID,
    group: str,
    severity: str,
    alarm_type: str,
    acked: bool,
    start: int,
    end: int,
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
    event_source: EventSource,
    event_type: str,
    mac: str,
    text: str,
    ssid: str,
) -> None:
    if event_source or event_type or mac or text or ssid:
        raise ToolError(
            {
                "status_code": 400,
                "message": "`event_source`, `event_type`, `mac`, `text`, and `ssid` can only be used when `search_type` is `event`.",
            }
        )


def _validate_alarm_params_not_used(
    group: str,
    severity: str,
    alarm_type: str,
    acked: bool,
) -> None:
    if group or severity or alarm_type or acked is not None:
        raise ToolError(
            {
                "status_code": 400,
                "message": "`group`, `severity`, `alarm_type`, and `acked` can only be used when `search_type` is `alarm`.",
            }
        )
