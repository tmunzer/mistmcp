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
from enum import Enum


mcp = mcp_instance.get()


class Edr_provider(Enum):
    CROWDSTRIKE = "crowdstrike"
    SENTINELONE = "sentinelone"
    NONE = None


class Edr_status(Enum):
    SENTINELONE_HEALTHY = "sentinelone_healthy"
    SENTINELONE_INFECTED = "sentinelone_infected"
    CROWDSTRIKE_LOW = "crowdstrike_low"
    CROWDSTRIKE_MEDIUM = "crowdstrike_medium"
    CROWDSTRIKE_HIGH = "crowdstrike_high"
    CROWDSTRIKE_CRITICAL = "crowdstrike_critical"
    CROWDSTRIKE_INFORMATIONAL = "crowdstrike_informational"
    NONE = None


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
    ap: Annotated[
        Optional[str | None], Field(description="""AP MAC connected to by client""")
    ] = None,
    auth_type: Annotated[
        Optional[str | None],
        Field(
            description="""Authentication type, e.g. 'eap-tls', 'eap-peap', 'eap-ttls', 'eap-teap', 'mab', 'psk', 'device-auth'"""
        ),
    ] = None,
    edr_managed: Annotated[
        Optional[bool | None],
        Field(
            description="""Filters NAC clients that are integrated with EDR providers"""
        ),
    ] = None,
    edr_provider: Annotated[
        Optional[Edr_provider | None],
        Field(description="""EDR provider of client's organization"""),
    ] = Edr_provider.NONE,
    edr_status: Annotated[
        Optional[Edr_status | None],
        Field(description="""EDR Status of the NAC client"""),
    ] = Edr_status.NONE,
    family: Annotated[
        Optional[str | None],
        Field(
            description="""Client family, e.g. 'Phone/Tablet/Wearable', 'Access Point'"""
        ),
    ] = None,
    hostname: Annotated[
        Optional[str | None],
        Field(description="""Client hostname, e.g. 'my-laptop', 'my-phone'"""),
    ] = None,
    idp_id: Annotated[
        Optional[str | None], Field(description="""SSO ID, if present and used""")
    ] = None,
    mac: Annotated[Optional[str | None], Field(description="""MAC address""")] = None,
    mdm_compliance: Annotated[
        Optional[str | None],
        Field(
            description="""MDM compliance of client i.e 'compliant', 'not compliant'"""
        ),
    ] = None,
    mdm_provider: Annotated[
        Optional[str | None],
        Field(
            description="""MDM provider of client’s organization eg 'intune', 'jamf'"""
        ),
    ] = None,
    mdm_managed: Annotated[
        Optional[bool | None],
        Field(description="""Filters NAC clients that are managed by MDM providers"""),
    ] = None,
    mfg: Annotated[
        Optional[str | None],
        Field(description="""Client manufacturer, e.g. 'apple', 'cisco', 'juniper'"""),
    ] = None,
    model: Annotated[
        Optional[str | None],
        Field(description="""Client model, e.g. 'iPhone 12', 'MX100'"""),
    ] = None,
    nacrule_name: Annotated[
        Optional[str | None], Field(description="""NAC Policy Rule Name matched""")
    ] = None,
    nacrule_id: Annotated[
        Optional[str | None], Field(description="""NAC Policy Rule ID, if matched""")
    ] = None,
    nacrule_matched: Annotated[
        Optional[bool | None], Field(description="""NAC Policy Rule Matched""")
    ] = None,
    nas_vendor: Annotated[
        Optional[str | None], Field(description="""Vendor of NAS device""")
    ] = None,
    nas_ip: Annotated[
        Optional[str | None], Field(description="""IP address of NAS device""")
    ] = None,
    ingress_vlan: Annotated[
        Optional[str | None],
        Field(description="""Vendor specific Vlan ID in radius requests"""),
    ] = None,
    os: Annotated[
        Optional[str | None],
        Field(
            description="""Client OS, e.g. 'iOS 18.1', 'Android', 'Windows', 'Linux'"""
        ),
    ] = None,
    ssid: Annotated[Optional[str | None], Field(description="""SSID""")] = None,
    status: Annotated[
        Optional[Status | None],
        Field(
            description="""Connection status of client i.e 'permitted', 'denied, 'session_stared', 'session_ended'"""
        ),
    ] = Status.NONE,
    text: Annotated[
        Optional[str | None],
        Field(
            description="""partial / full MAC address, last_username, device_mac, nas_ip or last_ap"""
        ),
    ] = None,
    timestamp: Annotated[
        Optional[float | None], Field(description="""Start time, in epoch""")
    ] = None,
    type: Annotated[
        Optional[str | None],
        Field(description="""Client type i.e. 'wireless', 'wired' etc."""),
    ] = None,
    usermac_label: Annotated[
        Optional[List[str] | None],
        Field(description="""Labels derived from usermac entry"""),
    ] = None,
    username: Annotated[
        Optional[str | None], Field(description="""Username presented by the client""")
    ] = None,
    vlan: Annotated[
        Optional[str | None],
        Field(description="""Vlan name or ID assigned to the client"""),
    ] = None,
    site_id: Annotated[
        Optional[str | None],
        Field(description="""Site id if assigned, null if not assigned"""),
    ] = None,
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
            description="""On which field the list should be sorted, -prefix represents DESC order."""
        ),
    ] = None,
    search_after: Annotated[
        Optional[str | None],
        Field(
            description="""Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed."""
        ),
    ] = None,
) -> dict | list:
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
        ap=ap if ap else None,
        auth_type=auth_type if auth_type else None,
        edr_managed=edr_managed if edr_managed else None,
        edr_provider=edr_provider.value if edr_provider else None,
        edr_status=edr_status.value if edr_status else None,
        family=family if family else None,
        hostname=hostname if hostname else None,
        idp_id=idp_id if idp_id else None,
        mac=mac if mac else None,
        mdm_compliance=mdm_compliance if mdm_compliance else None,
        mdm_provider=mdm_provider if mdm_provider else None,
        mdm_managed=mdm_managed if mdm_managed else None,
        mfg=mfg if mfg else None,
        model=model if model else None,
        nacrule_name=nacrule_name if nacrule_name else None,
        nacrule_id=nacrule_id if nacrule_id else None,
        nacrule_matched=nacrule_matched if nacrule_matched else None,
        nas_vendor=nas_vendor if nas_vendor else None,
        nas_ip=nas_ip if nas_ip else None,
        ingress_vlan=ingress_vlan if ingress_vlan else None,
        os=os if os else None,
        ssid=ssid if ssid else None,
        status=status.value if status else None,
        text=text if text else None,
        timestamp=timestamp if timestamp else None,
        type=type if type else None,
        usermac_label=usermac_label if usermac_label else None,
        username=username if username else None,
        vlan=vlan if vlan else None,
        site_id=site_id if site_id else None,
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
