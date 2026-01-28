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
from fastmcp.server.dependencies import get_context, get_http_request
from fastmcp.exceptions import ToolError, ClientError, NotFoundError
from starlette.requests import Request
from mistmcp.config import config
from mistmcp.server_factory import mcp_instance
#from mistmcp.server_factory import mcp

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


mcp = mcp_instance.get()



class Type(Enum):
    WAN = "wan"
    WXTUNNEL = "wxtunnel"



@mcp.tool(
    enabled=False,
    name = "searchOrgTunnelsStats",
    description = """By default the endpoint returns only `wxtunnel` type stats, to get `wan` type statsyou need to specify `type=wan` in the query parameters.Tunnel types:- `wxtunnel` (default) - A WxLan Tunnel (WxTunnel) are used to create a secure connection between Juniper Mist Access Points and third-party VPN concentrators using protocols such as L2TPv3 or dmvpn.- `wan` - A WAN Tunnel is a secure connection between two Gateways, typically used for site-to-site or mesh connectivity. It can be configured with various protocols and encryption methods.If `type` is not specified or `type`==`wxtunnel`, the following parameters are supported:- `mxcluster_id` - the MX cluster ID- `site_id` - the site ID- `wxtunnel_id` - the WX tunnel ID- `ap` - the AP MAC addressIf `type`==`wan`, the following parameters are supported:- `mac` - the MAC address of the WAN device- `node` - the node ID- `peer_ip` - the peer IP address- `peer_host` - the peer host name- `ip` - the IP address of the WAN device- `tunnel_name` - the name of the tunnel- `protocol` - the protocol used for the tunnel- `auth_algo` - the authentication algorithm used for the tunnel- `encrypt_algo` - the encryption algorithm used for the tunnel- `ike_version` - the IKE version used for the tunnel- `up` - the status of the tunnel (up or down)""",
    tags = {"orgs_stats"},
    annotations = {
        "title": "searchOrgTunnelsStats",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchOrgTunnelsStats(
    
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    mxcluster_id: Annotated[Optional[str], Field(description="""If `type`==`wxtunnel`""")],
    site_id: Annotated[Optional[str], Field(description="""ID of the Mist Site""")],
    wxtunnel_id: Annotated[Optional[str], Field(description="""If `type`==`wxtunnel`""")],
    ap: Annotated[Optional[str], Field(description="""If `type`==`wxtunnel`""")],
    mac: Annotated[Optional[str], Field(description="""If `type`==`wan`""")],
    node: Annotated[Optional[str], Field(description="""If `type`==`wan`""")],
    peer_ip: Annotated[Optional[str], Field(description="""If `type`==`wan`""")],
    peer_host: Annotated[Optional[str], Field(description="""If `type`==`wan`""")],
    ip: Annotated[Optional[str], Field(description="""If `type`==`wan`""")],
    tunnel_name: Annotated[Optional[str], Field(description="""If `type`==`wan`""")],
    protocol: Annotated[Optional[str], Field(description="""If `type`==`wan`""")],
    auth_algo: Annotated[Optional[str], Field(description="""If `type`==`wan`""")],
    encrypt_algo: Annotated[Optional[str], Field(description="""If `type`==`wan`""")],
    ike_version: Annotated[Optional[str], Field(description="""If `type`==`wan`""")],
    up: Annotated[Optional[str], Field(description="""If `type`==`wan`""")],
    type: Optional[Type] = Type.WXTUNNEL,
    limit: Optional[int],
    start: Annotated[Optional[str], Field(description="""Start time (epoch timestamp in seconds, or relative string like '-1d', '-1w')""")],
    end: Annotated[Optional[str], Field(description="""End time (epoch timestamp in seconds, or relative string like '-1d', '-2h', 'now')""")],
    duration: Annotated[Optional[str], Field(description="""Duration like 7d, 2w""")],
    sort: Annotated[Optional[str], Field(description="""On which field the list should be sorted, -prefix represents DESC order""")],
    search_after: Annotated[Optional[str], Field(description="""Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed.""")],
) -> dict|list:
    """By default the endpoint returns only `wxtunnel` type stats, to get `wan` type statsyou need to specify `type=wan` in the query parameters.Tunnel types:- `wxtunnel` (default) - A WxLan Tunnel (WxTunnel) are used to create a secure connection between Juniper Mist Access Points and third-party VPN concentrators using protocols such as L2TPv3 or dmvpn.- `wan` - A WAN Tunnel is a secure connection between two Gateways, typically used for site-to-site or mesh connectivity. It can be configured with various protocols and encryption methods.If `type` is not specified or `type`==`wxtunnel`, the following parameters are supported:- `mxcluster_id` - the MX cluster ID- `site_id` - the site ID- `wxtunnel_id` - the WX tunnel ID- `ap` - the AP MAC addressIf `type`==`wan`, the following parameters are supported:- `mac` - the MAC address of the WAN device- `node` - the node ID- `peer_ip` - the peer IP address- `peer_host` - the peer host name- `ip` - the IP address of the WAN device- `tunnel_name` - the name of the tunnel- `protocol` - the protocol used for the tunnel- `auth_algo` - the authentication algorithm used for the tunnel- `encrypt_algo` - the encryption algorithm used for the tunnel- `ike_version` - the IKE version used for the tunnel- `up` - the status of the tunnel (up or down)"""

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

    
    response = mistapi.api.v1.orgs.stats.searchOrgTunnelsStats(
            apisession,
            org_id=str(org_id),
            mxcluster_id=mxcluster_id if mxcluster_id else None,
            site_id=site_id if site_id else None,
            wxtunnel_id=wxtunnel_id if wxtunnel_id else None,
            ap=ap if ap else None,
            mac=mac if mac else None,
            node=node if node else None,
            peer_ip=peer_ip if peer_ip else None,
            peer_host=peer_host if peer_host else None,
            ip=ip if ip else None,
            tunnel_name=tunnel_name if tunnel_name else None,
            protocol=protocol if protocol else None,
            auth_algo=auth_algo if auth_algo else None,
            encrypt_algo=encrypt_algo if encrypt_algo else None,
            ike_version=ike_version if ike_version else None,
            up=up if up else None,
            type=type.value if type else Type.WXTUNNEL.value,
            limit=limit if limit else None,
            start=start if start else None,
            end=end if end else None,
            duration=duration if duration else None,
            sort=sort if sort else None,
            search_after=search_after if search_after else None,
    )


    if response.status_code != 200:
        api_error = {
            "status_code": response.status_code,
            "message": ""
        }
        if response.data:
            #await ctx.error(f"Got HTTP{response.status_code} with details {response.data}")
            api_error["message"] =json.dumps(response.data)
        elif response.status_code == 400:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] =json.dumps("Bad Request. The API endpoint exists but its syntax/payload is incorrect, detail may be given")
        elif response.status_code == 401:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] =json.dumps("Unauthorized")
        elif response.status_code == 403:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] =json.dumps("Unauthorized")
        elif response.status_code == 401:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] =json.dumps("Permission Denied")
        elif response.status_code == 404:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] =json.dumps("Not found. The API endpoint doesn’t exist or resource doesn’t exist")
        elif response.status_code == 429:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] =json.dumps("Too Many Request. The API Token used for the request reached the 5000 API Calls per hour threshold")
        raise ToolError(api_error)

    return response.data
