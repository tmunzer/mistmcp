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
from enum import Enum




class Type(Enum):
    EGRESS_VLAN_NAMES = "egress_vlan_names"
    GBP_TAG = "gbp_tag"
    MATCH = "match"
    RADIUS_ATTRS = "radius_attrs"
    RADIUS_GROUP = "radius_group"
    RADIUS_VENDOR_ATTRS = "radius_vendor_attrs"
    SESSION_TIMEOUT = "session_timeout"
    USERNAME_ATTR = "username_attr"
    VLAN = "vlan"
    NONE = None

class Match(Enum):
    CERT_CN = "cert_cn"
    CERT_ISSUER = "cert_issuer"
    CERT_SAN = "cert_san"
    CERT_SERIAL = "cert_serial"
    CERT_SUB = "cert_sub"
    CERT_TEMPLATE = "cert_template"
    CLIENT_MAC = "client_mac"
    IDP_ROLE = "idp_role"
    INGRESS_VLAN = "ingress_vlan"
    MDM_STATUS = "mdm_status"
    NAS_IP = "nas_ip"
    RADIUS_GROUP = "radius_group"
    REALM = "realm"
    SSID = "ssid"
    USER_NAME = "user_name"
    USERMAC_LABEL = "usermac_label"
    NONE = None


def add_tool():
    mcp.add_tool(
        fn=listOrgNacTags,
        name="listOrgNacTags",
        description="""Get List of Org NAC Tags""",
        tags={"Orgs NAC Tags"},
        annotations={
            "title": "listOrgNacTags",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True
        }
    )

def remove_tool():
    mcp.remove_tool("listOrgNacTags")

async def listOrgNacTags(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    type: Annotated[Type, Field(description="""Type of NAC Tag. enum: `egress_vlan_names`, `gbp_tag`, `match`, `radius_attrs`, `radius_group`, `radius_vendor_attrs`, `session_timeout`, `username_attr`, `vlan`""",min_length=1)] = Type.NONE,
    name: Annotated[Optional[str], Field(description="""Name of NAC Tag""")] | None = None,
    match: Annotated[Match, Field(description="""if `type`==`match`, Type of NAC Tag. enum: `cert_cn`, `cert_issuer`, `cert_san`, `cert_serial`, `cert_sub`, `cert_template`, `client_mac`, `idp_role`, `ingress_vlan`, `mdm_status`, `nas_ip`, `radius_group`, `realm`, `ssid`, `user_name`, `usermac_label`""",min_length=1)] = Match.NONE,
    limit: Annotated[int, Field(default=100)] = 100,
    page: Annotated[int, Field(ge=1,default=1)] = 1,
) -> dict:
    """Get List of Org NAC Tags"""

    response = mistapi.api.v1.orgs.nactags.listOrgNacTags(
            apisession,
            org_id=str(org_id),
            type=type.value,
            name=name,
            match=match.value,
            limit=limit,
            page=page,
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
