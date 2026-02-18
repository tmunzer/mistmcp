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
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum



mcp = get_mcp()

if not mcp:
    raise RuntimeError(
        "MCP instance not found. Make sure to initialize the MCP server before defining tools."
    )



class Source(Enum):
    LLDP = "lldp"
    MAC = "mac"
    NONE = None



@mcp.tool(
    enabled=True,
    name = "searchOrgWiredClients",
    description = """Search for Wired Clients in orgNote: For list of available `type` values, please refer to [List Client Events Definitions](/#operations/listClientEventsDefinitions)""",
    tags = {"clients"},
    annotations = {
        "title": "searchOrgWiredClients",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchOrgWiredClients(
    
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    auth_state: Annotated[Optional[str | None], Field(description="""Authentication state""")] = None,
    auth_method: Annotated[Optional[str | None], Field(description="""Authentication method""")] = None,
    source: Annotated[Optional[Source | None], Field(description="""source from where the client was learned (lldp, mac)""")] = Source.NONE,
    site_id: Annotated[Optional[str | None], Field(description="""Site ID""")] = None,
    device_mac: Annotated[Optional[str | None], Field(description="""Device mac (Gateway/Switch) where the client has connected to""")] = None,
    mac: Annotated[Optional[str | None], Field(description="""Partial / full MAC address""")] = None,
    port_id: Annotated[Optional[str | None], Field(description="""Port id where the client has connected to""")] = None,
    vlan: Annotated[Optional[int | None], Field(description="""VLAN""")] = None,
    ip: Optional[str | None] = None,
    manufacture: Annotated[Optional[str | None], Field(description="""Client manufacturer""")] = None,
    text: Annotated[Optional[str | None], Field(description="""Partial / full MAC address, hostname or username""")] = None,
    nacrule_id: Annotated[Optional[str | None], Field(description="""nacrule_id""")] = None,
    dhcp_hostname: Annotated[Optional[str | None], Field(description="""DHCP Hostname""")] = None,
    dhcp_fqdn: Annotated[Optional[str | None], Field(description="""DHCP FQDN""")] = None,
    dhcp_client_identifier: Annotated[Optional[str | None], Field(description="""DHCP Client Identifier""")] = None,
    dhcp_vendor_class_identifier: Annotated[Optional[str | None], Field(description="""DHCP Vendor Class Identifier""")] = None,
    dhcp_request_params: Annotated[Optional[str | None], Field(description="""DHCP Request Parameters""")] = None,
    limit: Optional[int | None] = None,
    start: Annotated[Optional[str | None], Field(description="""Start time (epoch timestamp in seconds, or relative string like '-1d', '-1w')""")] = None,
    end: Annotated[Optional[str | None], Field(description="""End time (epoch timestamp in seconds, or relative string like '-1d', '-2h', 'now')""")] = None,
    duration: Annotated[Optional[str | None], Field(description="""Duration like 7d, 2w""")] = None,
    sort: Annotated[Optional[str | None], Field(description="""On which field the list should be sorted, -prefix represents DESC order""")] = None,
    search_after: Annotated[Optional[str | None], Field(description="""Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed.""")] = None,
) -> dict|list:
    """Search for Wired Clients in orgNote: For list of available `type` values, please refer to [List Client Events Definitions](/#operations/listClientEventsDefinitions)"""

    apisession = get_apisession()
    data = {}
    
    
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
            dhcp_client_identifier=dhcp_client_identifier if dhcp_client_identifier else None,
            dhcp_vendor_class_identifier=dhcp_vendor_class_identifier if dhcp_vendor_class_identifier else None,
            dhcp_request_params=dhcp_request_params if dhcp_request_params else None,
            limit=limit if limit else None,
            start=start if start else None,
            end=end if end else None,
            duration=duration if duration else None,
            sort=sort if sort else None,
            search_after=search_after if search_after else None,
    )
    await process_response(response)
    
    data = response.data


    return data
