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
        fn=searchSiteWiredClients,
        name="searchSiteWiredClients",
        description="""Search Wired Clients""",
        tags={"Sites Clients - Wired"},
        annotations={
            "title": "searchSiteWiredClients",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True
        }
    )

def remove_tool():
    mcp.remove_tool("searchSiteWiredClients")

async def searchSiteWiredClients(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    device_mac: Annotated[Optional[str], Field(description="""Device mac""")] | None = None,
    mac: Annotated[Optional[str], Field(description="""Client mac""")] | None = None,
    ip: Annotated[Optional[str], Field(description="""Client ip""")] | None = None,
    port_id: Annotated[Optional[str], Field(description="""Port id""")] | None = None,
    vlan: Annotated[Optional[str], Field(description="""VLAN""")] | None = None,
    manufacture: Annotated[Optional[str], Field(description="""Manufacture""")] | None = None,
    text: Annotated[Optional[str], Field(description="""Single entry of hostname/mac""")] | None = None,
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
    """Search Wired Clients"""

    response = mistapi.api.v1.sites.wired_clients.searchSiteWiredClients(
            apisession,
            site_id=str(site_id),
            device_mac=device_mac,
            mac=mac,
            ip=ip,
            port_id=port_id,
            vlan=vlan,
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
