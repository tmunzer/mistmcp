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

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


mcp = mcp_instance.get()


class Distinct(Enum):
    HOSTNAME = "hostname"
    LLDP_MGMT_ADDR = "lldp_mgmt_addr"
    LLDP_PORT_ID = "lldp_port_id"
    LLDP_SYSTEM_DESC = "lldp_system_desc"
    LLDP_SYSTEM_NAME = "lldp_system_name"
    MAP_ID = "map_id"
    MODEL = "model"
    MXEDGE_ID = "mxedge_id"
    MXTUNNEL_STATUS = "mxtunnel_status"
    VERSION = "version"


@mcp.tool(
    enabled=True,
    name="countSiteDevices",
    description="""Counts the number of entries in ap events history for distinct field with given filters""",
    tags={"Sites Devices"},
    annotations={
        "title": "countSiteDevices",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def countSiteDevices(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    distinct: Distinct = Distinct.MODEL,
    hostname: Optional[str] = None,
    model: Optional[str] = None,
    mac: Optional[str] = None,
    version: Optional[str] = None,
    mxtunnel_status: Optional[str] = None,
    mxedge_id: Annotated[
        Optional[str], Field(description="""ID of the Mist Mxedge""")
    ] = None,
    lldp_system_name: Optional[str] = None,
    lldp_system_desc: Optional[str] = None,
    lldp_port_id: Annotated[
        Optional[str], Field(description="""ID of the Mist Lldp_port""")
    ] = None,
    lldp_mgmt_addr: Optional[str] = None,
    map_id: Annotated[
        Optional[str], Field(description="""ID of the Mist Map""")
    ] = None,
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
    """Counts the number of entries in ap events history for distinct field with given filters"""

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

    apisession = mistapi.APISession(
        host=cloud,
        apitoken=apitoken,
    )

    response = mistapi.api.v1.sites.devices.countSiteDevices(
        apisession,
        site_id=str(site_id),
        distinct=distinct.value,
        hostname=hostname,
        model=model,
        mac=mac,
        version=version,
        mxtunnel_status=mxtunnel_status,
        mxedge_id=mxedge_id,
        lldp_system_name=lldp_system_name,
        lldp_system_desc=lldp_system_desc,
        lldp_port_id=lldp_port_id,
        lldp_mgmt_addr=lldp_mgmt_addr,
        map_id=map_id,
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
