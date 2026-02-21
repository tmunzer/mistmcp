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


class Client_type(Enum):
    WIRELESS = "wireless"
    WIRED = "wired"
    VTY = "vty"
    NONE = None


@mcp.tool(
    name="searchOrgClientFingerprints",
    description="""Search Client Fingerprints""",
    tags={"orgs_nac"},
    annotations={
        "title": "searchOrgClientFingerprints",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchOrgClientFingerprints(
    site_id: Annotated[UUID, Field(description="""Site ID""")],
    family: Annotated[
        Optional[str | None],
        Field(description="""Device Category  of the client device"""),
    ] = None,
    client_type: Annotated[
        Optional[Client_type | None],
        Field(description="""Whether client is wired or wireless"""),
    ] = Client_type.NONE,
    model: Annotated[
        Optional[str | None], Field(description="""Model name of the client device""")
    ] = None,
    mfg: Annotated[
        Optional[str | None],
        Field(description="""Manufacturer name of the client device"""),
    ] = None,
    os: Annotated[
        Optional[str | None],
        Field(description="""Operating System name and version of the client device"""),
    ] = None,
    os_type: Annotated[
        Optional[str | None],
        Field(description="""Operating system name of the client device"""),
    ] = None,
    mac: Annotated[
        Optional[str | None], Field(description="""MAC address of the client device""")
    ] = None,
    limit: Annotated[
        int, Field(description="""Max number of results per page""", default=100)
    ] = 100,
    start: Annotated[
        Optional[str | None],
        Field(description="""Start of time range (epoch seconds)"""),
    ] = None,
    end: Annotated[
        Optional[str | None], Field(description="""End of time range (epoch seconds)""")
    ] = None,
    duration: Annotated[
        Optional[str | None],
        Field(description="""Time range duration (e.g. 1d, 1h, 10m)"""),
    ] = None,
    interval: Annotated[
        Optional[str | None],
        Field(description="""Aggregation interval (e.g. 1h, 1d)"""),
    ] = None,
    sort: Annotated[Optional[str | None], Field(description="""Sort field""")] = None,
    search_after: Annotated[
        Optional[str | None],
        Field(
            description="""Pagination cursor from '_next' URL of previous response"""
        ),
    ] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """Search Client Fingerprints"""

    logger.debug("Tool searchOrgClientFingerprints called")

    apisession, response_format = get_apisession()

    response = mistapi.api.v1.sites.insights.searchOrgClientFingerprints(
        apisession,
        site_id=str(site_id),
        family=family if family else None,
        client_type=client_type.value if client_type else None,
        model=model if model else None,
        mfg=mfg if mfg else None,
        os=os if os else None,
        os_type=os_type if os_type else None,
        mac=mac if mac else None,
        limit=limit,
        start=start if start else None,
        end=end if end else None,
        duration=duration if duration else None,
        interval=interval if interval else None,
        sort=sort if sort else None,
        search_after=search_after if search_after else None,
    )
    await process_response(response)

    return format_response(response, response_format)
