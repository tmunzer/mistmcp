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
from mistmcp.server import mcp

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


class Mxtunnel_status(Enum):
    DOWN = "down"
    UP = "up"
    NONE = None


class Type(Enum):
    AP = "ap"
    GATEWAY = "gateway"
    SWITCH = "switch"


@mcp.tool(
    name="searchOrgDevices",
    description="""Search Org Devices""",
    tags={"devices"},
    annotations={
        "title": "searchOrgDevices",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchOrgDevices(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    band_24_bandwidth: Annotated[
        Optional[int | None],
        Field(description="""If `type`==`ap`, Bandwidth of band_24"""),
    ] = None,
    band_24_channel: Annotated[
        Optional[int | None],
        Field(description="""If `type`==`ap`, Channel of band_24"""),
    ] = None,
    band_24_power: Annotated[
        Optional[int | None], Field(description="""If `type`==`ap`, Power of band_24""")
    ] = None,
    band_5_bandwidth: Annotated[
        Optional[int | None],
        Field(description="""If `type`==`ap`, Bandwidth of band_5"""),
    ] = None,
    band_5_channel: Annotated[
        Optional[int | None],
        Field(description="""If `type`==`ap`, Channel of band_5"""),
    ] = None,
    band_5_power: Annotated[
        Optional[int | None], Field(description="""If `type`==`ap`, Power of band_5""")
    ] = None,
    band_6_bandwidth: Annotated[
        Optional[int | None],
        Field(description="""If `type`==`ap`, Bandwidth of band_6"""),
    ] = None,
    band_6_channel: Annotated[
        Optional[int | None],
        Field(description="""If `type`==`ap`, Channel of band_6"""),
    ] = None,
    band_6_power: Annotated[
        Optional[int | None], Field(description="""If `type`==`ap`, Power of band_6""")
    ] = None,
    cpu: Annotated[
        Optional[str | None],
        Field(
            description="""If `type`==`switch` or `type`==`gateway`, max cpu usage"""
        ),
    ] = None,
    clustered: Annotated[
        Optional[str | None],
        Field(description="""If `type`==`gateway`, true / false"""),
    ] = None,
    eth0_port_speed: Annotated[
        Optional[int | None],
        Field(description="""If `type`==`ap`, Port speed of eth0"""),
    ] = None,
    evpntopo_id: Annotated[
        Optional[str | None],
        Field(description="""If `type`==`switch`, EVPN topology id"""),
    ] = None,
    ext_ip: Annotated[
        Optional[str | None], Field(description="""External IP Address""")
    ] = None,
    hostname: Annotated[
        Optional[str | None], Field(description="""Partial / full hostname""")
    ] = None,
    ip: Optional[str | None] = None,
    last_config_status: Annotated[
        Optional[str | None],
        Field(
            description="""If `type`==`switch` or `type`==`gateway`, last configuration status"""
        ),
    ] = None,
    last_hostname: Annotated[
        Optional[str | None],
        Field(
            description="""If `type`==`switch` or `type`==`gateway`, last hostname"""
        ),
    ] = None,
    lldp_mgmt_addr: Annotated[
        Optional[str | None],
        Field(description="""If `type`==`ap`, LLDP management ip address"""),
    ] = None,
    lldp_port_id: Annotated[
        Optional[str | None], Field(description="""If `type`==`ap`, LLDP port id""")
    ] = None,
    lldp_power_allocated: Annotated[
        Optional[int | None],
        Field(description="""If `type`==`ap`, LLDP Allocated Power"""),
    ] = None,
    lldp_power_draw: Annotated[
        Optional[int | None],
        Field(description="""If `type`==`ap`, LLDP Negotiated Power"""),
    ] = None,
    lldp_system_desc: Annotated[
        Optional[str | None],
        Field(description="""If `type`==`ap`, LLDP system description"""),
    ] = None,
    lldp_system_name: Annotated[
        Optional[str | None], Field(description="""If `type`==`ap`, LLDP system name""")
    ] = None,
    mac: Annotated[Optional[str | None], Field(description="""Device mac""")] = None,
    model: Annotated[
        Optional[str | None], Field(description="""Device model""")
    ] = None,
    mxedge_id: Annotated[
        Optional[str | None],
        Field(
            description="""If `type`==`ap`, Mist Edge id, if AP is connecting to a Mist Edge"""
        ),
    ] = None,
    mxedge_ids: Annotated[
        Optional[str | None],
        Field(
            description="""If `type`==`ap`, Comma separated list of Mist Edge ids, if AP is connecting to a Mist Edge"""
        ),
    ] = None,
    mxtunnel_status: Annotated[
        Optional[Mxtunnel_status | None],
        Field(description="""If `type`==`ap`, MxTunnel status, up / down"""),
    ] = Mxtunnel_status.NONE,
    node: Annotated[
        Optional[str | None],
        Field(description="""If `type`==`gateway`, `node0` / `node1`"""),
    ] = None,
    node0_mac: Annotated[
        Optional[str | None],
        Field(description="""If `type`==`gateway`, mac for node0"""),
    ] = None,
    node1_mac: Annotated[
        Optional[str | None],
        Field(description="""If `type`==`gateway`, mac for node1"""),
    ] = None,
    power_constrained: Annotated[
        Optional[bool | None],
        Field(description="""If `type`==`ap`, Power_constrained"""),
    ] = None,
    site_id: Annotated[Optional[str | None], Field(description="""Site id""")] = None,
    t128agent_version: Annotated[
        Optional[str | None],
        Field(description="""If `type`==`gateway`,version of 128T agent"""),
    ] = None,
    version: Annotated[Optional[str | None], Field(description="""Version""")] = None,
    type: Annotated[
        Optional[Type | None],
        Field(description="""Type of device. enum: `ap`, `gateway`, `switch`"""),
    ] = Type.AP,
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
    ctx: Context | None = None,
) -> dict | list | str:
    """Search Org Devices"""

    apisession, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.orgs.devices.searchOrgDevices(
        apisession,
        org_id=str(org_id),
        band_24_bandwidth=band_24_bandwidth if band_24_bandwidth else None,
        band_24_channel=band_24_channel if band_24_channel else None,
        band_24_power=band_24_power if band_24_power else None,
        band_5_bandwidth=band_5_bandwidth if band_5_bandwidth else None,
        band_5_channel=band_5_channel if band_5_channel else None,
        band_5_power=band_5_power if band_5_power else None,
        band_6_bandwidth=band_6_bandwidth if band_6_bandwidth else None,
        band_6_channel=band_6_channel if band_6_channel else None,
        band_6_power=band_6_power if band_6_power else None,
        cpu=cpu if cpu else None,
        clustered=clustered if clustered else None,
        eth0_port_speed=eth0_port_speed if eth0_port_speed else None,
        evpntopo_id=evpntopo_id if evpntopo_id else None,
        ext_ip=ext_ip if ext_ip else None,
        hostname=hostname if hostname else None,
        ip=ip if ip else None,
        last_config_status=last_config_status if last_config_status else None,
        last_hostname=last_hostname if last_hostname else None,
        lldp_mgmt_addr=lldp_mgmt_addr if lldp_mgmt_addr else None,
        lldp_port_id=lldp_port_id if lldp_port_id else None,
        lldp_power_allocated=lldp_power_allocated if lldp_power_allocated else None,
        lldp_power_draw=lldp_power_draw if lldp_power_draw else None,
        lldp_system_desc=lldp_system_desc if lldp_system_desc else None,
        lldp_system_name=lldp_system_name if lldp_system_name else None,
        mac=mac if mac else None,
        model=model if model else None,
        mxedge_id=mxedge_id if mxedge_id else None,
        mxedge_ids=mxedge_ids if mxedge_ids else None,
        mxtunnel_status=mxtunnel_status.value if mxtunnel_status else None,
        node=node if node else None,
        node0_mac=node0_mac if node0_mac else None,
        node1_mac=node1_mac if node1_mac else None,
        power_constrained=power_constrained if power_constrained else None,
        site_id=site_id if site_id else None,
        t128agent_version=t128agent_version if t128agent_version else None,
        version=version if version else None,
        type=type.value if type else Type.AP.value,
        limit=limit if limit else None,
        start=start if start else None,
        end=end if end else None,
        duration=duration if duration else None,
        sort=sort if sort else None,
        search_after=search_after if search_after else None,
    )
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
