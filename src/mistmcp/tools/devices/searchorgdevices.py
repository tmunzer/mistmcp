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


class Mxtunnel_status(Enum):
    DOWN = "down"
    UP = "up"
    NONE = None


class Type(Enum):
    AP = "ap"
    GATEWAY = "gateway"
    SWITCH = "switch"


@mcp.tool(
    enabled=False,
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
        Optional[int], Field(description="""If `type`==`ap`, Bandwidth of band_24""")
    ] = None,
    band_24_channel: Annotated[
        Optional[int], Field(description="""If `type`==`ap`, Channel of band_24""")
    ] = None,
    band_24_power: Annotated[
        Optional[int], Field(description="""If `type`==`ap`, Power of band_24""")
    ] = None,
    band_5_bandwidth: Annotated[
        Optional[int], Field(description="""If `type`==`ap`, Bandwidth of band_5""")
    ] = None,
    band_5_channel: Annotated[
        Optional[int], Field(description="""If `type`==`ap`, Channel of band_5""")
    ] = None,
    band_5_power: Annotated[
        Optional[int], Field(description="""If `type`==`ap`, Power of band_5""")
    ] = None,
    band_6_bandwidth: Annotated[
        Optional[int], Field(description="""If `type`==`ap`, Bandwidth of band_6""")
    ] = None,
    band_6_channel: Annotated[
        Optional[int], Field(description="""If `type`==`ap`, Channel of band_6""")
    ] = None,
    band_6_power: Annotated[
        Optional[int], Field(description="""If `type`==`ap`, Power of band_6""")
    ] = None,
    cpu: Annotated[
        Optional[str],
        Field(
            description="""If `type`==`switch` or `type`==`gateway`, max cpu usage"""
        ),
    ] = None,
    clustered: Annotated[
        Optional[str], Field(description="""If `type`==`gateway`, true / false""")
    ] = None,
    eth0_port_speed: Annotated[
        Optional[int], Field(description="""If `type`==`ap`, Port speed of eth0""")
    ] = None,
    evpntopo_id: Annotated[
        Optional[str], Field(description="""If `type`==`switch`, EVPN topology id""")
    ] = None,
    ext_ip: Annotated[
        Optional[str], Field(description="""External IP Address""")
    ] = None,
    hostname: Annotated[
        Optional[str], Field(description="""Partial / full hostname""")
    ] = None,
    ip_address: Optional[str] = None,
    last_config_status: Annotated[
        Optional[str],
        Field(
            description="""If `type`==`switch` or `type`==`gateway`, last configuration status"""
        ),
    ] = None,
    last_hostname: Annotated[
        Optional[str],
        Field(
            description="""If `type`==`switch` or `type`==`gateway`, last hostname"""
        ),
    ] = None,
    lldp_mgmt_addr: Annotated[
        Optional[str],
        Field(description="""If `type`==`ap`, LLDP management ip address"""),
    ] = None,
    lldp_port_id: Annotated[
        Optional[str], Field(description="""If `type`==`ap`, LLDP port id""")
    ] = None,
    lldp_power_allocated: Annotated[
        Optional[int], Field(description="""If `type`==`ap`, LLDP Allocated Power""")
    ] = None,
    lldp_power_draw: Annotated[
        Optional[int], Field(description="""If `type`==`ap`, LLDP Negotiated Power""")
    ] = None,
    lldp_system_desc: Annotated[
        Optional[str], Field(description="""If `type`==`ap`, LLDP system description""")
    ] = None,
    lldp_system_name: Annotated[
        Optional[str], Field(description="""If `type`==`ap`, LLDP system name""")
    ] = None,
    mac: Annotated[Optional[str], Field(description="""Device mac""")] = None,
    model: Annotated[Optional[str], Field(description="""Device model""")] = None,
    mxedge_id: Annotated[
        Optional[str],
        Field(
            description="""If `type`==`ap`, Mist Edge id, if AP is connecting to a Mist Edge"""
        ),
    ] = None,
    mxedge_ids: Annotated[
        Optional[str],
        Field(
            description="""If `type`==`ap`, Comma separated list of Mist Edge ids, if AP is connecting to a Mist Edge"""
        ),
    ] = None,
    mxtunnel_status: Annotated[
        Mxtunnel_status,
        Field(description="""If `type`==`ap`, MxTunnel status, up / down"""),
    ] = Mxtunnel_status.NONE,
    node: Annotated[
        Optional[str], Field(description="""If `type`==`gateway`, `node0` / `node1`""")
    ] = None,
    node0_mac: Annotated[
        Optional[str], Field(description="""If `type`==`gateway`, mac for node0""")
    ] = None,
    node1_mac: Annotated[
        Optional[str], Field(description="""If `type`==`gateway`, mac for node1""")
    ] = None,
    power_constrained: Annotated[
        Optional[bool], Field(description="""If `type`==`ap`, Power_constrained""")
    ] = None,
    site_id: Annotated[Optional[str], Field(description="""Site id""")] = None,
    t128agent_version: Annotated[
        Optional[str],
        Field(description="""If `type`==`gateway`,version of 128T agent"""),
    ] = None,
    version: Annotated[Optional[str], Field(description="""Version""")] = None,
    type: Annotated[
        Type, Field(description="""Type of device. enum: `ap`, `gateway`, `switch`""")
    ] = Type.AP,
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
    """Search Org Devices"""

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

    response = mistapi.api.v1.orgs.devices.searchOrgDevices(
        apisession,
        org_id=str(org_id),
        band_24_bandwidth=band_24_bandwidth,
        band_24_channel=band_24_channel,
        band_24_power=band_24_power,
        band_5_bandwidth=band_5_bandwidth,
        band_5_channel=band_5_channel,
        band_5_power=band_5_power,
        band_6_bandwidth=band_6_bandwidth,
        band_6_channel=band_6_channel,
        band_6_power=band_6_power,
        cpu=cpu,
        clustered=clustered,
        eth0_port_speed=eth0_port_speed,
        evpntopo_id=evpntopo_id,
        ext_ip=ext_ip,
        hostname=hostname,
        ip_address=ip_address,
        last_config_status=last_config_status,
        last_hostname=last_hostname,
        lldp_mgmt_addr=lldp_mgmt_addr,
        lldp_port_id=lldp_port_id,
        lldp_power_allocated=lldp_power_allocated,
        lldp_power_draw=lldp_power_draw,
        lldp_system_desc=lldp_system_desc,
        lldp_system_name=lldp_system_name,
        mac=mac,
        model=model,
        mxedge_id=mxedge_id,
        mxedge_ids=mxedge_ids,
        mxtunnel_status=mxtunnel_status.value,
        node=node,
        node0_mac=node0_mac,
        node1_mac=node1_mac,
        power_constrained=power_constrained,
        site_id=site_id,
        t128agent_version=t128agent_version,
        version=version,
        type=type.value,
        limit=limit,
        start=start,
        end=end,
        duration=duration,
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
                "Not found. The API endpoint doesn’t exist or resource doesn’t exist"
            )
        elif response.status_code == 429:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps(
                "Too Many Request. The API Token used for the request reached the 5000 API Calls per hour threshold"
            )
        raise ToolError(api_error)

    return response.data
