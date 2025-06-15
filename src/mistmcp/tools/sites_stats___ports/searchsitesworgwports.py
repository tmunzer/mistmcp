""" "
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import json
import mistapi
from fastmcp.server.dependencies import get_context, get_http_request
from fastmcp.exceptions import ToolError
from starlette.requests import Request
from mistmcp.server_factory import _CURRENT_MCP_INSTANCE as mcp
from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


class Device_type(Enum):
    AP = "ap"
    BLE = "ble"
    GATEWAY = "gateway"
    MXEDGE = "mxedge"
    NAC = "nac"
    SWITCH = "switch"
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
    ROOT = "root"
    ROOT_PREVENTED = "root-prevented"
    NONE = None


class Auth_state(Enum):
    AUTHENTICATED = "authenticated"
    AUTHENTICATING = "authenticating"
    HELD = "held"
    INIT = "init"
    NONE = None


@mcp.tool(
    enabled=True,
    name="searchSiteSwOrGwPorts",
    description="""Search Switch / Gateway Ports""",
    tags={"Sites Stats - Ports"},
    annotations={
        "title": "searchSiteSwOrGwPorts",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchSiteSwOrGwPorts(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    full_duplex: Annotated[
        Optional[bool], Field(description="""Indicates full or half duplex""")
    ] = None,
    disabled: Annotated[
        Optional[bool], Field(description="""Indicates if interface is disabled""")
    ] = None,
    mac: Annotated[Optional[str], Field(description="""Device identifier""")] = None,
    device_type: Annotated[
        Device_type, Field(description="""Device type""")
    ] = Device_type.NONE,
    neighbor_mac: Annotated[
        Optional[str],
        Field(description="""Chassis identifier of the chassis type listed"""),
    ] = None,
    neighbor_port_desc: Annotated[
        Optional[str],
        Field(
            description="""Description supplied by the system on the interface E.g. 'GigabitEthernet2/0/39'"""
        ),
    ] = None,
    neighbor_system_name: Annotated[
        Optional[str],
        Field(
            description="""Name supplied by the system on the interface E.g. neighbor system name E.g. 'Kumar-Acc-SW.mist.local'"""
        ),
    ] = None,
    poe_disabled: Annotated[
        Optional[bool], Field(description="""Is the POE configured not be disabled.""")
    ] = None,
    poe_mode: Annotated[
        Optional[str],
        Field(description="""POE mode depending on class E.g. '802.3at'"""),
    ] = None,
    poe_on: Annotated[
        Optional[bool], Field(description="""Is the device attached to POE""")
    ] = None,
    port_id: Annotated[Optional[str], Field(description="""Interface name""")] = None,
    port_mac: Annotated[
        Optional[str], Field(description="""Interface mac address""")
    ] = None,
    power_draw: Annotated[
        Optional[float],
        Field(
            description="""Amount of power being used by the interface at the time the command is executed. Unit in watts."""
        ),
    ] = None,
    tx_pkts: Annotated[Optional[int], Field(description="""Output packets""")] = None,
    rx_pkts: Annotated[Optional[int], Field(description="""Input packets""")] = None,
    rx_bytes: Annotated[Optional[int], Field(description="""Input bytes""")] = None,
    tx_bps: Annotated[Optional[int], Field(description="""Output rate""")] = None,
    rx_bps: Annotated[Optional[int], Field(description="""Input rate""")] = None,
    tx_errors: Annotated[Optional[int], Field(description="""Output errors""")] = None,
    rx_errors: Annotated[Optional[int], Field(description="""Input errors""")] = None,
    tx_mcast_pkts: Annotated[
        Optional[int], Field(description="""Multicast output packets""")
    ] = None,
    tx_bcast_pkts: Annotated[
        Optional[int], Field(description="""Broadcast output packets""")
    ] = None,
    rx_mcast_pkts: Annotated[
        Optional[int], Field(description="""Multicast input packets""")
    ] = None,
    rx_bcast_pkts: Annotated[
        Optional[int], Field(description="""Broadcast input packets""")
    ] = None,
    speed: Annotated[Optional[int], Field(description="""Port speed""")] = None,
    mac_limit: Annotated[
        Optional[int],
        Field(description="""Limit on number of dynamically learned macs"""),
    ] = None,
    mac_count: Annotated[
        Optional[int],
        Field(description="""Number of mac addresses in the forwarding table"""),
    ] = None,
    up: Annotated[
        Optional[bool], Field(description="""Indicates if interface is up""")
    ] = None,
    active: Annotated[
        Optional[bool],
        Field(description="""Indicates if interface is active/inactive"""),
    ] = None,
    jitter: Annotated[
        Optional[float], Field(description="""Last sampled jitter of the interface""")
    ] = None,
    loss: Annotated[
        Optional[float], Field(description="""Last sampled loss of the interface""")
    ] = None,
    latency: Annotated[
        Optional[float], Field(description="""Last sampled latency of the interface""")
    ] = None,
    stp_state: Annotated[
        Stp_state, Field(description="""If `up`==`true`""")
    ] = Stp_state.NONE,
    stp_role: Annotated[
        Stp_role, Field(description="""If `up`==`true`""")
    ] = Stp_role.NONE,
    xcvr_part_number: Annotated[
        Optional[str],
        Field(description="""Optic Slot Partnumber, Check for null/empty"""),
    ] = None,
    auth_state: Annotated[
        Auth_state, Field(description="""If `up`==`true` && has Authenticator role""")
    ] = Auth_state.NONE,
    lte_imsi: Annotated[
        Optional[str], Field(description="""LTE IMSI value, Check for null/empty""")
    ] = None,
    lte_iccid: Annotated[
        Optional[str], Field(description="""LTE ICCID value, Check for null/empty""")
    ] = None,
    lte_imei: Annotated[
        Optional[str], Field(description="""LTE IMEI value, Check for null/empty""")
    ] = None,
    limit: Annotated[int, Field(default=100)] = 100,
    start: Annotated[
        Optional[int],
        Field(
            description="""Start datetime, can be epoch or relative time like -1d, -1w; -1d if not specified"""
        ),
    ] = None,
    end: Annotated[
        Optional[int],
        Field(
            description="""End datetime, can be epoch or relative time like -1d, -2h; now if not specified"""
        ),
    ] = None,
    duration: Annotated[
        str, Field(description="""Duration like 7d, 2w""", default="1d")
    ] = "1d",
) -> dict:
    """Search Switch / Gateway Ports"""

    ctx = get_context()
    request: Request = get_http_request()
    cloud = request.query_params.get("cloud", None)
    apitoken = request.headers.get("X-Authorization", None)
    apisession = mistapi.APISession(
        host=cloud,
        apitoken=apitoken,
    )

    response = mistapi.api.v1.sites.stats.searchSiteSwOrGwPorts(
        apisession,
        site_id=str(site_id),
        full_duplex=full_duplex,
        disabled=disabled,
        mac=mac,
        device_type=device_type.value,
        neighbor_mac=neighbor_mac,
        neighbor_port_desc=neighbor_port_desc,
        neighbor_system_name=neighbor_system_name,
        poe_disabled=poe_disabled,
        poe_mode=poe_mode,
        poe_on=poe_on,
        port_id=port_id,
        port_mac=port_mac,
        power_draw=power_draw,
        tx_pkts=tx_pkts,
        rx_pkts=rx_pkts,
        rx_bytes=rx_bytes,
        tx_bps=tx_bps,
        rx_bps=rx_bps,
        tx_errors=tx_errors,
        rx_errors=rx_errors,
        tx_mcast_pkts=tx_mcast_pkts,
        tx_bcast_pkts=tx_bcast_pkts,
        rx_mcast_pkts=rx_mcast_pkts,
        rx_bcast_pkts=rx_bcast_pkts,
        speed=speed,
        mac_limit=mac_limit,
        mac_count=mac_count,
        up=up,
        active=active,
        jitter=jitter,
        loss=loss,
        latency=latency,
        stp_state=stp_state.value,
        stp_role=stp_role.value,
        xcvr_part_number=xcvr_part_number,
        auth_state=auth_state.value,
        lte_imsi=lte_imsi,
        lte_iccid=lte_iccid,
        lte_imei=lte_imei,
        limit=limit,
        start=start,
        end=end,
        duration=duration,
    )

    if response.status_code != 200:
        api_error = {"status_code": response.status_code, "message": ""}
        if response.data:
            await ctx.error(
                f"Got HTTP{response.status_code} with details {response.data}"
            )
            api_error["message"] = json.dumps(response.data)
        elif response.status_code == 400:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps(
                "Bad Request. The API endpoint exists but its syntax/payload is incorrect, detail may be given"
            )
        elif response.status_code == 401:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps("Unauthorized")
        elif response.status_code == 403:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps("Unauthorized")
        elif response.status_code == 401:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps("Permission Denied")
        elif response.status_code == 404:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps(
                "Not found. The API endpoint doesn’t exist or resource doesn’t exist"
            )
        elif response.status_code == 429:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps(
                "Too Many Request. The API Token used for the request reached the 5000 API Calls per hour threshold"
            )
        raise ToolError(api_error)

    return response.data
