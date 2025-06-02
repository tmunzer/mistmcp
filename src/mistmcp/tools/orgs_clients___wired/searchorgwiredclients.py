""""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""
import json
import mistapi
from fastmcp.server.dependencies import get_context
from fastmcp.exceptions import ToolError
from mistmcp.__server import mcp
from mistmcp.__mistapi import apisession
from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID





def add_tool():
    mcp.add_tool(
        fn=searchOrgWiredClients,
        name="searchOrgWiredClients",
        description="""Search for Wired Clients in orgNote: For list of available `type` values, please refer to [List Client Events Definitions]($e/Constants%20Events/listClientEventsDefinitions)""",
        tags={"Orgs Clients - Wired"},
        annotations={
            "title": "searchOrgWiredClients",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True
        }
    )

def remove_tool():
    mcp.remove_tool("searchOrgWiredClients")

async def searchOrgWiredClients(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    auth_state: Annotated[Optional[str], Field(description="""Authentication state""")] | None = None,
    auth_method: Annotated[Optional[str], Field(description="""Authentication method""")] | None = None,
    site_id: Annotated[Optional[str], Field(description="""Site ID""")] | None = None,
    device_mac: Annotated[Optional[str], Field(description="""Device mac (Gateway/Switch) where the client has connected to""")] | None = None,
    mac: Annotated[Optional[str], Field(description="""Partial / full MAC address""")] | None = None,
    port_id: Annotated[Optional[str], Field(description="""Port id where the client has connected to""")] | None = None,
    vlan: Annotated[Optional[int], Field(description="""VLAN""")] | None = None,
    ip_address: Optional[str] | None = None,
    manufacture: Annotated[Optional[str], Field(description="""Client manufacturer""")] | None = None,
    text: Annotated[Optional[str], Field(description="""Partial / full MAC address, hostname or username""")] | None = None,
    nacrule_id: Annotated[Optional[str], Field(description="""nacrule_id""")] | None = None,
    dhcp_hostname: Annotated[Optional[str], Field(description="""DHCP Hostname""")] | None = None,
    dhcp_fqdn: Annotated[Optional[str], Field(description="""DHCP FQDN""")] | None = None,
    dhcp_client_identifier: Annotated[Optional[str], Field(description="""DHCP Client Identifier""")] | None = None,
    dhcp_vendor_class_identifier: Annotated[Optional[str], Field(description="""DHCP Vendor Class Identifier""")] | None = None,
    dhcp_request_params: Annotated[Optional[str], Field(description="""DHCP Request Parameters""")] | None = None,
    limit: Annotated[int, Field(default=100)] = 100,
    start: Annotated[Optional[int], Field(description="""Start datetime, can be epoch or relative time like -1d, -1w; -1d if not specified""")] | None = None,
    end: Annotated[Optional[int], Field(description="""End datetime, can be epoch or relative time like -1d, -2h; now if not specified""")] | None = None,
    duration: Annotated[str, Field(description="""Duration like 7d, 2w""",default="1d")] = "1d",
) -> dict:
    """Search for Wired Clients in orgNote: For list of available `type` values, please refer to [List Client Events Definitions]($e/Constants%20Events/listClientEventsDefinitions)"""

    response = mistapi.api.v1.orgs.wired_clients.searchOrgWiredClients(
            apisession,
            org_id=str(org_id),
            auth_state=auth_state,
            auth_method=auth_method,
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
    
    
    ctx = get_context()
    
    if response.status_code != 200:
        error = {
            "status_code": response.status_code,
            "message": ""
        }
        if response.data:
            await ctx.error(f"Got HTTP{response.status_code} with details {response.data}")
            error["message"] =json.dumps(response.data)
        elif response.status_code == 400:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] =json.dumps("Bad Request. The API endpoint exists but its syntax/payload is incorrect, detail may be given")
        elif response.status_code == 401:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] =json.dumps("Unauthorized")
        elif response.status_code == 403:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] =json.dumps("Unauthorized")
        elif response.status_code == 401:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] =json.dumps("Permission Denied")
        elif response.status_code == 404:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] =json.dumps("Not found. The API endpoint doesn’t exist or resource doesn’t exist")
        elif response.status_code == 429:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] =json.dumps("Too Many Request. The API Token used for the request reached the 5000 API Calls per hour threshold")
        raise ToolError(error)
            
    return response.data
