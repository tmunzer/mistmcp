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
from typing import Annotated, Optional, List
from uuid import UUID


mcp = mcp_instance.get()


@mcp.tool(
    enabled=False,
    name="searchOrgNacClientEvents",
    description="""Search NAC Client Events""",
    tags={"clients"},
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
    ],
    nacrule_id: Annotated[
        Optional[UUID], Field(description="""NAC Policy Rule ID, if matched""")
    ],
    nacrule_matched: Annotated[
        Optional[bool], Field(description="""NAC Policy Rule Matched""")
    ],
    dryrun_nacrule_id: Annotated[
        Optional[str],
        Field(description="""NAC Policy Dry Run Rule ID, if present and matched"""),
    ],
    dryrun_nacrule_matched: Annotated[
        Optional[bool],
        Field(
            description="""True - if dryrun rule present and matched with priority, False - if not matched or not present"""
        ),
    ],
    auth_type: Annotated[
        Optional[str],
        Field(
            description="""Authentication type, e.g. 'eap-tls', 'eap-peap', 'eap-ttls', 'eap-teap', 'mab', 'psk', 'device-auth'"""
        ),
    ],
    vlan: Annotated[
        Optional[int], Field(description="""Vlan name or ID assigned to the client""")
    ],
    nas_vendor: Annotated[Optional[str], Field(description="""Vendor of NAS device""")],
    bssid: Annotated[Optional[str], Field(description="""BSSID""")],
    idp_id: Annotated[
        Optional[UUID], Field(description="""SSO ID, if present and used""")
    ],
    idp_role: Annotated[
        Optional[str], Field(description="""IDP returned roles/groups for the user""")
    ],
    idp_username: Annotated[
        Optional[str],
        Field(description="""Username presented to the Identity Provider"""),
    ],
    resp_attrs: Annotated[
        Optional[List[str]],
        Field(description="""Radius attributes returned by NAC to NAS derive"""),
    ],
    ssid: Annotated[Optional[str], Field(description="""SSID""")],
    username: Annotated[
        Optional[str], Field(description="""Username presented by the client""")
    ],
    site_id: Annotated[Optional[str], Field(description="""Site id""")],
    ap: Annotated[Optional[str], Field(description="""AP MAC""")],
    random_mac: Annotated[Optional[bool], Field(description="""AP random macMAC""")],
    mac: Annotated[Optional[str], Field(description="""MAC address""")],
    timestamp: Annotated[
        Optional[float], Field(description="""Start time, in epoch""")
    ],
    usermac_label: Annotated[
        Optional[str], Field(description="""Labels derived from usermac entry""")
    ],
    text: Annotated[
        Optional[str],
        Field(description="""Partial / full MAC address, username, device_mac or ap"""),
    ],
    nas_ip: Annotated[Optional[str], Field(description="""IP address of NAS device""")],
    ingress_vlan: Annotated[
        Optional[str],
        Field(description="""Vendor specific Vlan ID in radius requests"""),
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
            description="""On which field the list should be sorted, -prefix represents DESC order."""
        ),
    ],
    search_after: Annotated[
        Optional[str],
        Field(
            description="""Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed."""
        ),
    ],
) -> dict | list:
    """Search NAC Client Events"""

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

    response = mistapi.api.v1.orgs.nac_clients.searchOrgNacClientEvents(
        apisession,
        org_id=str(org_id),
        type=type if type else None,
        nacrule_id=str(nacrule_id) if nacrule_id else None,
        nacrule_matched=nacrule_matched if nacrule_matched else None,
        dryrun_nacrule_id=dryrun_nacrule_id if dryrun_nacrule_id else None,
        dryrun_nacrule_matched=dryrun_nacrule_matched
        if dryrun_nacrule_matched
        else None,
        auth_type=auth_type if auth_type else None,
        vlan=vlan if vlan else None,
        nas_vendor=nas_vendor if nas_vendor else None,
        bssid=bssid if bssid else None,
        idp_id=str(idp_id) if idp_id else None,
        idp_role=idp_role if idp_role else None,
        idp_username=idp_username if idp_username else None,
        resp_attrs=resp_attrs if resp_attrs else None,
        ssid=ssid if ssid else None,
        username=username if username else None,
        site_id=site_id if site_id else None,
        ap=ap if ap else None,
        random_mac=random_mac if random_mac else None,
        mac=mac if mac else None,
        timestamp=timestamp if timestamp else None,
        usermac_label=usermac_label if usermac_label else None,
        text=text if text else None,
        nas_ip=nas_ip if nas_ip else None,
        ingress_vlan=ingress_vlan if ingress_vlan else None,
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
