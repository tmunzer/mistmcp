# Template for individual tool files
TOOL_TEMPLATE_WRITE = '''"""
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

from mistmcp.elicitation_processor import config_elicitation_handler
from mistmcp.server import mcp

{imports}
{models}
{enums}


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
    {parameters}    ctx: Context|None = None,
    ) -> dict | list | str:
    \"\"\"{description}\"\"\"


    apisession, response_format = get_apisession()
    data = {{}}
    
    action_wording = "create a new"
    if object_id:
        action_wording = "update an existing"
    
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

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
'''

TOOL_TEMPLATE_WRITE_ELICITATION = '''
                try:
                    elicitation_response = await config_elicitation_handler(
                    message=f"""Do you accept to trigger the updateOrgConfigurationObjects API call""",
                    context=get_context(),
                )
                except Exception as exc:
                    raise ToolError(
                        {
                            "status_code": 400,
                            "message": (
                                "AI App does not support elicitation. You cannot use it to "
                                "modify configuration objects. Please use the Mist API "
                                "directly or use an AI App with elicitation support to "
                                "modify configuration objects."
                            ),
                        }
                    ) from exc

                if elicitation_response.action == "accept":
                    {request}
                elif elicitation_response.action == "decline":
                    return {"message": "Action declined by user."}
                elif elicitation_response.action == "cancel":
                    return {"message": "Action canceled by user."}
'''
