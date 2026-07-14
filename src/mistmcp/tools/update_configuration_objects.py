"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

from enum import Enum
from typing import Annotated
from uuid import UUID

from fastmcp import Context
from pydantic import Field

from mistmcp.server import mcp
from mistmcp.tools.change_configuration_objects import (
    Action_type as ChangeActionType,
)
from mistmcp.tools.change_configuration_objects import (
    Object_type,
    change_configuration_objects,
)


class Action_type(Enum):
    CREATE = "create"
    UPDATE = "update"


@mcp.tool(
    name="mist_update_configuration_objects",
    description="""Update or create configuration object for a specified org or site.

IMPORTANT:
When updating an existing object:
1. Retrieve the current object with `mist_get_configuration(operation=objects, ...)`
2. Modify the desired attributes
3. Submit only the attributes that need to be created or updated

It is not required to send all root attributes in the request payload. Root attributes omitted from the payload are not removed from Mist; Mist replaces the values of the root attributes included in the payload with the values sent.

When creating a new configuration object, make sure to call `mist_describe(subject=configuration_schema)` to list schemas, then retrieve the matching schema to discover supported and required attributes.

When deleting an org WLAN template (`org_wlantemplates`), make sure to delete all WLANs that are using the template before deleting it, otherwise the deletion will fail
When creating a WLAN, make sure to set the `template_id` attribute in the payload to the ID of an existing WLAN Template. If needed, create a new WLAN Template using this tool before creating the WLAN and use the ID of the newly created template in the WLAN payload

NOTE:
- To remove a root attribute, include it in the payload with the same name prefixed by "-" and an empty string value. Example: {"-dhcpd_config": ""} removes the root attribute "dhcpd_config".

WARNING:
- when updating a nested object or list, the entire nested object or list will be replaced with the new value provided in the payload. This means that any existing values not included in the payload will be removed. To avoid accidental data loss, it is recommended to first retrieve the current configuration object using `mist_get_configuration(operation=objects, ...)` and use the retrieved object as a base for the payload, modifying only the desired attributes.
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
    action_type: Annotated[
        Action_type,
        Field(
            description="Whether the action is creating a new object, updating an existing one, or deleting an existing one. When updating or deleting, the object_id parameter must be provided."
        ),
    ],
    object_type: Annotated[
        Object_type,
        Field(description="Type of configuration object to create or update"),
    ],
    payload: Annotated[
        dict,
        Field(
            description="JSON payload of the configuration object to create or update. When updating an existing object, include the attributes to create or update; root attributes omitted from the payload are not removed from Mist. To remove a root attribute, include it in the payload with the same name prefixed by '-' and an empty string value; for example, {'-dhcpd_config': ''} removes the root attribute 'dhcpd_config'. It is recommended to first retrieve the current configuration object using `mist_get_configuration(operation=objects, ...)` and use the retrieved object as a base for the payload, modifying only the desired attributes"
            "",
        ),
    ],
    org_id: Annotated[
        UUID,
        Field(
            description="""Organization ID. Required when object_type starts with 'org_'""",
            default=None,
        ),
    ],
    site_id: Annotated[
        UUID,
        Field(
            description="""Site ID. Required when object_type starts with 'site_'""",
            default=None,
        ),
    ],
    object_id: Annotated[
        UUID,
        Field(
            description="""ID of the specific configuration object to update. Required when action_type is 'update'""",
            default=None,
        ),
    ],
    ctx: Context,
) -> dict | list | str:
    """Update an existing configuration object or create a new one."""

    new_action_type = (
        ChangeActionType.UPDATE
        if action_type == Action_type.UPDATE
        else ChangeActionType.CREATE
    )
    return await change_configuration_objects(
        action_type=new_action_type,
        object_type=object_type,
        payload=payload,
        org_id=org_id,
        site_id=site_id,
        object_id=object_id,
        ctx=ctx,
    )
