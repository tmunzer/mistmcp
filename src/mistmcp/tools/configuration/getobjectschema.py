"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

from enum import Enum
from typing import Annotated, Any

from pydantic import Field

from mistmcp.server import get_mcp
from mistmcp.tools.configuration import schemas_data as _schemas_data_module

mcp = get_mcp()

if not mcp:
    raise RuntimeError(
        "MCP instance not found. Make sure to initialize the MCP server before defining tools."
    )

# Pre-resolved schemas keyed by schema_name (= schemas_config.yaml entry key).
# Each entry: {"schema": <dict>, "_schema_name": <oas_schema_name>}
_SCHEMAS_DATA: dict = _schemas_data_module.SCHEMAS_DATA

# Enum of available schema names, built at import time from the pre-resolved data keys.
SchemaName = Enum("SchemaName", {name: name for name in _SCHEMAS_DATA})  # type: ignore[misc]


@mcp.tool(
    enabled=True,
    name="getObjectSchema",
    description="""Retrieve the JSON schema for a Mist configuration object type.
The schema is derived from the Mist OpenAPI specification and includes all properties with their types, descriptions, defaults, and constraints.
Use this tool to understand the structure of a configuration object before creating or updating it.""",
    tags={"configuration"},
    annotations={
        "title": "getObjectSchema",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": False,
    },
)
async def getObjectSchema(
    schema_name: Annotated[
        SchemaName,
        Field(description="Name of the configuration object schema to retrieve."),
    ],
) -> dict[str, Any]:
    """Retrieve the pre-resolved JSON schema for a Mist configuration object."""

    entry = _SCHEMAS_DATA.get(schema_name.value)
    if entry is None:
        raise ValueError(
            f"Schema '{schema_name.value}' not found. "
            "Re-run the generator to rebuild schemas_data.py."
        )

    resolved: dict = dict(entry["schema"])  # shallow copy — safe to annotate

    if not resolved:
        raise ValueError(
            f"No schema found for '{schema_name.value}'. "
            "Re-run the generator to rebuild schemas_data.py."
        )

    resolved["x-schema-name"] = entry["_schema_name"]
    return resolved
