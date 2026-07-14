"""Device and client search facade tool."""

from enum import Enum
from typing import Annotated, Optional
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


class AssetType(Enum):
    DEVICE = "device"
    WAN_CLIENT = "wan_client"
    WIRED_CLIENT = "wired_client"
    WIRELESS_CLIENT = "wireless_client"
    NAC_CLIENT = "nac_client"
    ORG_GUEST = "org_guest"
    SITE_GUEST = "site_guest"


class Device_type(Enum):
    AP = "ap"
    SWITCH = "switch"
    GATEWAY = "gateway"


class Status(Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


async def search_device(
    org_id: Annotated[UUID, Field(description="Organization ID")],
    site_id: Annotated[UUID, Field(description="Site ID", default=None)],
    serial: Annotated[
        str,
        Field(
            description="Serial number of the device to filter inventory by",
            default=None,
        ),
    ],
    model: Annotated[
        str,
        Field(
            description="Device model. Partial match allowed with wildcard * (e.g. `AP*` will match `AP43` and `AP41`)",
            default=None,
        ),
    ],
    mac: Annotated[
        str,
        Field(
            description="MAC address. Partial match allowed with wildcard * (e.g. `*5b35*` will match `5c5b350e0001` and `5c5b35000301`)",
            default=None,
        ),
    ],
    version: Annotated[
        str,
        Field(
            description="Firmware version of the device to filter inventory by",
            default=None,
        ),
    ],
    device_type: Annotated[
        Optional[Device_type],
        Field(description="Type of the device to filter inventory by", default=None),
    ],
    status: Annotated[
        Status,
        Field(
            description="Connection status of the device to filter inventory by",
            default=None,
        ),
    ],
    text: Annotated[
        str,
        Field(
            description="Text to search for in device attributes (name, serial number, MAC). Use the wildcard `*` for partial matches (e.g. `london` will match `london-1`, `london-2`, `my-london-device`...)",
            default=None,
        ),
    ],
    limit: Annotated[
        int, Field(description="Max number of results per page", default=20)
    ],
) -> dict | list | str:
    """Search a network device in the Organization Inventory. This tool provides a consolidated view of all devices within an organization, even those not assigned to any site. This can be used to quickly search for a device across the whole organization. It allows filtering by various attributes such as serial number, model, MAC address, firmware version, device type, and connection status. This tool is useful for quickly finding specific devices or getting an overview of the organization's inventory without needing to query each site separately."""
    logger.debug("Tool search_device called")
    logger.debug(
        "Input Parameters: org_id: %s, site_id: %s, serial: %s, model: %s, mac: %s, version: %s, device_type: %s, status: %s, text: %s, limit: %s",
        org_id,
        site_id,
        serial,
        model,
        mac,
        version,
        device_type,
        status,
        text,
        limit,
    )
    apisession, response_format = await get_apisession()
    try:
        response = mistapi.api.v1.orgs.inventory.searchOrgInventory(
            apisession,
            org_id=str(org_id),
            serial=serial if serial else None,
            model=model if model else None,
            type=device_type.value if device_type else None,
            mac=mac if mac else None,
            site_id=str(site_id) if site_id else None,
            version=version if version else None,
            text=text if text else None,
            status=status.value if status else None,
            limit=limit,
        )
        await process_response(response)
        if isinstance(response.data, dict):
            for device in response.data.get("results", []):
                if device.get("vc_mac"):
                    device["device_id"] = f"00000000-0000-0000-1000-{device['vc_mac']}"
                else:
                    device["device_id"] = f"00000000-0000-0000-1000-{device['mac']}"
    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)
    return format_response(response, response_format)


class Client_type(Enum):
    WAN = "wan"
    WIRED = "wired"
    WIRELESS = "wireless"
    NAC = "nac"
    ORG_GUEST = "org_guest"
    SITE_GUEST = "site_guest"


class Band(Enum):
    B24 = "24"
    B5 = "5"
    B6 = "6"


