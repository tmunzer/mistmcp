"""NAC user-MAC and rogue-device search facade tool."""

from enum import Enum
from typing import Annotated, List
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


class SecuritySubject(Enum):
    NAC_USER_MAC = "nac_user_mac"
    ROGUE_DEVICE = "rogue_device"


async def search_nac_user_macs(
    org_id: Annotated[UUID, Field(description="Organization ID")],
    usermac_id: Annotated[
        str,
        Field(
            description="ID of the User MAC address to return details for. If specified, other filters are ignored and details for the specified User MAC address is returned if it exists",
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
    labels: Annotated[
        List[str],
        Field(
            description="Comma separated list of labels to filter NAC endpoints by. A NAC endpoint must have all the specified labels to be included in the results",
            default=None,
        ),
    ],
    limit: Annotated[
        int, Field(description="Max number of results per page", default=20)
    ],
) -> dict | list | str:
    """Search for NAC user MAC addresses in an organization or site, with optional filters for associated SSID and time range. User MACs are used to perform MAC Authentication with Juniper Mist NAC."""
    logger.debug("Tool search_nac_user_macs called")
    logger.debug(
        "Input Parameters: org_id: %s, usermac_id: %s, mac: %s, labels: %s, limit: %s",
        org_id,
        usermac_id,
        mac,
        labels,
        limit,
    )
    apisession, response_format = await get_apisession()
    try:
        if usermac_id:
            response = mistapi.api.v1.orgs.usermacs.getOrgUserMac(
                apisession, org_id=str(org_id), usermac_id=str(usermac_id)
            )
            await process_response(response)
        else:
            response = mistapi.api.v1.orgs.usermacs.searchOrgUserMacs(
                apisession,
                org_id=str(org_id),
                mac=str(mac) if mac else None,
                labels=labels if labels else None,
                limit=limit,
            )
            await process_response(response)
    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)
    return format_response(response, response_format)


class Rogue_type(Enum):
    AP = "ap"
    CLIENT = "client"


class Rogue_ap_type(Enum):
    HONEYPOT = "honeypot"
    LAN = "lan"
    OTHERS = "others"
    SPOOF = "spoof"


async def list_rogue_devices(
    site_id: Annotated[UUID, Field(description="Site ID")],
    rogue_type: Annotated[
        Rogue_type, Field(description="Type of rogue device to filter by")
    ],
    rogue_ap_type: Annotated[
        Rogue_ap_type,
        Field(
            description="Type of rogue AP to filter by. Only applicable when filtering for rogue APs",
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
    ] = 20,
) -> dict | list | str:
    """Retrieve a list of rogue devices (APs or clients) for a site, with optional filters for rogue AP type and time range"""
    logger.debug("Tool list_rogue_devices called")
    logger.debug(
        "Input Parameters: site_id: %s, rogue_type: %s, rogue_ap_type: %s, start: %s, end: %s, limit: %s",
        site_id,
        rogue_type,
        rogue_ap_type,
        start,
        end,
        limit,
    )
    apisession, response_format = await get_apisession()
    try:
        object_type = rogue_type
        if rogue_ap_type and rogue_type.value not in ["ap"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`rogue_ap_type` parameter can only be used when `rogue_type` is "ap".',
                }
            )
        match object_type.value:
            case "ap":
                response = mistapi.api.v1.sites.insights.listSiteRogueAPs(
                    apisession,
                    site_id=str(site_id),
                    type=rogue_ap_type.value if rogue_ap_type else None,
                    limit=limit,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                )
                await process_response(response)
            case "client":
                response = mistapi.api.v1.sites.insights.listSiteRogueClients(
                    apisession,
                    site_id=str(site_id),
                    limit=limit,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                )
                await process_response(response)
            case _:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Rogue_type]}",
                    }
                )
    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)
    return format_response(response, response_format)


RogueType = Rogue_type
RogueApType = Rogue_ap_type

_SEARCH_NAC_USER_MACS = internal_tool(search_nac_user_macs)
_LIST_ROGUE_DEVICES = internal_tool(list_rogue_devices)


@mcp.tool(
    name="mist_search_security",
    description="""Search NAC user-MAC records or site rogue devices.

For `subject=nac_user_mac`, provide `org_id`. Use `usermac_id` to retrieve one exact
record (other filters are then ignored), or search by wildcard `mac` and `labels`.
All supplied labels must match. NAC user MACs are endpoints used for MAC
authentication with Mist NAC.

For `subject=rogue_device`, provide `site_id` and `rogue_type`. Rogue AP searches
may be narrowed with `rogue_ap_type` (honeypot, lan, others, or spoof). Both rogue
AP and rogue-client searches accept `start`, `end`, and `limit`. Search results may
return `next` for pagination.""",
    tags={"orgs_nac"},
    annotations={
        "title": "Search NAC and rogue-device records",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def search_security(
    subject: Annotated[
        SecuritySubject, Field(description="Security record type to search.")
    ],
    org_id: Annotated[
        UUID, Field(description="Organization ID for NAC searches.", default=None)
    ] = None,
    site_id: Annotated[
        UUID, Field(description="Site ID for rogue-device searches.", default=None)
    ] = None,
    mac: Annotated[str, Field(description="NAC user MAC filter.", default=None)] = None,
    usermac_id: Annotated[
        str,
        Field(
            description="Exact NAC user-MAC record ID; when supplied, other NAC filters are ignored.",
            default=None,
        ),
    ] = None,
    labels: Annotated[
        list[str],
        Field(
            description="Labels that a NAC endpoint must contain in full.", default=None
        ),
    ] = None,
    rogue_type: Annotated[
        RogueType,
        Field(description="Rogue device type: ap or client.", default=None),
    ] = None,
    rogue_ap_type: Annotated[
        RogueApType,
        Field(
            description="Rogue AP classification; valid only when rogue_type=ap.",
            default=None,
        ),
    ] = None,
    start: Annotated[
        int, Field(description="Rogue search start time.", default=None)
    ] = None,
    end: Annotated[
        int, Field(description="Rogue search end time.", default=None)
    ] = None,
    limit: Annotated[int, Field(description="Maximum results per page.")] = 20,
) -> ToolResult:
    if subject is SecuritySubject.NAC_USER_MAC:
        if org_id is None:
            raise ToolError("org_id is required for subject='nac_user_mac'.")
        return await run_internal_tool(
            _SEARCH_NAC_USER_MACS,
            arguments(
                {
                    "org_id": org_id,
                    "usermac_id": usermac_id,
                    "mac": mac,
                    "labels": labels,
                    "limit": limit,
                }
            ),
        )
    if site_id is None:
        raise ToolError("site_id is required for subject='rogue_device'.")
    if rogue_type is None:
        raise ToolError("rogue_type is required for subject='rogue_device'.")
    return await run_internal_tool(
        _LIST_ROGUE_DEVICES,
        arguments(
            {
                "site_id": site_id,
                "start": start,
                "end": end,
                "limit": limit,
                "rogue_type": rogue_type,
                "rogue_ap_type": rogue_ap_type,
            }
        ),
    )
