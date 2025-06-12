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
from fastmcp.server.dependencies import get_context
from fastmcp.exceptions import ToolError
from mistmcp.__server import mcp
from mistmcp.__mistapi import apisession
from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID


def add_tool() -> None:
    mcp.add_tool(
        fn=searchSiteNacClients,
        name="searchSiteNacClients",
        description="""Search Site NAC Clients""",
        tags={"Sites Clients - NAC"},
        annotations={
            "title": "searchSiteNacClients",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True,
        },
    )


def remove_tool() -> None:
    mcp.remove_tool("searchSiteNacClients")


async def searchSiteNacClients(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    nacrule_id: Annotated[
        Optional[str], Field(description="""NAC Policy Rule ID, if matched""")
    ]
    | None = None,
    nacrule_matched: Annotated[
        Optional[bool], Field(description="""NAC Policy Rule Matched""")
    ]
    | None = None,
    auth_type: Annotated[
        Optional[str],
        Field(
            description="""Authentication type, e.g. 'eap-tls', 'eap-peap', 'eap-ttls', 'eap-teap', 'mab', 'psk', 'device-auth'"""
        ),
    ]
    | None = None,
    vlan: Annotated[
        Optional[str], Field(description="""Vlan name or ID assigned to the client""")
    ]
    | None = None,
    nas_vendor: Annotated[Optional[str], Field(description="""Vendor of NAS device""")]
    | None = None,
    idp_id: Annotated[
        Optional[str], Field(description="""SSO ID, if present and used""")
    ]
    | None = None,
    ssid: Annotated[Optional[str], Field(description="""SSID""")] | None = None,
    username: Annotated[
        Optional[str], Field(description="""Username presented by the client""")
    ]
    | None = None,
    timestamp: Annotated[Optional[float], Field(description="""Start time, in epoch""")]
    | None = None,
    ap: Annotated[Optional[str], Field(description="""AP MAC connected to by client""")]
    | None = None,
    mac: Annotated[Optional[str], Field(description="""MAC address""")] | None = None,
    mdm_managed: Annotated[
        Optional[bool],
        Field(description="""Filters NAC clients that are managed by MDM providers"""),
    ]
    | None = None,
    mxedge_id: Annotated[
        Optional[str],
        Field(description="""ID of Mist Edge that the client is connected through"""),
    ]
    | None = None,
    nacrule_name: Annotated[
        Optional[str], Field(description="""NAC Policy Rule Name matched""")
    ]
    | None = None,
    status: Annotated[
        Optional[str],
        Field(
            description="""Connection status of client i.e 'permitted', 'denied, 'session_ended'"""
        ),
    ]
    | None = None,
    type: Annotated[
        Optional[str],
        Field(description="""Client type i.e. 'wireless', 'wired' etc."""),
    ]
    | None = None,
    mdm_compliance: Annotated[
        Optional[str],
        Field(
            description="""MDM compliance of client i.e 'compliant', 'not compliant'"""
        ),
    ]
    | None = None,
    mdm_provider: Annotated[
        Optional[str],
        Field(
            description="""MDM provider of client’s organisation eg 'intune', 'jamf'"""
        ),
    ]
    | None = None,
    sort: Annotated[
        Optional[str],
        Field(
            description="""Sort options, ‘-‘ prefix represents DESC order, default is wcid in ASC order"""
        ),
    ]
    | None = None,
    usermac_label: Annotated[
        Optional[list], Field(description="""Labels derived from usermac entry""")
    ]
    | None = None,
    ingress_vlan: Annotated[
        Optional[str],
        Field(description="""Vendor specific Vlan ID in radius requests"""),
    ]
    | None = None,
    start: Annotated[
        Optional[int],
        Field(
            description="""Start datetime, can be epoch or relative time like -1d, -1w; -1d if not specified"""
        ),
    ]
    | None = None,
    end: Annotated[
        Optional[int],
        Field(
            description="""End datetime, can be epoch or relative time like -1d, -2h; now if not specified"""
        ),
    ]
    | None = None,
    duration: Annotated[
        str, Field(description="""Duration like 7d, 2w""", default="1d")
    ] = "1d",
    limit: Annotated[int, Field(default=100)] = 100,
    page: Annotated[int, Field(ge=1, default=1)] = 1,
) -> dict:
    """Search Site NAC Clients"""

    response = mistapi.api.v1.sites.nac_clients.searchSiteNacClients(
        apisession,
        site_id=str(site_id),
        nacrule_id=nacrule_id,
        nacrule_matched=nacrule_matched,
        auth_type=auth_type,
        vlan=vlan,
        nas_vendor=nas_vendor,
        idp_id=idp_id,
        ssid=ssid,
        username=username,
        timestamp=timestamp,
        ap=ap,
        mac=mac,
        mdm_managed=mdm_managed,
        mxedge_id=mxedge_id,
        nacrule_name=nacrule_name,
        status=status,
        type=type,
        mdm_compliance=mdm_compliance,
        mdm_provider=mdm_provider,
        sort=sort,
        usermac_label=usermac_label,
        ingress_vlan=ingress_vlan,
        start=start,
        end=end,
        duration=duration,
        limit=limit,
        page=page,
    )

    ctx = get_context()

    if response.status_code != 200:
        error = {"status_code": response.status_code, "message": ""}
        if response.data:
            await ctx.error(
                f"Got HTTP{response.status_code} with details {response.data}"
            )
            error["message"] = json.dumps(response.data)
        elif response.status_code == 400:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] = json.dumps(
                "Bad Request. The API endpoint exists but its syntax/payload is incorrect, detail may be given"
            )
        elif response.status_code == 401:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] = json.dumps("Unauthorized")
        elif response.status_code == 403:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] = json.dumps("Unauthorized")
        elif response.status_code == 401:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] = json.dumps("Permission Denied")
        elif response.status_code == 404:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] = json.dumps(
                "Not found. The API endpoint doesn’t exist or resource doesn’t exist"
            )
        elif response.status_code == 429:
            await ctx.error(f"Got HTTP{response.status_code}")
            error["message"] = json.dumps(
                "Too Many Request. The API Token used for the request reached the 5000 API Calls per hour threshold"
            )
        raise ToolError(error)

    return response.data