async def search_client(
    client_type: Annotated[
        Client_type,
        Field(
            description="Type of client: WAN, wired, wireless, NAC, Org guest, or Site guest"
        ),
    ],
    org_id: Annotated[UUID, Field(description="Organization ID")],
    site_id: Annotated[
        UUID,
        Field(
            description="Site ID. Required for site_guest, optional for other client types",
            default=None,
        ),
    ],
    device_mac: Annotated[
        str,
        Field(
            description="Partial / full MAC Address of the Access Point or the Switch. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `aabbcc*` and `*bbcc*` match `aabbccddeeff`). Suffix-only wildcards (e.g. `*bccddeeff`) are not supported. Not applicable for WAN clients or Org/Site Guests",
            default=None,
        ),
    ],
    band: Annotated[
        Band,
        Field(
            description="802.11 band (24 or 5 or 6 GHz). Wireless clients only",
            default=None,
        ),
    ],
    mac: Annotated[
        str,
        Field(
            description="Partial / full Client MAC Address. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `aabbcc*` and `*bbcc*` match `aabbccddeeff`). Suffix-only wildcards (e.g. `*bccddeeff`) are not supported",
            default=None,
        ),
    ],
    hostname: Annotated[
        str,
        Field(
            description="Partial / full Client hostname. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `everest*` and `*rest*` match `my-everest-client`). Suffix-only wildcards (e.g. `*everest`) are not supported. Not applicable for wired clients or Org/Site Guests",
            default=None,
        ),
    ],
    ip: Annotated[
        str,
        Field(
            description="Partial / full Client IP Address.  Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `10.100.10.*` and  `*100.10.*` match `10.100.10.54`). Suffix-only wildcards (e.g. `*.54`) are not supported. Not applicable for NAC clients or Org/Site Guests",
            default=None,
        ),
    ],
    ssid: Annotated[
        str,
        Field(
            description="SSID name to filter by. Only applicable for wireless clients, Guests, and NAC clients",
            default=None,
        ),
    ],
    text: Annotated[
        str,
        Field(
            description="Free text search in client details (supports * wildcard). Not applicable for WAN clients or Org/Site Guests",
            default=None,
        ),
    ],
    start: Annotated[
        int, Field(description="Start of time range (epoch seconds)", default=None)
    ],
    end: Annotated[
        int, Field(description="End of time range (epoch seconds)", default=None)
    ],
    limit: Annotated[
        int, Field(description="Max number of results per page", default=20)
    ],
) -> dict | list | str:
    """Search for clients across an organization or specific site.
    Supports searching by client type (WAN, wired, wireless, NAC), MAC address, hostname, IP address, and more.
    Use wildcards (*) for partial matches on MAC address, hostname, IP, and text fields.
    Different client types support different filter parameters - the tool will validate compatibility."""
    logger.debug("Tool search_client called")
    logger.debug(
        "Input Parameters: client_type: %s, org_id: %s, site_id: %s, device_mac: %s, band: %s, mac: %s, hostname: %s, ip: %s, ssid: %s, text: %s, start: %s, end: %s, limit: %s",
        client_type,
        org_id,
        site_id,
        device_mac,
        band,
        mac,
        hostname,
        ip,
        ssid,
        text,
        start,
        end,
        limit,
    )
    apisession, response_format = await get_apisession()
    try:
        object_type = client_type
        if device_mac and client_type.value not in ["wireless", "wired"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`device_mac` parameter can only be used when `client_type` is in "wireless", "wired".',
                }
            )
        if band and client_type.value not in ["wireless"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`band` parameter can only be used when `client_type` is "wireless".',
                }
            )
        if hostname and client_type.value not in ["wireless", "nac", "wan"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`hostname` parameter can only be used when `client_type` is in "wireless", "nac", "wan".',
                }
            )
        if ip and client_type.value not in ["wan", "wired", "wireless"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`ip` parameter can only be used when `client_type` is in "wan", "wired", "wireless".',
                }
            )
        if ssid and client_type.value not in [
            "wireless",
            "org_guest",
            "site_guest",
            "nac",
        ]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`ssid` parameter can only be used when `client_type` is in "wireless", "org_guest", "site_guest", "nac".',
                }
            )
        if text and client_type.value not in ["wired", "wireless", "nac"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`text` parameter can only be used when `client_type` is in "wired", "wireless", "nac".',
                }
            )
        match object_type.value:
            case "wan":
                response = mistapi.api.v1.orgs.wan_clients.searchOrgWanClients(
                    apisession,
                    org_id=str(org_id),
                    site_id=str(site_id) if site_id else None,
                    mac=str(mac) if mac else None,
                    hostname=str(hostname) if hostname else None,
                    ip=str(ip) if ip else None,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    limit=limit,
                )
                await process_response(response)
            case "wired":
                response = mistapi.api.v1.orgs.wired_clients.searchOrgWiredClients(
                    apisession,
                    org_id=str(org_id),
                    site_id=str(site_id) if site_id else None,
                    device_mac=str(device_mac) if device_mac else None,
                    mac=str(mac) if mac else None,
                    ip=str(ip) if ip else None,
                    text=str(text) if text else None,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    limit=limit,
                )
                await process_response(response)
            case "wireless":
                response = mistapi.api.v1.orgs.clients.searchOrgWirelessClients(
                    apisession,
                    org_id=str(org_id),
                    site_id=str(site_id) if site_id else None,
                    ap=str(device_mac) if device_mac else None,
                    band=band.value if band else None,
                    ssid=str(ssid) if ssid else None,
                    mac=str(mac) if mac else None,
                    hostname=str(hostname) if hostname else None,
                    ip=str(ip) if ip else None,
                    text=str(text) if text else None,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    limit=limit,
                )
                await process_response(response)
            case "nac":
                response = mistapi.api.v1.orgs.nac_clients.searchOrgNacClients(
                    apisession,
                    org_id=str(org_id),
                    site_id=str(site_id) if site_id else None,
                    ssid=str(ssid) if ssid else None,
                    mac=str(mac) if mac else None,
                    hostname=str(hostname) if hostname else None,
                    text=str(text) if text else None,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    limit=limit,
                )
                await process_response(response)
            case "org_guest":
                if mac:
                    response = mistapi.api.v1.orgs.guests.getOrgGuestAuthorization(
                        apisession, org_id=str(org_id), guest_mac=str(mac)
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.guests.searchOrgGuestAuthorization(
                        apisession,
                        org_id=str(org_id),
                        ssid=str(ssid) if ssid else None,
                        start=str(start) if start else None,
                        end=str(end) if end else None,
                        limit=limit,
                    )
                    await process_response(response)
            case "site_guest":
                if not site_id:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": '`site_id` parameter is required when `client_type` is "site_guest".',
                        }
                    )
                if mac:
                    response = mistapi.api.v1.sites.guests.getSiteGuestAuthorization(
                        apisession, site_id=str(site_id), guest_mac=str(mac)
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.sites.guests.searchSiteGuestAuthorization(
                        apisession,
                        site_id=str(site_id),
                        ssid=str(ssid) if ssid else None,
                        start=str(start) if start else None,
                        end=str(end) if end else None,
                        limit=limit,
                    )
                    await process_response(response)
            case _:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Client_type]}",
                    }
                )
    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)
    return format_response(response, response_format)


