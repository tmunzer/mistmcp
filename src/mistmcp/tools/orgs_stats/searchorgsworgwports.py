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


class Device_type(Enum):
    SWITCH = "switch"
    GATEWAY = "gateway"
    ALL = "all"


class Auth_state(Enum):
    AUTHENTICATED = "authenticated"
    AUTHENTICATING = "authenticating"
    HELD = "held"
    INIT = "init"
    NONE = None


class Poe_priority(Enum):
    LOW = "low"
    HIGH = "high"
    NONE = None


class Stp_state(Enum):
    BLOCKING = "blocking"
    DISABLED = "disabled"
    FORWARDING = "forwarding"
    LEARNING = "learning"
    LISTENING = "listening"
    NONE = None


class Stp_role(Enum):
    ALTERNATE = "alternate"
    BACKUP = "backup"
    DESIGNATED = "designated"
    DISABLED = "disabled"
    ROOT = "root"
    ROOT_PREVENTED = "root_prevented"
    NONE = None


@mcp.tool(
    name="searchOrgSwOrGwPorts",
    description="""Search Switch / Gateway Ports Stats.Returns a list of switch/gateway ports stats that match the search criteria.The response provide current/last port status and statistics within the hour.Traffic information (Tx/Rx) are cumulative counters since the last device reboot.""",
    tags={"orgs_stats"},
    annotations={
        "title": "searchOrgSwOrGwPorts",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchOrgSwOrGwPorts(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    device_type: Annotated[
        Optional[Device_type | None],
        Field(description="""Type of device. enum: `switch`, `gateway`, `all`"""),
    ] = Device_type.ALL,
    auth_state: Annotated[
        Optional[Auth_state | None],
        Field(description="""If `up`==`true` && has Authenticator role"""),
    ] = Auth_state.NONE,
    full_duplex: Annotated[
        Optional[bool | None], Field(description="""Indicates full or half duplex""")
    ] = None,
    lte_imsi: Annotated[
        Optional[str | None],
        Field(description="""LTE IMSI value, Check for null/empty"""),
    ] = None,
    lte_iccid: Annotated[
        Optional[str | None],
        Field(description="""LTE ICCID value, Check for null/empty"""),
    ] = None,
    lte_imei: Annotated[
        Optional[str | None],
        Field(description="""LTE IMEI value, Check for null/empty"""),
    ] = None,
    mac: Annotated[
        Optional[str | None], Field(description="""Device identifier""")
    ] = None,
    neighbor_mac: Annotated[
        Optional[str | None],
        Field(description="""Chassis identifier of the chassis type listed"""),
    ] = None,
    neighbor_port_desc: Annotated[
        Optional[str | None],
        Field(
            description="""Description supplied by the system on the interface E.g. 'GigabitEthernet2/0/39'"""
        ),
    ] = None,
    neighbor_system_name: Annotated[
        Optional[str | None],
        Field(
            description="""Name supplied by the system on the interface E.g. neighbor system name E.g. 'Kumar-Acc-SW.mist.local'"""
        ),
    ] = None,
    poe_disabled: Annotated[
        Optional[bool | None],
        Field(description="""Is the POE configured not be disabled."""),
    ] = None,
    poe_mode: Annotated[
        Optional[str | None],
        Field(description="""POE mode depending on class E.g. '802.3at'"""),
    ] = None,
    poe_on: Annotated[
        Optional[bool | None], Field(description="""Is the device attached to POE""")
    ] = None,
    poe_priority: Annotated[
        Optional[Poe_priority | None], Field(description="""PoE priority.""")
    ] = Poe_priority.NONE,
    port_id: Annotated[
        Optional[str | None], Field(description="""Interface name""")
    ] = None,
    port_mac: Annotated[
        Optional[str | None], Field(description="""Interface mac address""")
    ] = None,
    speed: Annotated[Optional[int | None], Field(description="""Port speed""")] = None,
    stp_state: Annotated[
        Optional[Stp_state | None], Field(description="""If `up`==`true`""")
    ] = Stp_state.NONE,
    stp_role: Annotated[
        Optional[Stp_role | None], Field(description="""If `up`==`true`""")
    ] = Stp_role.NONE,
    up: Annotated[
        Optional[bool | None], Field(description="""Indicates if interface is up""")
    ] = None,
    xcvr_part_number: Annotated[
        Optional[str | None],
        Field(description="""Optic Slot Partnumber, Check for null/empty"""),
    ] = None,
    limit: Optional[int | None] = None,
    sort: Annotated[
        Optional[str | None],
        Field(
            description="""On which field the list should be sorted, -prefix represents DESC order"""
        ),
    ] = None,
    search_after: Annotated[
        Optional[str | None],
        Field(
            description="""Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed."""
        ),
    ] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """Search Switch / Gateway Ports Stats.Returns a list of switch/gateway ports stats that match the search criteria.The response provide current/last port status and statistics within the hour.Traffic information (Tx/Rx) are cumulative counters since the last device reboot."""

    apisession, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.orgs.stats.searchOrgSwOrGwPorts(
        apisession,
        org_id=str(org_id),
        device_type=device_type.value if device_type else Device_type.ALL.value,
        auth_state=auth_state.value if auth_state else None,
        full_duplex=full_duplex if full_duplex else None,
        lte_imsi=lte_imsi if lte_imsi else None,
        lte_iccid=lte_iccid if lte_iccid else None,
        lte_imei=lte_imei if lte_imei else None,
        mac=mac if mac else None,
        neighbor_mac=neighbor_mac if neighbor_mac else None,
        neighbor_port_desc=neighbor_port_desc if neighbor_port_desc else None,
        neighbor_system_name=neighbor_system_name if neighbor_system_name else None,
        poe_disabled=poe_disabled if poe_disabled else None,
        poe_mode=poe_mode if poe_mode else None,
        poe_on=poe_on if poe_on else None,
        poe_priority=poe_priority.value if poe_priority else None,
        port_id=port_id if port_id else None,
        port_mac=port_mac if port_mac else None,
        speed=speed if speed else None,
        stp_state=stp_state.value if stp_state else None,
        stp_role=stp_role.value if stp_role else None,
        up=up if up else None,
        xcvr_part_number=xcvr_part_number if xcvr_part_number else None,
        limit=limit if limit else None,
        sort=sort if sort else None,
        search_after=search_after if search_after else None,
    )
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
