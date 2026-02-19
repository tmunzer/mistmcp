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
from mistmcp.server import mcp
from mistmcp.logger import logger

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


class Channel(Enum):
    ALPHA = "alpha"
    BETA = "beta"
    STABLE = "stable"


@mcp.tool(
    name="listOrgAvailableSsrVersions",
    description="""Get available version for SSR""",
    tags={"Utilities Upgrade"},
    annotations={
        "title": "listOrgAvailableSsrVersions",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def listOrgAvailableSsrVersions(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    channel: Annotated[
        Optional[Channel | None], Field(description="""SSR version channel""")
    ] = Channel.STABLE,
    mac: Annotated[
        Optional[str | None],
        Field(
            description="""Optional. MAC address, or comma separated MAC address list."""
        ),
    ] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """Get available version for SSR"""

    logger.debug("Tool listOrgAvailableSsrVersions called")

    apisession, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.orgs.ssr.listOrgAvailableSsrVersions(
        apisession,
        org_id=str(org_id),
        channel=channel.value if channel else Channel.STABLE.value,
        mac=mac if mac else None,
    )
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
