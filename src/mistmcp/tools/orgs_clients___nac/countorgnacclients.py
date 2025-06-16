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
from mistmcp.server_factory import mcp_instance

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


mcp = mcp_instance.get()


class Distinct(Enum):
    AUTH_TYPE = "auth_type"
    LAST_AP = "last_ap"
    LAST_NACRULE_ID = "last_nacrule_id"
    LAST_NAS_VENDOR = "last_nas_vendor"
    LAST_SSID = "last_ssid"
    LAST_STATUS = "last_status"
    LAST_USERNAME = "last_username"
    LAST_VLAN = "last_vlan"
    MAC = "mac"
    MDM_COMPLIANCE = "mdm_compliance"
    MDM_PROVIDER = "mdm_provider"
    TYPE = "type"


@mcp.tool(
    enabled=True,
    name="countOrgNacClients",
    description="""Count by Distinct Attributes of NAC Clients""",
    tags={"Orgs Clients - NAC"},
    annotations={
        "title": "countOrgNacClients",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def countOrgNacClients(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    distinct: Annotated[
        Distinct, Field(description="""NAC Policy Rule ID, if matched""")
    ] = Distinct.TYPE,
    last_nacrule_id: Annotated[
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
    last_vlan_id: Annotated[Optional[str], Field(description="""Vlan ID""")] = None,
    last_nas_vendor: Annotated[
        Optional[str], Field(description="""Vendor of NAS device""")
    ] = None,
    idp_id: Annotated[
        Optional[str], Field(description="""SSO ID, if present and used""")
    ] = None,
    last_ssid: Annotated[Optional[str], Field(description="""SSID""")] = None,
    last_username: Annotated[
        Optional[str], Field(description="""Username presented by the client""")
    ] = None,
    timestamp: Annotated[
        Optional[float], Field(description="""Start time, in epoch""")
    ] = None,
    site_id: Annotated[
        Optional[str],
        Field(description="""Site id if assigned, null if not assigned"""),
    ] = None,
    last_ap: Annotated[
        Optional[str], Field(description="""AP MAC connected to by client""")
    ] = None,
    mac: Annotated[Optional[str], Field(description="""MAC address""")] = None,
    last_status: Annotated[
        Optional[str],
        Field(
            description="""Connection status of client i.e 'permitted', 'denied, 'session_ended'"""
        ),
    ] = None,
    type: Annotated[
        Optional[str],
        Field(description="""Client type i.e. 'wireless', 'wired' etc."""),
    ] = None,
    mdm_compliance_status: Annotated[
        Optional[str],
        Field(
            description="""MDM compliance of client i.e 'compliant', 'not compliant'"""
        ),
    ] = None,
    mdm_provider: Annotated[
        Optional[str],
        Field(
            description="""MDM provider of client’s organization eg 'intune', 'jamf'"""
        ),
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
    """Count by Distinct Attributes of NAC Clients"""

    ctx = get_context()
    request: Request = get_http_request()
    cloud = request.query_params.get("cloud", None)
    apitoken = request.headers.get("X-Authorization", None)
    apisession = mistapi.APISession(
        host=cloud,
        apitoken=apitoken,
    )

    response = mistapi.api.v1.orgs.nac_clients.countOrgNacClients(
        apisession,
        org_id=str(org_id),
        distinct=distinct.value,
        last_nacrule_id=last_nacrule_id,
        nacrule_matched=nacrule_matched,
        auth_type=auth_type,
        last_vlan_id=last_vlan_id,
        last_nas_vendor=last_nas_vendor,
        idp_id=idp_id,
        last_ssid=last_ssid,
        last_username=last_username,
        timestamp=timestamp,
        site_id=site_id,
        last_ap=last_ap,
        mac=mac,
        last_status=last_status,
        type=type,
        mdm_compliance_status=mdm_compliance_status,
        mdm_provider=mdm_provider,
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
