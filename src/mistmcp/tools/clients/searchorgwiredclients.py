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
    auth_state: Annotated[Optional[str], Field(description="""Authentication state""")],
    auth_method: Annotated[
        Optional[str], Field(description="""Authentication method""")
    ],
    source: Annotated[
        Optional[Source],
        Field(description="""source from where the client was learned (lldp, mac)"""),
    ],
    site_id: Annotated[Optional[str], Field(description="""Site ID""")],
    device_mac: Annotated[
        Optional[str],
        Field(
            description="""Device mac (Gateway/Switch) where the client has connected to"""
        ),
    ],
    mac: Annotated[Optional[str], Field(description="""Partial / full MAC address""")],
    port_id: Annotated[
        Optional[str],
        Field(description="""Port id where the client has connected to"""),
    ],
    vlan: Annotated[Optional[int], Field(description="""VLAN""")],
    ip: Optional[str],
    manufacture: Annotated[Optional[str], Field(description="""Client manufacturer""")],
    text: Annotated[
        Optional[str],
        Field(description="""Partial / full MAC address, hostname or username"""),
    ],
    nacrule_id: Annotated[Optional[str], Field(description="""nacrule_id""")],
    dhcp_hostname: Annotated[Optional[str], Field(description="""DHCP Hostname""")],
    dhcp_fqdn: Annotated[Optional[str], Field(description="""DHCP FQDN""")],
    dhcp_client_identifier: Annotated[
        Optional[str], Field(description="""DHCP Client Identifier""")
    ],
    dhcp_vendor_class_identifier: Annotated[
        Optional[str], Field(description="""DHCP Vendor Class Identifier""")
    ],
    dhcp_request_params: Annotated[
        Optional[str], Field(description="""DHCP Request Parameters""")
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
        auth_state=auth_state if auth_state else None,
        auth_method=auth_method if auth_method else None,
        source=source.value if source else None,
        site_id=site_id if site_id else None,
        device_mac=device_mac if device_mac else None,
        mac=mac if mac else None,
        port_id=port_id if port_id else None,
        vlan=vlan if vlan else None,
        ip=ip if ip else None,
        manufacture=manufacture if manufacture else None,
        text=text if text else None,
        nacrule_id=nacrule_id if nacrule_id else None,
        dhcp_hostname=dhcp_hostname if dhcp_hostname else None,
        dhcp_fqdn=dhcp_fqdn if dhcp_fqdn else None,
        dhcp_client_identifier=dhcp_client_identifier
        if dhcp_client_identifier
        else None,
        dhcp_vendor_class_identifier=dhcp_vendor_class_identifier
        if dhcp_vendor_class_identifier
        else None,
        dhcp_request_params=dhcp_request_params if dhcp_request_params else None,
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
