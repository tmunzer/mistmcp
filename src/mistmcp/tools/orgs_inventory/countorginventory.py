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
from typing import Annotated
from uuid import UUID
from enum import Enum


class Type(Enum):
    AP = "ap"
    GATEWAY = "gateway"
    SWITCH = "switch"


class Distinct(Enum):
    MODEL = "model"
    STATUS = "status"
    SITE_ID = "site_id"
    SKU = "sku"
    VERSION = "version"


def add_tool() -> None:
    mcp.add_tool(
        fn=countOrgInventory,
        name="countOrgInventory",
        description="""Count by Distinct Attributes of in the Org Inventory""",
        tags={"Orgs Inventory"},
        annotations={
            "title": "countOrgInventory",
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True,
        },
    )


def remove_tool() -> None:
    mcp.remove_tool("countOrgInventory")


async def countOrgInventory(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    type: Type = Type.AP,
    distinct: Distinct = Distinct.MODEL,
    limit: Annotated[int, Field(default=100)] = 100,
) -> dict:
    """Count by Distinct Attributes of in the Org Inventory"""

    response = mistapi.api.v1.orgs.inventory.countOrgInventory(
        apisession,
        org_id=str(org_id),
        type=type.value,
        distinct=distinct.value,
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
