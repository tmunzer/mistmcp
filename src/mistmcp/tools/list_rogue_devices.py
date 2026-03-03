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
from fastmcp import Context
from fastmcp.exceptions import ToolError
from mistmcp.request_processor import get_apisession
from mistmcp.response_processor import process_response
from mistmcp.response_formatter import format_response
from mistmcp.server import mcp
from mistmcp.logger import logger

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


class Rogue_type(Enum):
    AP = "ap"
    CLIENT = "client"


class Rogue_ap_type(Enum):
    HONEYPOT = "honeypot"
    LAN = "lan"
    OTHERS = "others"
    SPOOF = "spoof"


@mcp.tool(
    name="mist_list_rogue_devices",
    description="""Retrieve a list of rogue devices (APs or clients) for a site, with optional filters for rogue AP type and time range""",
    tags={"sites_rogues"},
    annotations={
        "title": "List rogue devices",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def list_rogue_devices(
    site_id: Annotated[UUID, Field(description="""Site ID""")],
    rogue_type: Annotated[
        Rogue_type, Field(description="""Type of rogue device to filter by""")
    ],
    rogue_ap_type: Annotated[
        Optional[Rogue_ap_type | None],
        Field(
            description="""Type of rogue AP to filter by. Only applicable when filtering for rogue APs"""
        ),
    ] = None,
    start: Annotated[
        Optional[str | None],
        Field(description="""Start of time range (epoch seconds)"""),
    ] = None,
    end: Annotated[
        Optional[str | None], Field(description="""End of time range (epoch seconds)""")
    ] = None,
    limit: Annotated[
        int, Field(description="""Max number of results per page""", default=10)
    ] = 10,
    ctx: Context | None = None,
) -> dict | list | str:
    """Retrieve a list of rogue devices (APs or clients) for a site, with optional filters for rogue AP type and time range"""

    logger.debug("Tool list_rogue_devices called")

    apisession, response_format = get_apisession()

    object_type = rogue_type
    match object_type.value:
        case "ap":
            response = mistapi.api.v1.sites.insights.listSiteRogueAPs(
                apisession,
                site_id=str(site_id),
                type=rogue_ap_type.value if rogue_ap_type else None,
                limit=limit,
                start=str(start) if start else None,
                end=str(end) if end else None,
            )
            await process_response(response)
        case "client":
            response = mistapi.api.v1.sites.insights.listSiteRogueClients(
                apisession,
                site_id=str(site_id),
                limit=limit,
                start=str(start) if start else None,
                end=str(end) if end else None,
            )
            await process_response(response)

        case _:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Rogue_type]}",
                }
            )

    return format_response(response, response_format)