DeviceType = Device_type
DeviceStatus = Status
ClientBand = Band

_SEARCH_DEVICE = internal_tool(search_device)
_SEARCH_CLIENT = internal_tool(search_client)


@mcp.tool(
    name="mist_search_assets",
    description="""Search Mist-managed devices, clients, or connected guest sessions.

`org_id` is required for every asset type. For `asset_type=device`, search the
organization inventory with `serial`, `model`,
`mac`, `version`, `device_type`, `status`, `text`, and optional `site_id`.
Returned inventory records include a normalized `device_id` for tools that require a
device UUID.

For client types, use `mac` for the client MAC. Wired and wireless clients also
support `device_mac`; wireless clients support `band`; WAN, wireless, and NAC
clients support `hostname` as applicable; WAN, wired, and wireless clients support
`ip`; wireless, NAC, and guest sessions support `ssid`. The underlying API validates
which filters apply to each client type. `site_guest` requires `site_id`; other client
types may use it to narrow the organization search. `start` and `end` bound client or
guest-session searches. Results use `limit` and may return `next` for pagination.

MAC, hostname, IP, model, and text searches support prefix (`value*`) or contains
(`*value*`) matching where documented; suffix-only wildcards are unsupported.
Without `mac`, `org_guest` and `site_guest` search connected captive-portal sessions;
their default time window is the last 24 hours. Supplying an exact `mac` retrieves
that guest's authorization. To list pre-created authorization records—including
records that let a MAC bypass the portal without an active connection—use
`mist_get_configuration` with `object_type=org_guest_authorizations` or
`object_type=site_guest_authorizations`.""",
    tags={"devices"},
    annotations={
        "title": "Search devices and clients",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def search_assets(
    asset_type: Annotated[
        AssetType, Field(description="Device or client subtype to search.")
    ],
    org_id: Annotated[UUID, Field(description="Organization ID.")],
    site_id: Annotated[
        UUID, Field(description="Optional site scope.", default=None)
    ] = None,
    text: Annotated[
        str,
        Field(description="Free-text or wildcard search when supported.", default=None),
    ] = None,
    serial: Annotated[
        str, Field(description="Device serial-number filter.", default=None)
    ] = None,
    model: Annotated[
        str,
        Field(
            description="Device model filter; supports wildcard matching.", default=None
        ),
    ] = None,
    version: Annotated[
        str, Field(description="Device firmware-version filter.", default=None)
    ] = None,
    device_type: Annotated[
        DeviceType,
        Field(
            description="Device inventory type: ap, switch, or gateway.", default=None
        ),
    ] = None,
    status: Annotated[
        DeviceStatus,
        Field(
            description="Device connection status: connected or disconnected.",
            default=None,
        ),
    ] = None,
    device_mac: Annotated[
        str,
        Field(
            description="AP or switch MAC serving a wired or wireless client.",
            default=None,
        ),
    ] = None,
    band: Annotated[
        ClientBand,
        Field(description="Wireless client band: 24, 5, or 6 GHz.", default=None),
    ] = None,
    hostname: Annotated[
        str, Field(description="Client hostname wildcard filter.", default=None)
    ] = None,
    ip: Annotated[
        str, Field(description="Client IP-address wildcard filter.", default=None)
    ] = None,
    ssid: Annotated[
        str,
        Field(description="Wireless, NAC, or guest-session SSID filter.", default=None),
    ] = None,
    mac: Annotated[
        str, Field(description="Device or client MAC filter.", default=None)
    ] = None,
    start: Annotated[
        int, Field(description="Client search start time.", default=None)
    ] = None,
    end: Annotated[
        int, Field(description="Client search end time.", default=None)
    ] = None,
    limit: Annotated[int, Field(description="Maximum results per page.")] = 20,
) -> ToolResult:
    if asset_type is AssetType.DEVICE:
        return await run_internal_tool(
            _SEARCH_DEVICE,
            arguments(
                {
                    "org_id": org_id,
                    "site_id": site_id,
                    "serial": serial,
                    "model": model,
                    "mac": mac,
                    "version": version,
                    "device_type": device_type,
                    "status": status,
                    "text": text,
                    "limit": limit,
                }
            ),
        )
    return await run_internal_tool(
        _SEARCH_CLIENT,
        arguments(
            {
                "client_type": asset_type.value.removesuffix("_client"),
                "org_id": org_id,
                "site_id": site_id,
                "device_mac": device_mac,
                "band": band,
                "mac": mac,
                "hostname": hostname,
                "ip": ip,
                "ssid": ssid,
                "text": text,
                "start": start,
                "end": end,
                "limit": limit,
            }
        ),
    )
