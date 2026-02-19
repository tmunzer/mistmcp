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
from fastmcp import Context
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


class Type(Enum):
    WAN = "wan"
    WXTUNNEL = "wxtunnel"


@mcp.tool(
    name="searchOrgTunnelsStats",
    description="""By default the endpoint returns only `wxtunnel` type stats, to get `wan` type statsyou need to specify `type=wan` in the query parameters.Tunnel types:- `wxtunnel` (default) - A WxLan Tunnel (WxTunnel) are used to create a secure connection between Juniper Mist Access Points and third-party VPN concentrators using protocols such as L2TPv3 or dmvpn.- `wan` - A WAN Tunnel is a secure connection between two Gateways, typically used for site-to-site or mesh connectivity. It can be configured with various protocols and encryption methods.If `type` is not specified or `type`==`wxtunnel`, the following parameters are supported:- `mxcluster_id` - the MX cluster ID- `site_id` - the site ID- `wxtunnel_id` - the WX tunnel ID- `ap` - the AP MAC addressIf `type`==`wan`, the following parameters are supported:- `mac` - the MAC address of the WAN device- `node` - the node ID- `peer_ip` - the peer IP address- `peer_host` - the peer host name- `ip` - the IP address of the WAN device- `tunnel_name` - the name of the tunnel- `protocol` - the protocol used for the tunnel- `auth_algo` - the authentication algorithm used for the tunnel- `encrypt_algo` - the encryption algorithm used for the tunnel- `ike_version` - the IKE version used for the tunnel- `up` - the status of the tunnel (up or down)""",
    tags={"orgs_stats"},
    annotations={
        "title": "searchOrgTunnelsStats",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchOrgTunnelsStats(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    mxcluster_id: Annotated[
        Optional[str | None], Field(description="""If `type`==`wxtunnel`""")
    ] = None,
    site_id: Annotated[
        Optional[str | None], Field(description="""ID of the Mist Site""")
    ] = None,
    wxtunnel_id: Annotated[
        Optional[str | None], Field(description="""If `type`==`wxtunnel`""")
    ] = None,
    ap: Annotated[
        Optional[str | None], Field(description="""If `type`==`wxtunnel`""")
    ] = None,
    mac: Annotated[
        Optional[str | None], Field(description="""If `type`==`wan`""")
    ] = None,
    node: Annotated[
        Optional[str | None], Field(description="""If `type`==`wan`""")
    ] = None,
    peer_ip: Annotated[
        Optional[str | None], Field(description="""If `type`==`wan`""")
    ] = None,
    peer_host: Annotated[
        Optional[str | None], Field(description="""If `type`==`wan`""")
    ] = None,
    ip: Annotated[
        Optional[str | None], Field(description="""If `type`==`wan`""")
    ] = None,
    tunnel_name: Annotated[
        Optional[str | None], Field(description="""If `type`==`wan`""")
    ] = None,
    protocol: Annotated[
        Optional[str | None], Field(description="""If `type`==`wan`""")
    ] = None,
    auth_algo: Annotated[
        Optional[str | None], Field(description="""If `type`==`wan`""")
    ] = None,
    encrypt_algo: Annotated[
        Optional[str | None], Field(description="""If `type`==`wan`""")
    ] = None,
    ike_version: Annotated[
        Optional[str | None], Field(description="""If `type`==`wan`""")
    ] = None,
    up: Annotated[
        Optional[str | None], Field(description="""If `type`==`wan`""")
    ] = None,
    type: Optional[Type | None] = Type.WXTUNNEL,
    limit: Optional[int | None] = None,
    start: Annotated[
        Optional[str | None],
        Field(
            description="""Start time (epoch timestamp in seconds, or relative string like '-1d', '-1w')"""
        ),
    ] = None,
    end: Annotated[
        Optional[str | None],
        Field(
            description="""End time (epoch timestamp in seconds, or relative string like '-1d', '-2h', 'now')"""
        ),
    ] = None,
    duration: Annotated[
        Optional[str | None], Field(description="""Duration like 7d, 2w""")
    ] = None,
    sort: Annotated[
        Optional[str | None],
        Field(
            description="""On which field the list should be sorted, -prefix represents DESC order"""
        ),
    ] = None,
    search_after: Annotated[
        Optional[str | None],
        Field(
            description="""Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed."""
        ),
    ] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """By default the endpoint returns only `wxtunnel` type stats, to get `wan` type statsyou need to specify `type=wan` in the query parameters.Tunnel types:- `wxtunnel` (default) - A WxLan Tunnel (WxTunnel) are used to create a secure connection between Juniper Mist Access Points and third-party VPN concentrators using protocols such as L2TPv3 or dmvpn.- `wan` - A WAN Tunnel is a secure connection between two Gateways, typically used for site-to-site or mesh connectivity. It can be configured with various protocols and encryption methods.If `type` is not specified or `type`==`wxtunnel`, the following parameters are supported:- `mxcluster_id` - the MX cluster ID- `site_id` - the site ID- `wxtunnel_id` - the WX tunnel ID- `ap` - the AP MAC addressIf `type`==`wan`, the following parameters are supported:- `mac` - the MAC address of the WAN device- `node` - the node ID- `peer_ip` - the peer IP address- `peer_host` - the peer host name- `ip` - the IP address of the WAN device- `tunnel_name` - the name of the tunnel- `protocol` - the protocol used for the tunnel- `auth_algo` - the authentication algorithm used for the tunnel- `encrypt_algo` - the encryption algorithm used for the tunnel- `ike_version` - the IKE version used for the tunnel- `up` - the status of the tunnel (up or down)"""

    apisession, response_format = get_apisession()
    data = {}

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
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
