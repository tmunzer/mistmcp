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


class Type(Enum):
    AP = "ap"
    GATEWAY = "gateway"
    SWITCH = "switch"


@mcp.tool(
    name="listOrgAvailableDeviceVersions",
    description="""Get List of Available Device Versions""",
    tags={"Utilities Upgrade"},
    annotations={
        "title": "listOrgAvailableDeviceVersions",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def listOrgAvailableDeviceVersions(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    type: Optional[Type | None] = Type.AP,
    model: Annotated[
        Optional[str | None],
        Field(
            description="""Fetch version for device model, use/combine with `type` as needed (for switch and gateway devices)"""
        ),
    ] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """Get List of Available Device Versions"""

    logger.debug("Tool listOrgAvailableDeviceVersions called")

    apisession, response_format = get_apisession()
    data = {}

    response = mistapi.api.v1.orgs.devices.listOrgAvailableDeviceVersions(
        apisession,
        org_id=str(org_id),
        type=type.value if type else Type.AP.value,
        model=model if model else None,
    )
    await process_response(response)

    data = response.data

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
