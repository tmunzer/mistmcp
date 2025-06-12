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
from enum import Enum


class Type(Enum):
    ARP = "arp"
    CURL = "curl"
    DHCP = "dhcp"
    DHCP6 = "dhcp6"
    DNS = "dns"
    LAN_CONNECTIVITY = "lan_connectivity"
    RADIUS = "radius"
    SPEEDTEST = "speedtest"
    NONE = None


class Protocol(Enum):
    PING = "ping"
    TRACEROUTE = "traceroute"
    NONE = None


def add_tool() -> None:
    mcp.add_tool(
        fn=searchSiteSyntheticTest,
        name="searchSiteSyntheticTest",
        description="""Search Site Synthetic Testing""",
        tags={"Sites Synthetic Tests"},
        annotations={
            "title": "searchSiteSyntheticTest",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True,
        },
    )


def remove_tool() -> None:
    mcp.remove_tool("searchSiteSyntheticTest")


async def searchSiteSyntheticTest(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    mac: Annotated[Optional[str], Field(description="""Device MAC Address""")]
    | None = None,
    port_id: Annotated[
        Optional[str],
        Field(description="""Port_id used to run the test (for SSR only)"""),
    ]
    | None = None,
    vlan_id: Annotated[Optional[str], Field(description="""VLAN ID""")] | None = None,
    by: Annotated[Optional[str], Field(description="""Entity who triggers the test""")]
    | None = None,
    reason: Annotated[Optional[str], Field(description="""Test failure reason""")]
    | None = None,
    type: Annotated[Type, Field(description="""Synthetic test type""")] = Type.NONE,
    protocol: Annotated[
        Protocol, Field(description="""Connectivity protocol""")
    ] = Protocol.NONE,
    tenant: Annotated[
        Optional[str],
        Field(description="""Tenant network in which lan_connectivity test was run"""),
    ]
    | None = None,
) -> dict:
    """Search Site Synthetic Testing"""

    response = mistapi.api.v1.sites.synthetic_test.searchSiteSyntheticTest(
        apisession,
        site_id=str(site_id),
        mac=mac,
        port_id=port_id,
        vlan_id=vlan_id,
        by=by,
        reason=reason,
        type=type.value,
        protocol=protocol.value,
        tenant=tenant,
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
