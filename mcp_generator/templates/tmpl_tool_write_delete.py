# Template for individual tool files
TOOL_TEMPLATE_WRITE_DELETE = '''"""
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

from mistmcp.elicitation_processor import config_elicitation_handler
from mistmcp.server import mcp
from mistmcp.logger import logger

{imports}
{models}
{enums}

class Action_type(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"

@mcp.tool(
    name = "{operationId}",
    description = """{description}""",
    tags = {{"{tag}"}},
    annotations = {{
        "title": "{operationId}",
        "readOnlyHint": {readOnlyHint},
        "destructiveHint": {destructiveHint},
        "openWorldHint": True,
    }},
)
async def {operationId}(
    action_type: Annotated[Action_type, Field(description="Whether the action is creating a new object, updating an existing one, or deleting an existing one. When updating or deleting, the object_id parameter must be provided.")],
    {parameters}    ctx: Context|None = None,
    ) -> dict | list | str:
    \"\"\"{description}\"\"\"

    logger.debug("Tool {operationId} called")

    apisession, response_format = get_apisession()
    
    action_wording = "create a new"
    if action_type == Action_type.UPDATE:
        if not object_id:
            raise ToolError(
                {{
                    "status_code": 400,
                    "message": "object_id parameter is required when action_type is 'update'."
                }}
            )  
        action_wording = "update an existing"
    elif action_type == Action_type.DELETE:
        if not object_id:
            raise ToolError(
                {{
                    "status_code": 400,
                    "message": "object_id parameter is required when action_type is 'delete'."
                }}
            )
        action_wording = "delete an existing"
    
    if ctx:
        try:
            elicitation_response = await config_elicitation_handler(
                message=f"""The LLM wants to {{action_wording}} {{object_type.value}}. Do you accept to trigger the API call?""",
                ctx=ctx,
            )
        except Exception as exc:
            raise ToolError(
                {{
                    "status_code": 400,
                    "message": (
                        "AI App does not support elicitation. You cannot use it to "
                        "modify configuration objects. Please use the Mist API "
                        "directly or use an AI App with elicitation support to "
                        "modify configuration objects."
                    ),
                }}
            ) from exc
        
        
        if elicitation_response.action == "decline":
            return {{"message": "Action declined by user."}}
        elif elicitation_response.action == "cancel":
            return {{"message": "Action canceled by user."}}

    {request}

    return format_response(response, response_format)
'''
