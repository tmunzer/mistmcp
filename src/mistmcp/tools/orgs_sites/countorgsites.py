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


class Distinct(Enum):
    ANALYTIC_ENABLED = "analytic_enabled"
    APP_WAKING = "app_waking"
    ASSET_ENABLED = "asset_enabled"
    AUTO_UPGRADE_ENABLED = "auto_upgrade_enabled"
    AUTO_UPGRADE_VERSION = "auto_upgrade_version"
    COUNTRY_CODE = "country_code"
    HONEYPOT_ENABLED = "honeypot_enabled"
    ID = "id"
    LOCATE_UNCONNECTED = "locate_unconnected"
    MESH_ENABLED = "mesh_enabled"
    NAME = "name"
    REMOTE_SYSLOG_ENABLED = "remote_syslog_enabled"
    ROGUE_ENABLED = "rogue_enabled"
    RTSA_ENABLED = "rtsa_enabled"
    VNA_ENABLED = "vna_enabled"
    WIFI_ENABLED = "wifi_enabled"


def add_tool() -> None:
    mcp.add_tool(
        fn=countOrgSites,
        name="countOrgSites",
        description="""Count by Distinct Attributes of Sites""",
        tags={"Orgs Sites"},
        annotations={
            "title": "countOrgSites",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True,
        },
    )


def remove_tool() -> None:
    mcp.remove_tool("countOrgSites")


async def countOrgSites(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    distinct: Distinct = Distinct.ID,
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
) -> dict:
    """Count by Distinct Attributes of Sites"""

    response = mistapi.api.v1.orgs.sites.countOrgSites(
        apisession,
        org_id=str(org_id),
        distinct=distinct.value,
        start=start,
        end=end,
        duration=duration,
        limit=limit,
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
