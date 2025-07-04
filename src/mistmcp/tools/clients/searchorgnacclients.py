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


class Status(Enum):
    PERMITTED = "permitted"
    SESSION_STARTED = "session_started"
    SESSION_ENDED = "session_ended"
    DENIED = "denied"
    NONE = None


@mcp.tool(
    enabled=False,
    name="searchOrgNacClients",
    description="""Search Org NAC Clients""",
    tags={"clients"},
    annotations={
        "title": "searchOrgNacClients",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchOrgNacClients(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    nacrule_id: Annotated[
        Optional[str], Field(description="""NAC Policy Rule ID, if matched""")
    ] = None,
    nacrule_matched: Annotated[
        Optional[bool], Field(description="""NAC Policy Rule Matched""")
    ] = None,
    auth_type: Annotated[
        Optional[str],
        Field(
            description="""Authentication type, e.g. 'eap-tls', 'eap-peap', 'eap-ttls', 'eap-teap', 'mab', 'psk', 'device-auth'"""
        ),
    ] = None,
    vlan: Annotated[
        Optional[str], Field(description="""Vlan name or ID assigned to the client""")
    ] = None,
    nas_vendor: Annotated[
        Optional[str], Field(description="""Vendor of NAS device""")
    ] = None,
    idp_id: Annotated[
        Optional[str], Field(description="""SSO ID, if present and used""")
    ] = None,
    ssid: Annotated[Optional[str], Field(description="""SSID""")] = None,
    username: Annotated[
        Optional[str], Field(description="""Username presented by the client""")
    ] = None,
    timestamp: Annotated[
        Optional[float], Field(description="""Start time, in epoch""")
    ] = None,
    site_id: Annotated[
        Optional[str],
        Field(description="""Site id if assigned, null if not assigned"""),
    ] = None,
    ap: Annotated[
        Optional[str], Field(description="""AP MAC connected to by client""")
    ] = None,
    mac: Annotated[Optional[str], Field(description="""MAC address""")] = None,
    mdm_managed: Annotated[
        Optional[bool],
        Field(description="""Filters NAC clients that are managed by MDM providers"""),
    ] = None,
    status: Annotated[
        Optional[Status],
        Field(
            description="""Connection status of client i.e 'permitted', 'denied, 'session_stared', 'session_ended'"""
        ),
    ] = Status.NONE,
    type: Annotated[
        Optional[str],
        Field(description="""Client type i.e. 'wireless', 'wired' etc."""),
    ] = None,
    mdm_compliance: Annotated[
        Optional[str],
        Field(
            description="""MDM compliance of client i.e 'compliant', 'not compliant'"""
        ),
    ] = None,
    family: Annotated[
        Optional[str],
        Field(
            description="""Client family, e.g. 'Phone/Tablet/Wearable', 'Access Point'"""
        ),
    ] = None,
    model: Annotated[
        Optional[str], Field(description="""Client model, e.g. 'iPhone 12', 'MX100'""")
    ] = None,
    os: Annotated[
        Optional[str],
        Field(
            description="""Client OS, e.g. 'iOS 18.1', 'Android', 'Windows', 'Linux'"""
        ),
    ] = None,
    hostname: Annotated[
        Optional[str],
        Field(description="""Client hostname, e.g. 'my-laptop', 'my-phone'"""),
    ] = None,
    mfg: Annotated[
        Optional[str],
        Field(description="""Client manufacturer, e.g. 'apple', 'cisco', 'juniper'"""),
    ] = None,
    mdm_provider: Annotated[
        Optional[str],
        Field(
            description="""MDM provider of client’s organization eg 'intune', 'jamf'"""
        ),
    ] = None,
    sort: Annotated[
        Optional[str],
        Field(
            description="""Sort options, ‘-‘ prefix represents DESC order, default is wcid in ASC order"""
        ),
    ] = None,
    usermac_label: Annotated[
        Optional[list], Field(description="""Labels derived from usermac entry""")
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
    page: Annotated[int, Field(ge=1, default=1)] = 1,
) -> dict:
    """Search Org NAC Clients"""

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

    response = mistapi.api.v1.orgs.nac_clients.searchOrgNacClients(
        apisession,
        org_id=str(org_id),
        nacrule_id=nacrule_id,
        nacrule_matched=nacrule_matched,
        auth_type=auth_type,
        vlan=vlan,
        nas_vendor=nas_vendor,
        idp_id=idp_id,
        ssid=ssid,
        username=username,
        timestamp=timestamp,
        site_id=site_id,
        ap=ap,
        mac=mac,
        mdm_managed=mdm_managed,
        status=status.value if status else None,
        type=type,
        mdm_compliance=mdm_compliance,
        family=family,
        model=model,
        os=os,
        hostname=hostname,
        mfg=mfg,
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
                "Not found. The API endpoint doesn't exist or resource doesn't exist"
            )
        elif response.status_code == 429:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps(
                "Too Many Request. The API Token used for the request reached the 5000 API Calls per hour threshold"
            )
        raise ToolError(api_error)

    return response.data
