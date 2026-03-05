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
from typing import Annotated, List
from uuid import UUID


@mcp.tool(
    name="mist_search_nac_user_macs",
    description="""Search for NAC user MAC addresses in an organization or site, with optional filters for associated SSID and time range. User MACs are used to perform MAC Authentication with Juniper Mist NAC.""",
    tags={"orgs_nac"},
    annotations={
        "title": "Search nac user macs",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def search_nac_user_macs(
    org_id: Annotated[UUID, Field(description="""Organization ID""")],
    usermac_id: Annotated[
        str,
        Field(
            description="""ID of the User MAC address to return details for. If specified, other filters are ignored and details for the specified User MAC address is returned if it exists""",
            default=None,
        ),
    ],
    mac: Annotated[
        str,
        Field(
            description="""Partial/full MAC address of the NAC endpoint to search for""",
            default=None,
        ),
    ],
    labels: Annotated[
        List[str],
        Field(
            description="""Comma separated list of labels to filter NAC endpoints by. A NAC endpoint must have all the specified labels to be included in the results""",
            default=None,
        ),
    ],
    limit: Annotated[
        int, Field(description="""Max number of results per page""", default=20)
    ] = 20,
) -> dict | list | str:
    """Search for NAC user MAC addresses in an organization or site, with optional filters for associated SSID and time range. User MACs are used to perform MAC Authentication with Juniper Mist NAC."""

    logger.debug("Tool search_nac_user_macs called")

    apisession, response_format = await get_apisession()

    try:
        if usermac_id:
            response = mistapi.api.v1.orgs.usermacs.getOrgUserMac(
                apisession, org_id=str(org_id), usermac_id=str(usermac_id)
            )
            await process_response(response)
        else:
            response = mistapi.api.v1.orgs.usermacs.searchOrgUserMacs(
                apisession,
                org_id=str(org_id),
                mac=str(mac) if mac else None,
                labels=labels if labels else None,
                limit=limit,
            )
            await process_response(response)
    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
