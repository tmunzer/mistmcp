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


class Source(Enum):
    LLDP = "lldp"
    MAC = "mac"
    NONE = None


@mcp.tool(
    enabled=False,
    name="searchOrgWiredClients",
    description="""Search for Wired Clients in orgNote: For list of available `type` values, please refer to [List Client Events Definitions](/#operations/listClientEventsDefinitions)""",
    tags={"clients"},
    annotations={
        "title": "searchOrgWiredClients",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchOrgWiredClients(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    auth_state: Annotated[
        Optional[str], Field(description="""Authentication state""")
    ] = None,
    auth_method: Annotated[
        Optional[str], Field(description="""Authentication method""")
    ] = None,
    source: Annotated[
        Optional[Source],
        Field(description="""source from where the client was learned (lldp, mac)"""),
    ] = Source.NONE,
    site_id: Annotated[Optional[str], Field(description="""Site ID""")] = None,
    device_mac: Annotated[
        Optional[str],
        Field(
            description="""Device mac (Gateway/Switch) where the client has connected to"""
        ),
    ] = None,
    mac: Annotated[
        Optional[str], Field(description="""Partial / full MAC address""")
    ] = None,
    port_id: Annotated[
        Optional[str],
        Field(description="""Port id where the client has connected to"""),
    ] = None,
    vlan: Annotated[Optional[int], Field(description="""VLAN""")] = None,
    ip_address: Optional[str] = None,
    manufacture: Annotated[
        Optional[str], Field(description="""Client manufacturer""")
    ] = None,
    text: Annotated[
        Optional[str],
        Field(description="""Partial / full MAC address, hostname or username"""),
    ] = None,
    nacrule_id: Annotated[Optional[str], Field(description="""nacrule_id""")] = None,
    dhcp_hostname: Annotated[
        Optional[str], Field(description="""DHCP Hostname""")
    ] = None,
    dhcp_fqdn: Annotated[Optional[str], Field(description="""DHCP FQDN""")] = None,
    dhcp_client_identifier: Annotated[
        Optional[str], Field(description="""DHCP Client Identifier""")
    ] = None,
    dhcp_vendor_class_identifier: Annotated[
        Optional[str], Field(description="""DHCP Vendor Class Identifier""")
    ] = None,
    dhcp_request_params: Annotated[
        Optional[str], Field(description="""DHCP Request Parameters""")
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
    """Search for Wired Clients in orgNote: For list of available `type` values, please refer to [List Client Events Definitions](/#operations/listClientEventsDefinitions)"""

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

    response = mistapi.api.v1.orgs.wired_clients.searchOrgWiredClients(
        apisession,
        org_id=str(org_id),
        auth_state=auth_state,
        auth_method=auth_method,
        source=source.value if source else None,
        site_id=site_id,
        device_mac=device_mac,
        mac=mac,
        port_id=port_id,
        vlan=vlan,
        ip_address=ip_address,
        manufacture=manufacture,
        text=text,
        nacrule_id=nacrule_id,
        dhcp_hostname=dhcp_hostname,
        dhcp_fqdn=dhcp_fqdn,
        dhcp_client_identifier=dhcp_client_identifier,
        dhcp_vendor_class_identifier=dhcp_vendor_class_identifier,
        dhcp_request_params=dhcp_request_params,
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
