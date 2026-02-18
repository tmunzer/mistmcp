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



class Key_mgmt(Enum):
    WPA2_PSK = "WPA2_PSK"
    WPA2_PSK_CCMP = "WPA2_PSK_CCMP"
    WPA2_PSK_FT = "WPA2_PSK_FT"
    WPA2_PSK_SHA256 = "WPA2_PSK_SHA256"
    WPA3_EAP_SHA256 = "WPA3_EAP_SHA256"
    WPA3_EAP_SHA256_CCMP = "WPA3_EAP_SHA256_CCMP"
    WPA3_EAP_FT_GCMP256 = "WPA3_EAP_FT_GCMP256"
    WPA3_SAE_FT = "WPA3_SAE_FT"
    WPA3_SAE_PSK = "WPA3_SAE_PSK"
    NONE = None

class Proto(Enum):
    A = "a"
    AC = "ac"
    AX = "ax"
    B = "b"
    BE = "be"
    G = "g"
    N = "n"
    NONE = None

class Band(Enum):
    B24 = "24"
    B5 = "5"
    B6 = "6"
    NONE = None



@mcp.tool(
    enabled=True,
    name = "searchOrgWirelessClientEvents",
    description = """Get Org Clients Events""",
    tags = {"clients"},
    annotations = {
        "title": "searchOrgWirelessClientEvents",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchOrgWirelessClientEvents(
    
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    type: Annotated[Optional[str | None], Field(description="""See [List Device Events Definitions](/#operations/listDeviceEventsDefinitions)""")] = None,
    reason_code: Annotated[Optional[int | None], Field(description="""For assoc/disassoc events""")] = None,
    ssid: Annotated[Optional[str | None], Field(description="""SSID Name""")] = None,
    ap: Annotated[Optional[str | None], Field(description="""AP MAC""")] = None,
    key_mgmt: Annotated[Optional[Key_mgmt | None], Field(description="""Key Management Protocol, e.g. WPA2-PSK, WPA3-SAE, WPA2-Enterprise""")] = Key_mgmt.NONE,
    proto: Annotated[Optional[Proto | None], Field(description="""a / b / g / n / ac / ax""")] = Proto.NONE,
    band: Annotated[Optional[Band | None], Field(description="""802.11 Band""")] = Band.NONE,
    wlan_id: Annotated[Optional[UUID | None], Field(description="""WLAN_id""")] = None,
    nacrule_id: Annotated[Optional[UUID | None], Field(description="""Nacrule_id""")] = None,
    start: Annotated[Optional[str | None], Field(description="""Start time (epoch timestamp in seconds, or relative string like '-1d', '-1w')""")] = None,
    end: Annotated[Optional[str | None], Field(description="""End time (epoch timestamp in seconds, or relative string like '-1d', '-2h', 'now')""")] = None,
    duration: Annotated[Optional[str | None], Field(description="""Duration like 7d, 2w""")] = None,
    sort: Annotated[Optional[str | None], Field(description="""On which field the list should be sorted, -prefix represents DESC order""")] = None,
    limit: Optional[int | None] = None,
    search_after: Annotated[Optional[str | None], Field(description="""Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed.""")] = None,
) -> dict|list:
    """Get Org Clients Events"""

    apisession = get_apisession()
    data = {}
    
    
    response = mistapi.api.v1.orgs.clients.searchOrgWirelessClientEvents(
            apisession,
            org_id=str(org_id),
            type=type if type else None,
            reason_code=reason_code if reason_code else None,
            ssid=ssid if ssid else None,
            ap=ap if ap else None,
            key_mgmt=key_mgmt.value if key_mgmt else None,
            proto=proto.value if proto else None,
            band=band.value if band else None,
            wlan_id=str(wlan_id) if wlan_id else None,
            nacrule_id=str(nacrule_id) if nacrule_id else None,
            start=start if start else None,
            end=end if end else None,
            duration=duration if duration else None,
            sort=sort if sort else None,
            limit=limit if limit else None,
            search_after=search_after if search_after else None,
    )
    await process_response(response)
    
    data = response.data


    return data
