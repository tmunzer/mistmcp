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
from typing import Annotated, Optional, List
from uuid import UUID
from enum import Enum


mcp = mcp_instance.get()


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
    enabled=False,
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
        Optional[str], Field(description="""Partial / full hostname""")
    ],
    type: Optional[Type],
    model: Annotated[Optional[str], Field(description="""Device model""")],
    mac: Annotated[Optional[str], Field(description="""Device MAC""")],
    ext_ip: Annotated[Optional[str], Field(description="""Device external ip""")],
    version: Annotated[Optional[str], Field(description="""Version""")],
    power_constrained: Annotated[
        Optional[bool], Field(description="""power_constrained""")
    ],
    ip: Optional[str],
    mxtunnel_status: Annotated[
        Optional[Mxtunnel_status],
        Field(description="""For APs only, MxTunnel status, up / down."""),
    ],
    mxedge_id: Annotated[
        Optional[UUID],
        Field(
            description="""For APs only, Mist Edge id, if AP is connecting to a Mist Edge"""
        ),
    ],
    mxedge_ids: Annotated[
        Optional[List[str]],
        Field(
            description="""For APs only, list of Mist Edge id, if AP is connecting to a Mist Edge"""
        ),
    ],
    last_hostname: Annotated[
        Optional[str],
        Field(description="""For Switches and Gateways only, last hostname"""),
    ],
    last_config_status: Annotated[
        Optional[str],
        Field(
            description="""For Switches and Gateways only, last configuration status of the switch/gateway"""
        ),
    ],
    radius_stats: Annotated[
        Optional[str],
        Field(
            description="""For Switches and Gateways only, Key-value pairs where the key is the RADIUS server address and the value contains authentication statistics:   *  <server_address> (string): IP address of the RADIUS server as the key   * `auth_accepts` (long): Number of accepted authentication requests   * `auth_rejects` (long): Number of rejected authentication requests   * `auth_timeouts` (long): Number of authentication timeouts   * `auth_server_status` (string): Status of the server. Possible values: `up`, `down`, `unreachable`"""
        ),
    ],
    cpu: Annotated[
        Optional[str],
        Field(description="""For Switches and Gateways only, max cpu usage"""),
    ],
    node0_mac: Annotated[
        Optional[str], Field(description="""For Gateways only, node0 MAC Address""")
    ],
    clustered: Annotated[Optional[bool], Field(description="""For Gateways only""")],
    t128agent_version: Annotated[
        Optional[str],
        Field(description="""For Gateways (SSR) only, version of 128T agent"""),
    ],
    node1_mac: Annotated[
        Optional[str], Field(description="""For Gateways only, node1 MAC Address""")
    ],
    node: Annotated[
        Optional[Node],
        Field(description="""For Gateways only. enum: `node0`, `node1`"""),
    ],
    evpntopo_id: Annotated[
        Optional[str], Field(description="""For Switches only, EVPN topology id""")
    ],
    lldp_system_name: Annotated[
        Optional[str], Field(description="""For APs only, LLDP system name""")
    ],
    lldp_system_desc: Annotated[
        Optional[str], Field(description="""For APs only, LLDP system description""")
    ],
    lldp_port_id: Annotated[
        Optional[str], Field(description="""For APs only, LLDP port id""")
    ],
    lldp_mgmt_addr: Annotated[
        Optional[str], Field(description="""For APs only, LLDP management ip address""")
    ],
    band_24_channel: Annotated[
        Optional[int], Field(description="""Channel of band_24""")
    ],
    band_5_channel: Annotated[
        Optional[int], Field(description="""Channel of band_5""")
    ],
    band_6_channel: Annotated[
        Optional[int], Field(description="""Channel of band_6""")
    ],
    band_24_bandwidth: Annotated[
        Optional[int], Field(description="""Bandwidth of band_24""")
    ],
    band_5_bandwidth: Annotated[
        Optional[int], Field(description="""Bandwidth of band_5""")
    ],
    band_6_bandwidth: Annotated[
        Optional[int], Field(description="""Bandwidth of band_6""")
    ],
    eth0_port_speed: Annotated[
        Optional[int], Field(description="""Port speed of eth0""")
    ],
    stats: Annotated[
        Optional[bool], Field(description="""Whether to return device stats""")
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
    sort: Annotated[Optional[Sort], Field(description="""Sort options""")],
    desc_sort: Annotated[
        Optional[Desc_sort], Field(description="""Sort options in reverse order""")
    ],
    search_after: Annotated[
        Optional[str],
        Field(
            description="""Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed."""
        ),
    ],
) -> dict | list:
    """Search Device"""

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
