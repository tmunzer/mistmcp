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


class Type(Enum):
    AP = "ap"
    GATEWAY = "gateway"
    SWITCH = "switch"


class Mxtunnel_status(Enum):
    DOWN = "down"
    UP = "up"
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
    tags={"Sites Devices"},
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
        Optional[str], Field(description="""Partial / full hostname""")
    ] = None,
    type: Type = Type.AP,
    model: Annotated[Optional[str], Field(description="""Device model""")] = None,
    mac: Annotated[Optional[str], Field(description="""Device MAC""")] = None,
    version: Annotated[Optional[str], Field(description="""Version""")] = None,
    power_constrained: Annotated[
        Optional[bool], Field(description="""power_constrained""")
    ] = None,
    ip_address: Optional[str] = None,
    mxtunnel_status: Annotated[
        Mxtunnel_status, Field(description="""MxTunnel status, up / down""")
    ] = Mxtunnel_status.NONE,
    mxedge_id: Annotated[
        Optional[UUID],
        Field(description="""Mist Edge id, if AP is connecting to a Mist Edge"""),
    ] = None,
    lldp_system_name: Annotated[
        Optional[str], Field(description="""LLDP system name""")
    ] = None,
    lldp_system_desc: Annotated[
        Optional[str], Field(description="""LLDP system description""")
    ] = None,
    lldp_port_id: Annotated[
        Optional[str], Field(description="""LLDP port id""")
    ] = None,
    lldp_mgmt_addr: Annotated[
        Optional[str], Field(description="""LLDP management ip address""")
    ] = None,
    band_24_channel: Annotated[
        Optional[int], Field(description="""Channel of band_24""")
    ] = None,
    band_5_channel: Annotated[
        Optional[int], Field(description="""Channel of band_5""")
    ] = None,
    band_6_channel: Annotated[
        Optional[int], Field(description="""Channel of band_6""")
    ] = None,
    band_24_bandwidth: Annotated[
        Optional[int], Field(description="""Bandwidth of band_24""")
    ] = None,
    band_5_bandwidth: Annotated[
        Optional[int], Field(description="""Bandwidth of band_5""")
    ] = None,
    band_6_bandwidth: Annotated[
        Optional[int], Field(description="""Bandwidth of band_6""")
    ] = None,
    eth0_port_speed: Annotated[
        Optional[int], Field(description="""Port speed of eth0""")
    ] = None,
    sort: Annotated[Sort, Field(description="""Sort options""")] = Sort.TIMESTAMP,
    desc_sort: Annotated[
        Desc_sort, Field(description="""Sort options in reverse order""")
    ] = Desc_sort.NONE,
    stats: Annotated[
        Optional[bool], Field(description="""Whether to return device stats""")
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
    """Search Device"""

    ctx = get_context()
    request: Request = get_http_request()
    cloud = request.query_params.get("cloud", None)
    apitoken = request.headers.get("X-Authorization", None)
    apisession = mistapi.APISession(
        host=cloud,
        apitoken=apitoken,
    )

    response = mistapi.api.v1.sites.devices.searchSiteDevices(
        apisession,
        site_id=str(site_id),
        hostname=hostname,
        type=type.value,
        model=model,
        mac=mac,
        version=version,
        power_constrained=power_constrained,
        ip_address=ip_address,
        mxtunnel_status=mxtunnel_status.value,
        mxedge_id=str(mxedge_id),
        lldp_system_name=lldp_system_name,
        lldp_system_desc=lldp_system_desc,
        lldp_port_id=lldp_port_id,
        lldp_mgmt_addr=lldp_mgmt_addr,
        band_24_channel=band_24_channel,
        band_5_channel=band_5_channel,
        band_6_channel=band_6_channel,
        band_24_bandwidth=band_24_bandwidth,
        band_5_bandwidth=band_5_bandwidth,
        band_6_bandwidth=band_6_bandwidth,
        eth0_port_speed=eth0_port_speed,
        sort=sort.value,
        desc_sort=desc_sort.value,
        stats=stats,
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
