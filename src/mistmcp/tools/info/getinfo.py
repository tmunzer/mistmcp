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
from enum import Enum
from uuid import UUID


class Info_type(Enum):
    ORG = "org"
    SITE = "site"


@mcp.tool(
    name="getInfo",
    description="""This tool can be used to search information about the organizations or sites.""",
    tags={"info"},
    annotations={
        "title": "getInfo",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getInfo(
    info_type: Annotated[
        Info_type,
        Field(
            description="""Type of information to search for. Possible values are `org` and `site`."""
        ),
    ],
    org_id: Annotated[
        UUID,
        Field(description="""ID of the organization to search for information in."""),
    ],
    site_id: Annotated[
        Optional[UUID | None],
        Field(
            description="""ID of the site to search for information in. Optional when `info_type` is `site`. If not specified, the search will include all sites in the organization."""
        ),
    ] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """This tool can be used to search information about the organizations or sites."""

    logger.debug("Tool getInfo called")

    apisession, response_format = get_apisession()
    data = {}

    object_type = info_type
    match object_type.value:
        case "org":
            response = mistapi.api.v1.orgs.orgs.getOrg(apisession, org_id=str(org_id))
            await process_response(response)
            data = response.data
        case "site":
            if site_id:
                response = mistapi.api.v1.sites.sites.getSiteInfo(
                    apisession, site_id=str(site_id)
                )
                await process_response(response)
                data = response.data
            else:
                response = mistapi.api.v1.orgs.sites.listOrgSites(
                    apisession, org_id=str(org_id)
                )
                await process_response(response)
                data = response.data

        case _:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Info_type]}",
                }
            )

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
