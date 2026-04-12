"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

from typing import Annotated
from uuid import UUID

from fastmcp import Context
from pydantic import Field

from mistmcp.server import mcp
from mistmcp.tools.change_configuration_objects import (
    Action_type as ChangeActionType,
    Object_type,
    change_configuration_objects,
)


@mcp.tool(
    name="mist_update_configuration_objects",
    description="""Update or create configuration object for a specified org or site.

IMPORTANT:
To ensure that you are not missing existing attributes when updating an object:
1. Retrieve the current object with `mist_get_configuration_objects`
2. Modify the desired attributes
3. Submit the full payload with this tool

When creating a new configuration object, use `mist_get_configuration_object_schema`
to discover required fields and valid structure.
""",
    tags={"write"},
    annotations={
        "title": "Update configuration objects",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def update_configuration_objects(
    object_type: Annotated[
        Object_type,
        Field(description="Type of configuration object to create or update"),
    ],
    payload: Annotated[
        dict,
        Field(
            description="JSON payload of the configuration object to create or update"
        ),
    ],
    org_id: Annotated[UUID, Field(description="Organization ID", default=None)],
    site_id: Annotated[UUID, Field(description="Site ID", default=None)],
    object_id: Annotated[
        UUID,
        Field(
            description=(
                "ID of the specific configuration object to update. "
                "If omitted, a new object is created."
            ),
            default=None,
        ),
    ],
    ctx: Context,
) -> dict | list | str:
    """Update an existing configuration object or create a new one."""

    action_type = ChangeActionType.UPDATE if object_id else ChangeActionType.CREATE
    return await change_configuration_objects(
        action_type=action_type,
        object_type=object_type,
        payload=payload,
        org_id=org_id,
        site_id=site_id,
        object_id=object_id,
        ctx=ctx,
    )
