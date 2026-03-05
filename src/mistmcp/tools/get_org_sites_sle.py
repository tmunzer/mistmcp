"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import mistapi
from fastmcp import Context
from fastmcp.exceptions import ToolError
from mistmcp.request_processor import get_apisession
from mistmcp.response_processor import process_response, handle_network_error
from mistmcp.response_formatter import format_response
from mistmcp.server import mcp
from mistmcp.logger import logger

from pydantic import Field
from typing import Annotated
from uuid import UUID
from enum import Enum


class Sle(Enum):
    WIFI = "wifi"
    WIRED = "wired"
    WAN = "wan"


@mcp.tool(
    name="mist_get_org_sites_sle",
    description="""Get SLE summary for the organization sites.""",
    tags={"sles"},
    annotations={
        "title": "Get org sites sle",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def get_org_sites_sle(
    org_id: Annotated[UUID, Field(description="""Organization ID""")],
    sle: Annotated[
        Sle,
        Field(
            description="""Type of SLE data to retrieve for the sites. Possible values are `wifi`, `wired`, and `wan`"""
        ),
    ],
    start: Annotated[
        int, Field(description="""Start of time range (epoch seconds)""", default=None)
    ],
    end: Annotated[
        int, Field(description="""End of time range (epoch seconds)""", default=None)
    ],
    limit: Annotated[
        int, Field(description="""Max number of results per page""", default=20)
    ] = 20,
) -> dict | list | str:
    """Get SLE summary for the organization sites."""

    logger.debug("Tool get_org_sites_sle called")

    apisession, response_format = await get_apisession()

    try:
        response = mistapi.api.v1.orgs.insights.getOrgSitesSle(
            apisession,
            org_id=str(org_id),
            sle=sle.value,
            start=str(start) if start else None,
            end=str(end) if end else None,
            limit=limit,
        )
        await process_response(response)
    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
