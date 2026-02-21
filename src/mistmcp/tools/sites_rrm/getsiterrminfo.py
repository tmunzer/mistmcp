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
from enum import Enum
from uuid import UUID


class Rrm_info_type(Enum):
    CURRENT_CHANNEL_PLANNING = "current_channel_planning"
    CURRENT_RRM_CONSIDERATIONS = "current_rrm_considerations"
    CURRENT_RRM_NEIGHBORS = "current_rrm_neighbors"


class Band(Enum):
    B24 = "24"
    B5 = "5"
    B6 = "6"


@mcp.tool(
    name="getSiteRrmInfo",
    description="""This tool can be used to retrieve information the site RRM (Radio Resource Management) status""",
    tags={"sites_rrm"},
    annotations={
        "title": "getSiteRrmInfo",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getSiteRrmInfo(
    rrm_info_type: Annotated[
        Rrm_info_type,
        Field(
            description="""Type of information to retrieve about the current user and account. Possible values are `account_info`, `api_usage`, and `login_failures`"""
        ),
    ],
    site_id: Annotated[UUID, Field(description="""Site ID""")],
    device_id: Annotated[
        Optional[UUID | None],
        Field(
            description="""ID of the device to retrieve RRM information for. Required when `rrm_info_type` is `current_rrm_considerations`"""
        ),
    ] = None,
    band: Annotated[
        Optional[Band | None],
        Field(
            description="""802.11 Band to retrieve RRM information for. Required when `rrm_info_type` is `current_rrm_considerations` or `current_rrm_neighbors`"""
        ),
    ] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """This tool can be used to retrieve information the site RRM (Radio Resource Management) status"""

    logger.debug("Tool getSiteRrmInfo called")

    apisession, response_format = get_apisession()

    object_type = rrm_info_type

    if object_type.value == "current_rrm_considerations":
        if not device_id:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`device_id` parameter is required when `object_type` is "current_rrm_considerations".',
                }
            )

    if object_type.value == "current_rrm_considerations":
        if not band:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`band` parameter is required when `object_type` is "current_rrm_considerations".',
                }
            )

    if object_type.value == "current_rrm_neighbors":
        if not band:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": '`band` parameter is required when `object_type` is "current_rrm_neighbors".',
                }
            )

    match object_type.value:
        case "current_channel_planning":
            response = mistapi.api.v1.sites.rrm.getSiteCurrentChannelPlanning(
                apisession, site_id=str(site_id)
            )
            await process_response(response)
        case "current_rrm_considerations":
            response = mistapi.api.v1.sites.rrm.getSiteCurrentRrmConsiderations(
                apisession,
                site_id=str(site_id),
                device_id=str(device_id),
                band=str(band),
            )
            await process_response(response)
        case "current_rrm_neighbors":
            response = mistapi.api.v1.sites.rrm.listSiteCurrentRrmNeighbors(
                apisession, site_id=str(site_id), band=str(band)
            )
            await process_response(response)

        case _:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Rrm_info_type]}",
                }
            )

    return format_response(response, response_format)
