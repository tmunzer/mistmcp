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
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


mcp = mcp_instance.get()


class Key_mgmt(Enum):
    WPA2_PSK = "WPA2_PSK"
    WPA2_PSK_CCMP = "WPA2_PSK_CCMP"
    WPA2_PSK_FT = "WPA2_PSK_FT"
    WPA2_PSK_SHA256 = "WPA2_PSK_SHA256"
    WPA3_EAP_SHA256 = "WPA3_EAP_SHA256"
    WPA3_EAP_SHA256_CCMP = "WPA3_EAP_SHA256_CCMP"
    WPA3_EAP_FT_GCMP256 = "WPA3_EAP_FT_GCMP256"
    WPA3_SAE_FT = "WPA3_SAE_FT"
    WPA3_SAE_PSK = "WPA3_SAE_PSK"
    NONE = None


class Proto(Enum):
    A = "a"
    AC = "ac"
    AX = "ax"
    B = "b"
    BE = "be"
    G = "g"
    N = "n"
    NONE = None


class Band(Enum):
    B24 = "24"
    B5 = "5"
    B6 = "6"
    NONE = None


@mcp.tool(
    enabled=False,
    name="searchOrgWirelessClientEvents",
    description="""Get Org Clients Events""",
    tags={"clients"},
    annotations={
        "title": "searchOrgWirelessClientEvents",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchOrgWirelessClientEvents(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    type: Annotated[
        Optional[str | None],
        Field(
            description="""See [List Device Events Definitions](/#operations/listDeviceEventsDefinitions)"""
        ),
    ] = None,
    reason_code: Annotated[
        Optional[int | None], Field(description="""For assoc/disassoc events""")
    ] = None,
    ssid: Annotated[Optional[str | None], Field(description="""SSID Name""")] = None,
    ap: Annotated[Optional[str | None], Field(description="""AP MAC""")] = None,
    key_mgmt: Annotated[
        Optional[Key_mgmt | None],
        Field(
            description="""Key Management Protocol, e.g. WPA2-PSK, WPA3-SAE, WPA2-Enterprise"""
        ),
    ] = Key_mgmt.NONE,
    proto: Annotated[
        Optional[Proto | None], Field(description="""a / b / g / n / ac / ax""")
    ] = Proto.NONE,
    band: Annotated[
        Optional[Band | None], Field(description="""802.11 Band""")
    ] = Band.NONE,
    wlan_id: Annotated[Optional[UUID | None], Field(description="""WLAN_id""")] = None,
    nacrule_id: Annotated[
        Optional[UUID | None], Field(description="""Nacrule_id""")
    ] = None,
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
    limit: Optional[int | None] = None,
    search_after: Annotated[
        Optional[str | None],
        Field(
            description="""Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed."""
        ),
    ] = None,
) -> dict | list:
    """Get Org Clients Events"""

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

    response = mistapi.api.v1.orgs.clients.searchOrgWirelessClientEvents(
        apisession,
        org_id=str(org_id),
        type=type if type else None,
        reason_code=reason_code if reason_code else None,
        ssid=ssid if ssid else None,
        ap=ap if ap else None,
        key_mgmt=key_mgmt.value if key_mgmt else None,
        proto=proto.value if proto else None,
        band=band.value if band else None,
        wlan_id=str(wlan_id) if wlan_id else None,
        nacrule_id=str(nacrule_id) if nacrule_id else None,
        start=start if start else None,
        end=end if end else None,
        duration=duration if duration else None,
        sort=sort if sort else None,
        limit=limit if limit else None,
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
