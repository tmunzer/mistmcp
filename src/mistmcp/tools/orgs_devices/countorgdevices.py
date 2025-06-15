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


class Distinct(Enum):
    HOSTNAME = "hostname"
    IP = "ip"
    LLDP_MGMT_ADDR = "lldp_mgmt_addr"
    LLDP_PORT_ID = "lldp_port_id"
    LLDP_SYSTEM_DESC = "lldp_system_desc"
    LLDP_SYSTEM_NAME = "lldp_system_name"
    MAC = "mac"
    MODEL = "model"
    MXEDGE_ID = "mxedge_id"
    MXTUNNEL_STATUS = "mxtunnel_status"
    SITE_ID = "site_id"
    VERSION = "version"


class Mxtunnel_status(Enum):
    DOWN = "down"
    UP = "up"
    NONE = None


class Type(Enum):
    AP = "ap"
    GATEWAY = "gateway"
    SWITCH = "switch"


@mcp.tool(
    enabled=True,
    name="countOrgDevices",
    description="""Count by Distinct Attributes of Org Devices""",
    tags={"Orgs Devices"},
    annotations={
        "title": "countOrgDevices",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def countOrgDevices(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    distinct: Distinct = Distinct.MODEL,
    hostname: Annotated[
        Optional[str], Field(description="""Partial / full hostname""")
    ] = None,
    site_id: Annotated[Optional[str], Field(description="""Site id""")] = None,
    model: Annotated[Optional[str], Field(description="""Device model""")] = None,
    managed: Annotated[
        Optional[str],
        Field(
            description="""for switches and gateways, to filter on managed/unmanaged devices. enum: `true`, `false`"""
        ),
    ] = None,
    mac: Annotated[Optional[str], Field(description="""AP mac""")] = None,
    version: Annotated[Optional[str], Field(description="""Version""")] = None,
    ip_address: Optional[str] = None,
    mxtunnel_status: Annotated[
        Mxtunnel_status, Field(description="""MxTunnel status, enum: `up`, `down`""")
    ] = Mxtunnel_status.NONE,
    mxedge_id: Annotated[
        Optional[str],
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
    type: Type = Type.AP,
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
    limit: Annotated[int, Field(default=100)] = 100,
) -> dict:
    """Count by Distinct Attributes of Org Devices"""

    ctx = get_context()
    request: Request = get_http_request()
    cloud = request.query_params.get("cloud", None)
    apitoken = request.headers.get("X-Authorization", None)
    apisession = mistapi.APISession(
        host=cloud,
        apitoken=apitoken,
    )

    response = mistapi.api.v1.orgs.devices.countOrgDevices(
        apisession,
        org_id=str(org_id),
        distinct=distinct.value,
        hostname=hostname,
        site_id=site_id,
        model=model,
        managed=managed,
        mac=mac,
        version=version,
        ip_address=ip_address,
        mxtunnel_status=mxtunnel_status.value,
        mxedge_id=mxedge_id,
        lldp_system_name=lldp_system_name,
        lldp_system_desc=lldp_system_desc,
        lldp_port_id=lldp_port_id,
        lldp_mgmt_addr=lldp_mgmt_addr,
        type=type.value,
        start=start,
        end=end,
        duration=duration,
        limit=limit,
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
