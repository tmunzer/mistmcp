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
    ],
    band_24_channel: Annotated[
        Optional[int], Field(description="""If `type`==`ap`, Channel of band_24""")
    ],
    band_24_power: Annotated[
        Optional[int], Field(description="""If `type`==`ap`, Power of band_24""")
    ],
    band_5_bandwidth: Annotated[
        Optional[int], Field(description="""If `type`==`ap`, Bandwidth of band_5""")
    ],
    band_5_channel: Annotated[
        Optional[int], Field(description="""If `type`==`ap`, Channel of band_5""")
    ],
    band_5_power: Annotated[
        Optional[int], Field(description="""If `type`==`ap`, Power of band_5""")
    ],
    band_6_bandwidth: Annotated[
        Optional[int], Field(description="""If `type`==`ap`, Bandwidth of band_6""")
    ],
    band_6_channel: Annotated[
        Optional[int], Field(description="""If `type`==`ap`, Channel of band_6""")
    ],
    band_6_power: Annotated[
        Optional[int], Field(description="""If `type`==`ap`, Power of band_6""")
    ],
    cpu: Annotated[
        Optional[str],
        Field(
            description="""If `type`==`switch` or `type`==`gateway`, max cpu usage"""
        ),
    ],
    clustered: Annotated[
        Optional[str], Field(description="""If `type`==`gateway`, true / false""")
    ],
    eth0_port_speed: Annotated[
        Optional[int], Field(description="""If `type`==`ap`, Port speed of eth0""")
    ],
    evpntopo_id: Annotated[
        Optional[str], Field(description="""If `type`==`switch`, EVPN topology id""")
    ],
    ext_ip: Annotated[Optional[str], Field(description="""External IP Address""")],
    hostname: Annotated[
        Optional[str], Field(description="""Partial / full hostname""")
    ],
    ip: Optional[str],
    last_config_status: Annotated[
        Optional[str],
        Field(
            description="""If `type`==`switch` or `type`==`gateway`, last configuration status"""
        ),
    ],
    last_hostname: Annotated[
        Optional[str],
        Field(
            description="""If `type`==`switch` or `type`==`gateway`, last hostname"""
        ),
    ],
    lldp_mgmt_addr: Annotated[
        Optional[str],
        Field(description="""If `type`==`ap`, LLDP management ip address"""),
    ],
    lldp_port_id: Annotated[
        Optional[str], Field(description="""If `type`==`ap`, LLDP port id""")
    ],
    lldp_power_allocated: Annotated[
        Optional[int], Field(description="""If `type`==`ap`, LLDP Allocated Power""")
    ],
    lldp_power_draw: Annotated[
        Optional[int], Field(description="""If `type`==`ap`, LLDP Negotiated Power""")
    ],
    lldp_system_desc: Annotated[
        Optional[str], Field(description="""If `type`==`ap`, LLDP system description""")
    ],
    lldp_system_name: Annotated[
        Optional[str], Field(description="""If `type`==`ap`, LLDP system name""")
    ],
    mac: Annotated[Optional[str], Field(description="""Device mac""")],
    model: Annotated[Optional[str], Field(description="""Device model""")],
    mxedge_id: Annotated[
        Optional[str],
        Field(
            description="""If `type`==`ap`, Mist Edge id, if AP is connecting to a Mist Edge"""
        ),
    ],
    mxedge_ids: Annotated[
        Optional[str],
        Field(
            description="""If `type`==`ap`, Comma separated list of Mist Edge ids, if AP is connecting to a Mist Edge"""
        ),
    ],
    mxtunnel_status: Annotated[
        Optional[Mxtunnel_status],
        Field(description="""If `type`==`ap`, MxTunnel status, up / down"""),
    ],
    node: Annotated[
        Optional[str], Field(description="""If `type`==`gateway`, `node0` / `node1`""")
    ],
    node0_mac: Annotated[
        Optional[str], Field(description="""If `type`==`gateway`, mac for node0""")
    ],
    node1_mac: Annotated[
        Optional[str], Field(description="""If `type`==`gateway`, mac for node1""")
    ],
    power_constrained: Annotated[
        Optional[bool], Field(description="""If `type`==`ap`, Power_constrained""")
    ],
    site_id: Annotated[Optional[str], Field(description="""Site id""")],
    t128agent_version: Annotated[
        Optional[str],
        Field(description="""If `type`==`gateway`,version of 128T agent"""),
    ],
    version: Annotated[Optional[str], Field(description="""Version""")],
    type: Annotated[
        Optional[Type],
        Field(description="""Type of device. enum: `ap`, `gateway`, `switch`"""),
    ],
    limit: Optional[int],
    start: Annotated[
        Optional[str],
        Field(
            description="""Start time (epoch timestamp in seconds, or relative string like '-1d', '-1w')"""
        ),
    ],
    end: Annotated[
        Optional[str],
        Field(
            description="""End time (epoch timestamp in seconds, or relative string like '-1d', '-2h', 'now')"""
        ),
    ],
    duration: Annotated[Optional[str], Field(description="""Duration like 7d, 2w""")],
    sort: Annotated[
        Optional[str],
        Field(
            description="""On which field the list should be sorted, -prefix represents DESC order"""
        ),
    ],
    search_after: Annotated[
        Optional[str],
        Field(
            description="""Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed."""
        ),
    ],
) -> dict | list:
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
