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
from fastmcp.server.dependencies import get_context, get_http_request
from fastmcp.exceptions import ToolError, ClientError, NotFoundError
from starlette.requests import Request
from mistmcp.config import config
from mistmcp.server_factory import mcp_instance
# from mistmcp.server_factory import mcp

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


mcp = mcp_instance.get()


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


class Auth_state(Enum):
    AUTHENTICATED = "authenticated"
    AUTHENTICATING = "authenticating"
    HELD = "held"
    INIT = "init"
    NONE = None


class Type(Enum):
    SWITCH = "switch"
    GATEWAY = "gateway"
    ALL = "all"


@mcp.tool(
    enabled=False,
    name="searchOrgSwOrGwPorts",
    description="""Search Switch / Gateway Ports""",
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
    full_duplex: Annotated[
        Optional[bool | None], Field(description="""Indicates full or half duplex""")
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
    poe_priority: Annotated[
        Optional[Poe_priority | None], Field(description="""PoE priority.""")
    ] = Poe_priority.NONE,
    poe_mode: Annotated[
        Optional[str | None],
        Field(description="""POE mode depending on class E.g. '802.3at'"""),
    ] = None,
    poe_on: Annotated[
        Optional[bool | None], Field(description="""Is the device attached to POE""")
    ] = None,
    port_id: Annotated[
        Optional[str | None], Field(description="""Interface name""")
    ] = None,
    port_mac: Annotated[
        Optional[str | None], Field(description="""Interface mac address""")
    ] = None,
    power_draw: Annotated[
        Optional[float | None],
        Field(
            description="""Amount of power being used by the interface at the time the command is executed. Unit in watts."""
        ),
    ] = None,
    tx_pkts: Annotated[
        Optional[int | None], Field(description="""Output packets""")
    ] = None,
    rx_pkts: Annotated[
        Optional[int | None], Field(description="""Input packets""")
    ] = None,
    rx_bytes: Annotated[
        Optional[int | None], Field(description="""Input bytes""")
    ] = None,
    tx_bps: Annotated[
        Optional[int | None], Field(description="""Output rate""")
    ] = None,
    rx_bps: Annotated[Optional[int | None], Field(description="""Input rate""")] = None,
    tx_errors: Annotated[
        Optional[int | None], Field(description="""Output errors""")
    ] = None,
    rx_errors: Annotated[
        Optional[int | None], Field(description="""Input errors""")
    ] = None,
    tx_mcast_pkts: Annotated[
        Optional[int | None], Field(description="""Multicast output packets""")
    ] = None,
    tx_bcast_pkts: Annotated[
        Optional[int | None], Field(description="""Broadcast output packets""")
    ] = None,
    rx_mcast_pkts: Annotated[
        Optional[int | None], Field(description="""Multicast input packets""")
    ] = None,
    rx_bcast_pkts: Annotated[
        Optional[int | None], Field(description="""Broadcast input packets""")
    ] = None,
    speed: Annotated[Optional[int | None], Field(description="""Port speed""")] = None,
    mac_limit: Annotated[
        Optional[int | None],
        Field(description="""Limit on number of dynamically learned macs"""),
    ] = None,
    mac_count: Annotated[
        Optional[int | None],
        Field(description="""Number of mac addresses in the forwarding table"""),
    ] = None,
    up: Annotated[
        Optional[bool | None], Field(description="""Indicates if interface is up""")
    ] = None,
    stp_state: Annotated[
        Optional[Stp_state | None], Field(description="""If `up`==`true`""")
    ] = Stp_state.NONE,
    stp_role: Annotated[
        Optional[Stp_role | None], Field(description="""If `up`==`true`""")
    ] = Stp_role.NONE,
    auth_state: Annotated[
        Optional[Auth_state | None],
        Field(description="""If `up`==`true` && has Authenticator role"""),
    ] = Auth_state.NONE,
    optics_bias_current: Annotated[
        Optional[float | None],
        Field(description="""Bias current of the optics in mA"""),
    ] = None,
    optics_tx_power: Annotated[
        Optional[float | None],
        Field(description="""Transmit power of the optics in dBm"""),
    ] = None,
    optics_rx_power: Annotated[
        Optional[float | None],
        Field(description="""Receive power of the optics in dBm"""),
    ] = None,
    optics_module_temperature: Annotated[
        Optional[float | None],
        Field(description="""Temperature of the optics module in Celsius"""),
    ] = None,
    optics_module_voltage: Annotated[
        Optional[float | None],
        Field(description="""Voltage of the optics module in mV"""),
    ] = None,
    type: Annotated[
        Optional[Type | None],
        Field(description="""Type of device. enum: `switch`, `gateway`, `all`"""),
    ] = Type.ALL,
    limit: Optional[int | None] = None,
    start: Annotated[
        Optional[str | None],
        Field(
            description="""Start time (epoch timestamp in seconds, or relative string like '-1d', '-1w')"""
        ),
    ] = None,
    end: Annotated[
        Optional[str | None],
        Field(
            description="""End time (epoch timestamp in seconds, or relative string like '-1d', '-2h', 'now')"""
        ),
    ] = None,
    duration: Annotated[
        Optional[str | None], Field(description="""Duration like 7d, 2w""")
    ] = None,
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
) -> dict | list:
    """Search Switch / Gateway Ports"""

    ctx = get_context()
    if config.transport_mode == "http":
        try:
            request: Request = get_http_request()
            cloud = request.query_params.get("cloud", None)
            apitoken = request.headers.get("X-Authorization", None)
        except NotFoundError as exc:
            raise ClientError(
                "HTTP request context not found. Are you using HTTP transport?"
            ) from exc
        if not cloud or not apitoken:
            raise ClientError(
                "Missing required parameters: 'cloud' and 'X-Authorization' header"
            )
    else:
        apitoken = config.mist_apitoken
        cloud = config.mist_host

    if not apitoken:
        raise ClientError(
            "Missing required parameter: 'X-Authorization' header or mist_apitoken in config"
        )
    if not cloud:
        raise ClientError(
            "Missing required parameter: 'cloud' query parameter or mist_host in config"
        )

    apisession = mistapi.APISession(
        host=cloud,
        apitoken=apitoken,
    )

    response = mistapi.api.v1.orgs.stats.searchOrgSwOrGwPorts(
        apisession,
        org_id=str(org_id),
        full_duplex=full_duplex if full_duplex else None,
        mac=mac if mac else None,
        neighbor_mac=neighbor_mac if neighbor_mac else None,
        neighbor_port_desc=neighbor_port_desc if neighbor_port_desc else None,
        neighbor_system_name=neighbor_system_name if neighbor_system_name else None,
        poe_disabled=poe_disabled if poe_disabled else None,
        poe_priority=poe_priority.value if poe_priority else None,
        poe_mode=poe_mode if poe_mode else None,
        poe_on=poe_on if poe_on else None,
        port_id=port_id if port_id else None,
        port_mac=port_mac if port_mac else None,
        power_draw=power_draw if power_draw else None,
        tx_pkts=tx_pkts if tx_pkts else None,
        rx_pkts=rx_pkts if rx_pkts else None,
        rx_bytes=rx_bytes if rx_bytes else None,
        tx_bps=tx_bps if tx_bps else None,
        rx_bps=rx_bps if rx_bps else None,
        tx_errors=tx_errors if tx_errors else None,
        rx_errors=rx_errors if rx_errors else None,
        tx_mcast_pkts=tx_mcast_pkts if tx_mcast_pkts else None,
        tx_bcast_pkts=tx_bcast_pkts if tx_bcast_pkts else None,
        rx_mcast_pkts=rx_mcast_pkts if rx_mcast_pkts else None,
        rx_bcast_pkts=rx_bcast_pkts if rx_bcast_pkts else None,
        speed=speed if speed else None,
        mac_limit=mac_limit if mac_limit else None,
        mac_count=mac_count if mac_count else None,
        up=up if up else None,
        stp_state=stp_state.value if stp_state else None,
        stp_role=stp_role.value if stp_role else None,
        auth_state=auth_state.value if auth_state else None,
        optics_bias_current=optics_bias_current if optics_bias_current else None,
        optics_tx_power=optics_tx_power if optics_tx_power else None,
        optics_rx_power=optics_rx_power if optics_rx_power else None,
        optics_module_temperature=optics_module_temperature
        if optics_module_temperature
        else None,
        optics_module_voltage=optics_module_voltage if optics_module_voltage else None,
        type=type.value if type else Type.ALL.value,
        limit=limit if limit else None,
        start=start if start else None,
        end=end if end else None,
        duration=duration if duration else None,
        sort=sort if sort else None,
        search_after=search_after if search_after else None,
    )

    if response.status_code != 200:
        api_error = {"status_code": response.status_code, "message": ""}
        if response.data:
            # await ctx.error(f"Got HTTP{response.status_code} with details {response.data}")
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
                "Not found. The API endpoint doesn't exist or resource doesn't exist"
            )
        elif response.status_code == 429:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps(
                "Too Many Request. The API Token used for the request reached the 5000 API Calls per hour threshold"
            )
        raise ToolError(api_error)

    return response.data
