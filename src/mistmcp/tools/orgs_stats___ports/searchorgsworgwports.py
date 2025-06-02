""""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""
import json
import mistapi
from fastmcp.server.dependencies import get_context
from fastmcp.exceptions import ToolError
from mistmcp.__server import mcp
from mistmcp.__mistapi import apisession
from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum




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


def add_tool():
    mcp.add_tool(
        fn=searchOrgSwOrGwPorts,
        name="searchOrgSwOrGwPorts",
        description="""Search Switch / Gateway Ports""",
        tags={"Orgs Stats - Ports"},
        annotations={
            "title": "searchOrgSwOrGwPorts",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True
        }
    )

def remove_tool():
    mcp.remove_tool("searchOrgSwOrGwPorts")

async def searchOrgSwOrGwPorts(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    full_duplex: Annotated[Optional[bool], Field(description="""Indicates full or half duplex""")] | None = None,
    mac: Annotated[Optional[str], Field(description="""Device identifier""")] | None = None,
    neighbor_mac: Annotated[Optional[str], Field(description="""Chassis identifier of the chassis type listed""")] | None = None,
    neighbor_port_desc: Annotated[Optional[str], Field(description="""Description supplied by the system on the interface E.g. 'GigabitEthernet2/0/39'""")] | None = None,
    neighbor_system_name: Annotated[Optional[str], Field(description="""Name supplied by the system on the interface E.g. neighbor system name E.g. 'Kumar-Acc-SW.mist.local'""")] | None = None,
    poe_disabled: Annotated[Optional[bool], Field(description="""Is the POE configured not be disabled.""")] | None = None,
    poe_mode: Annotated[Optional[str], Field(description="""POE mode depending on class E.g. '802.3at'""")] | None = None,
    poe_on: Annotated[Optional[bool], Field(description="""Is the device attached to POE""")] | None = None,
    port_id: Annotated[Optional[str], Field(description="""Interface name""")] | None = None,
    port_mac: Annotated[Optional[str], Field(description="""Interface mac address""")] | None = None,
    power_draw: Annotated[Optional[float], Field(description="""Amount of power being used by the interface at the time the command is executed. Unit in watts.""")] | None = None,
    tx_pkts: Annotated[Optional[int], Field(description="""Output packets""")] | None = None,
    rx_pkts: Annotated[Optional[int], Field(description="""Input packets""")] | None = None,
    rx_bytes: Annotated[Optional[int], Field(description="""Input bytes""")] | None = None,
    tx_bps: Annotated[Optional[int], Field(description="""Output rate""")] | None = None,
    rx_bps: Annotated[Optional[int], Field(description="""Input rate""")] | None = None,
    tx_errors: Annotated[Optional[int], Field(description="""Output errors""")] | None = None,
    rx_errors: Annotated[Optional[int], Field(description="""Input errors""")] | None = None,
    tx_mcast_pkts: Annotated[Optional[int], Field(description="""Multicast output packets""")] | None = None,
    tx_bcast_pkts: Annotated[Optional[int], Field(description="""Broadcast output packets""")] | None = None,
    rx_mcast_pkts: Annotated[Optional[int], Field(description="""Multicast input packets""")] | None = None,
    rx_bcast_pkts: Annotated[Optional[int], Field(description="""Broadcast input packets""")] | None = None,
    speed: Annotated[Optional[int], Field(description="""Port speed""")] | None = None,
    mac_limit: Annotated[Optional[int], Field(description="""Limit on number of dynamically learned macs""")] | None = None,
    mac_count: Annotated[Optional[int], Field(description="""Number of mac addresses in the forwarding table""")] | None = None,
    up: Annotated[Optional[bool], Field(description="""Indicates if interface is up""")] | None = None,
    stp_state: Annotated[Stp_state, Field(description="""If `up`==`true`""")] = Stp_state.NONE,
    stp_role: Annotated[Stp_role, Field(description="""If `up`==`true`""")] = Stp_role.NONE,
    auth_state: Annotated[Auth_state, Field(description="""If `up`==`true` && has Authenticator role""")] = Auth_state.NONE,
    limit: Annotated[int, Field(default=100)] = 100,
    start: Annotated[Optional[int], Field(description="""Start datetime, can be epoch or relative time like -1d, -1w; -1d if not specified""")] | None = None,
    end: Annotated[Optional[int], Field(description="""End datetime, can be epoch or relative time like -1d, -2h; now if not specified""")] | None = None,
    duration: Annotated[str, Field(description="""Duration like 7d, 2w""",default="1d")] = "1d",
) -> dict:
    """Search Switch / Gateway Ports"""

    response = mistapi.api.v1.orgs.stats.searchOrgSwOrGwPorts(
            apisession,
            org_id=str(org_id),
            full_duplex=full_duplex,
            mac=mac,
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
            stp_state=stp_state.value,
            stp_role=stp_role.value,
            auth_state=auth_state.value,
            limit=limit,
            start=start,
            end=end,
            duration=duration,
    )
    
    
    ctx = get_context()
    
    if response.status_code != 200:
        error = {
            "status_code": response.status_code,
            "message": ""
        }
        if response.data:
            await ctx.error(f"Got HTTP{response.status_code} with details {response.data}")
            error["message"] =json.dumps(response.data)
        elif response.status_code == 400:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] =json.dumps("Bad Request. The API endpoint exists but its syntax/payload is incorrect, detail may be given")
        elif response.status_code == 401:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] =json.dumps("Unauthorized")
        elif response.status_code == 403:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] =json.dumps("Unauthorized")
        elif response.status_code == 401:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] =json.dumps("Permission Denied")
        elif response.status_code == 404:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] =json.dumps("Not found. The API endpoint doesn’t exist or resource doesn’t exist")
        elif response.status_code == 429:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] =json.dumps("Too Many Request. The API Token used for the request reached the 5000 API Calls per hour threshold")
        raise ToolError(error)
            
    return response.data
