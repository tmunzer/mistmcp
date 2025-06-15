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


@mcp.tool(
    enabled=True,
    name="searchOrgNacClientEvents",
    description="""Search NAC Client Events""",
    tags={"Orgs Clients - NAC"},
    annotations={
        "title": "searchOrgNacClientEvents",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchOrgNacClientEvents(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    type: Annotated[
        Optional[str],
        Field(
            description="""See [List Device Events Definitions](/#operations/listNacEventsDefinitions)"""
        ),
    ] = None,
    nacrule_id: Annotated[
        Optional[UUID], Field(description="""NAC Policy Rule ID, if matched""")
    ] = None,
    nacrule_matched: Annotated[
        Optional[bool], Field(description="""NAC Policy Rule Matched""")
    ] = None,
    dryrun_nacrule_id: Annotated[
        Optional[str],
        Field(description="""NAC Policy Dry Run Rule ID, if present and matched"""),
    ] = None,
    dryrun_nacrule_matched: Annotated[
        Optional[bool],
        Field(
            description="""True - if dryrun rule present and matched with priority, False - if not matched or not present"""
        ),
    ] = None,
    auth_type: Annotated[
        Optional[str],
        Field(
            description="""Authentication type, e.g. 'eap-tls', 'eap-peap', 'eap-ttls', 'eap-teap', 'mab', 'psk', 'device-auth'"""
        ),
    ] = None,
    vlan: Annotated[
        Optional[int], Field(description="""Vlan name or ID assigned to the client""")
    ] = None,
    nas_vendor: Annotated[
        Optional[str], Field(description="""Vendor of NAS device""")
    ] = None,
    bssid: Annotated[Optional[str], Field(description="""BSSID""")] = None,
    idp_id: Annotated[
        Optional[UUID], Field(description="""SSO ID, if present and used""")
    ] = None,
    idp_role: Annotated[
        Optional[str], Field(description="""IDP returned roles/groups for the user""")
    ] = None,
    idp_username: Annotated[
        Optional[str],
        Field(description="""Username presented to the Identity Provider"""),
    ] = None,
    resp_attrs: Annotated[
        Optional[list],
        Field(description="""Radius attributes returned by NAC to NAS derive"""),
    ] = None,
    ssid: Annotated[Optional[str], Field(description="""SSID""")] = None,
    username: Annotated[
        Optional[str], Field(description="""Username presented by the client""")
    ] = None,
    site_id: Annotated[Optional[str], Field(description="""Site id""")] = None,
    ap: Annotated[Optional[str], Field(description="""AP MAC""")] = None,
    random_mac: Annotated[
        Optional[bool], Field(description="""AP random macMAC""")
    ] = None,
    mac: Annotated[Optional[str], Field(description="""MAC address""")] = None,
    timestamp: Annotated[
        Optional[float], Field(description="""Start time, in epoch""")
    ] = None,
    usermac_label: Annotated[
        Optional[str], Field(description="""Labels derived from usermac entry""")
    ] = None,
    text: Annotated[
        Optional[str],
        Field(description="""Partial / full MAC address, username, device_mac or ap"""),
    ] = None,
    nas_ip: Annotated[
        Optional[str], Field(description="""IP address of NAS device""")
    ] = None,
    sort: Annotated[
        Optional[str],
        Field(
            description="""Sort options, ‘-‘ prefix represents DESC order, default is wcid in ASC order"""
        ),
    ] = None,
    ingress_vlan: Annotated[
        Optional[str],
        Field(description="""Vendor specific Vlan ID in radius requests"""),
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
    """Search NAC Client Events"""

    ctx = get_context()
    request: Request = get_http_request()
    cloud = request.query_params.get("cloud", None)
    apitoken = request.headers.get("X-Authorization", None)
    apisession = mistapi.APISession(
        host=cloud,
        apitoken=apitoken,
    )

    response = mistapi.api.v1.orgs.nac_clients.searchOrgNacClientEvents(
        apisession,
        org_id=str(org_id),
        type=type,
        nacrule_id=str(nacrule_id),
        nacrule_matched=nacrule_matched,
        dryrun_nacrule_id=dryrun_nacrule_id,
        dryrun_nacrule_matched=dryrun_nacrule_matched,
        auth_type=auth_type,
        vlan=vlan,
        nas_vendor=nas_vendor,
        bssid=bssid,
        idp_id=str(idp_id),
        idp_role=idp_role,
        idp_username=idp_username,
        resp_attrs=resp_attrs,
        ssid=ssid,
        username=username,
        site_id=site_id,
        ap=ap,
        random_mac=random_mac,
        mac=mac,
        timestamp=timestamp,
        usermac_label=usermac_label,
        text=text,
        nas_ip=nas_ip,
        sort=sort,
        ingress_vlan=ingress_vlan,
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
