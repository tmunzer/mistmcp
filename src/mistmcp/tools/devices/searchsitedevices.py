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
from typing import Annotated, Optional, List
from uuid import UUID
from enum import Enum


mcp = get_mcp()

if not mcp:
    raise RuntimeError(
        "MCP instance not found. Make sure to initialize the MCP server before defining tools."
    )


class Type(Enum):
    AP = "ap"
    GATEWAY = "gateway"
    SWITCH = "switch"


class Mxtunnel_status(Enum):
    DOWN = "down"
    UP = "up"
    NONE = None


class Node(Enum):
    NODE0 = "node0"
    NODE1 = "node1"
    NONE = None


class Sort(Enum):
    MAC = "mac"
    MODEL = "model"
    SKU = "sku"
    TIMESTAMP = "timestamp"


class Desc_sort(Enum):
    MAC = "mac"
    MODEL = "model"
    SKU = "sku"
    TIMESTAMP = "timestamp"
    NONE = None


@mcp.tool(
    enabled=True,
    name="searchSiteDevices",
    description="""Search Device""",
    tags={"devices"},
    annotations={
        "title": "searchSiteDevices",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchSiteDevices(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    hostname: Annotated[
        Optional[str | None], Field(description="""Partial / full hostname""")
    ] = None,
    type: Optional[Type | None] = Type.AP,
    model: Annotated[
        Optional[str | None], Field(description="""Device model""")
    ] = None,
    mac: Annotated[Optional[str | None], Field(description="""Device MAC""")] = None,
    ext_ip: Annotated[
        Optional[str | None], Field(description="""Device external ip""")
    ] = None,
    version: Annotated[Optional[str | None], Field(description="""Version""")] = None,
    power_constrained: Annotated[
        Optional[bool | None], Field(description="""power_constrained""")
    ] = None,
    ip: Optional[str | None] = None,
    mxtunnel_status: Annotated[
        Optional[Mxtunnel_status | None],
        Field(description="""For APs only, MxTunnel status, up / down."""),
    ] = Mxtunnel_status.NONE,
    mxedge_id: Annotated[
        Optional[UUID | None],
        Field(
            description="""For APs only, Mist Edge id, if AP is connecting to a Mist Edge"""
        ),
    ] = None,
    mxedge_ids: Annotated[
        Optional[List[str] | None],
        Field(
            description="""For APs only, list of Mist Edge id, if AP is connecting to a Mist Edge"""
        ),
    ] = None,
    last_hostname: Annotated[
        Optional[str | None],
        Field(description="""For Switches and Gateways only, last hostname"""),
    ] = None,
    last_config_status: Annotated[
        Optional[str | None],
        Field(
            description="""For Switches and Gateways only, last configuration status of the switch/gateway"""
        ),
    ] = None,
    radius_stats: Annotated[
        Optional[str | None],
        Field(
            description="""For Switches and Gateways only, Key-value pairs where the key is the RADIUS server address and the value contains authentication statistics:   *  <server_address> (string): IP address of the RADIUS server as the key   * `auth_accepts` (long): Number of accepted authentication requests   * `auth_rejects` (long): Number of rejected authentication requests   * `auth_timeouts` (long): Number of authentication timeouts   * `auth_server_status` (string): Status of the server. Possible values: `up`, `down`, `unreachable`"""
        ),
    ] = None,
    cpu: Annotated[
        Optional[str | None],
        Field(description="""For Switches and Gateways only, max cpu usage"""),
    ] = None,
    node0_mac: Annotated[
        Optional[str | None],
        Field(description="""For Gateways only, node0 MAC Address"""),
    ] = None,
    clustered: Annotated[
        Optional[bool | None], Field(description="""For Gateways only""")
    ] = None,
    t128agent_version: Annotated[
        Optional[str | None],
        Field(description="""For Gateways (SSR) only, version of 128T agent"""),
    ] = None,
    node1_mac: Annotated[
        Optional[str | None],
        Field(description="""For Gateways only, node1 MAC Address"""),
    ] = None,
    node: Annotated[
        Optional[Node | None],
        Field(description="""For Gateways only. enum: `node0`, `node1`"""),
    ] = Node.NONE,
    evpntopo_id: Annotated[
        Optional[str | None],
        Field(description="""For Switches only, EVPN topology id"""),
    ] = None,
    lldp_system_name: Annotated[
        Optional[str | None], Field(description="""For APs only, LLDP system name""")
    ] = None,
    lldp_system_desc: Annotated[
        Optional[str | None],
        Field(description="""For APs only, LLDP system description"""),
    ] = None,
    lldp_port_id: Annotated[
        Optional[str | None], Field(description="""For APs only, LLDP port id""")
    ] = None,
    lldp_mgmt_addr: Annotated[
        Optional[str | None],
        Field(description="""For APs only, LLDP management ip address"""),
    ] = None,
    band_24_channel: Annotated[
        Optional[int | None], Field(description="""Channel of band_24""")
    ] = None,
    band_5_channel: Annotated[
        Optional[int | None], Field(description="""Channel of band_5""")
    ] = None,
    band_6_channel: Annotated[
        Optional[int | None], Field(description="""Channel of band_6""")
    ] = None,
    band_24_bandwidth: Annotated[
        Optional[int | None], Field(description="""Bandwidth of band_24""")
    ] = None,
    band_5_bandwidth: Annotated[
        Optional[int | None], Field(description="""Bandwidth of band_5""")
    ] = None,
    band_6_bandwidth: Annotated[
        Optional[int | None], Field(description="""Bandwidth of band_6""")
    ] = None,
    eth0_port_speed: Annotated[
        Optional[int | None], Field(description="""Port speed of eth0""")
    ] = None,
    stats: Annotated[
        Optional[bool | None], Field(description="""Whether to return device stats""")
    ] = None,
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
        Optional[Sort | None], Field(description="""Sort options""")
    ] = Sort.TIMESTAMP,
    desc_sort: Annotated[
        Optional[Desc_sort | None],
        Field(description="""Sort options in reverse order"""),
    ] = Desc_sort.NONE,
    search_after: Annotated[
        Optional[str | None],
        Field(
            description="""Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed."""
        ),
    ] = None,
) -> dict | list | str:
    """Search Device"""

    apisession, _, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.sites.devices.searchSiteDevices(
        apisession,
        site_id=str(site_id),
        hostname=hostname if hostname else None,
        type=type.value if type else Type.AP.value,
        model=model if model else None,
        mac=mac if mac else None,
        ext_ip=ext_ip if ext_ip else None,
        version=version if version else None,
        power_constrained=power_constrained if power_constrained else None,
        ip=ip if ip else None,
        mxtunnel_status=mxtunnel_status.value if mxtunnel_status else None,
        mxedge_id=str(mxedge_id) if mxedge_id else None,
        mxedge_ids=mxedge_ids if mxedge_ids else None,
        last_hostname=last_hostname if last_hostname else None,
        last_config_status=last_config_status if last_config_status else None,
        radius_stats=radius_stats if radius_stats else None,
        cpu=cpu if cpu else None,
        node0_mac=node0_mac if node0_mac else None,
        clustered=clustered if clustered else None,
        t128agent_version=t128agent_version if t128agent_version else None,
        node1_mac=node1_mac if node1_mac else None,
        node=node.value if node else None,
        evpntopo_id=evpntopo_id if evpntopo_id else None,
        lldp_system_name=lldp_system_name if lldp_system_name else None,
        lldp_system_desc=lldp_system_desc if lldp_system_desc else None,
        lldp_port_id=lldp_port_id if lldp_port_id else None,
        lldp_mgmt_addr=lldp_mgmt_addr if lldp_mgmt_addr else None,
        band_24_channel=band_24_channel if band_24_channel else None,
        band_5_channel=band_5_channel if band_5_channel else None,
        band_6_channel=band_6_channel if band_6_channel else None,
        band_24_bandwidth=band_24_bandwidth if band_24_bandwidth else None,
        band_5_bandwidth=band_5_bandwidth if band_5_bandwidth else None,
        band_6_bandwidth=band_6_bandwidth if band_6_bandwidth else None,
        eth0_port_speed=eth0_port_speed if eth0_port_speed else None,
        stats=stats if stats else None,
        limit=limit if limit else None,
        start=start if start else None,
        end=end if end else None,
        duration=duration if duration else None,
        sort=sort.value if sort else Sort.TIMESTAMP.value,
        desc_sort=desc_sort.value if desc_sort else None,
        search_after=search_after if search_after else None,
    )
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
