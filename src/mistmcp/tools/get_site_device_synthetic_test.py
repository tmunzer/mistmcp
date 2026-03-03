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
from typing import Annotated
from uuid import UUID


@mcp.tool(
    name="mist_get_site_device_synthetic_test",
    description="""Get Device Synthetic Test""",
    tags={"marvis"},
    annotations={
        "title": "Get site device synthetic test",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def get_site_device_synthetic_test(
    site_id: Annotated[UUID, Field(description="""Site ID""")],
    device_id: Annotated[UUID, Field(description="""ID of the Mist Device""")],
    ctx: Context | None = None,
) -> dict | list | str:
    """Get Device Synthetic Test"""

    logger.debug("Tool get_site_device_synthetic_test called")

    apisession, response_format = get_apisession()

    response = mistapi.api.v1.sites.devices.getSiteDeviceSyntheticTest(
        apisession,
        site_id=str(site_id),
        device_id=str(device_id),
    )
    await process_response(response)

    return format_response(response, response_format)
