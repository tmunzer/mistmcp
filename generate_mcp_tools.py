"""
This module generates Python tool files for interacting with Mist APIs based on an OpenAPI specification.
It processes a Mist OpenAPI specification to create a well-organized set of Python modules that provide
programmatic access to Mist's REST APIs through the Model Context Protocol (MCP) server.

Key Features:
- Parses OpenAPI specification to extract API endpoints and their details
- Generates Python classes and functions for API interaction
- Handles type conversions between OpenAPI and Python types
- Creates organized directory structure for tools by functionality
- Manages imports and dependencies automatically
- Generates proper parameter validation and type hints

Author: Thomas Munzer (tmunzer@juniper.net)
License: MIT License
"""
import os
import re
import shutil
import json
import yaml
from pathlib import Path
from typing import Dict, List

# Configuration Constants
OPENAPI_PATH = "mist.openapi.yaml"  # Path to the OpenAPI specification file
OUTPUT_DIR = Path("./src/mistmcp/tools")  # Directory where generated tool files will be placed
TOOLS_MODULE = "mistmcp.tools"  # Base module name for imports
INIT_FILE = Path("./src/mistmcp//tools/__init__.py")  # Path to package __init__ file
TOOLS_FILE = Path("./src/mistmcp/tools.json")  # File storing tool configuration
TOOLS_CONFIG_FILE = Path("./src/mistmcp/__ctools.py")  # File storing tool configuration

# List of API tags that should be excluded from tool generation
# These tags represent endpoints that are either deprecated, internal,
# or not relevant for general API usage
EXCLUDED_TAGS = [
        "Admins Login",
        "Admins Logout",
        "Admins Recover Password",
        "Admins Login - OAuth2",
        "Installer",
        "MSPs",
        "MSPs Admins",
        "Orgs SecIntel Profiles",
        "MSPs Inventory",
        "MSPs Logo",
        "MSPs Logs",
        "MSPs Licenses",
        "MSPs Marvis",
        "MSPs Org Groups",
        "MSPs Orgs",
        "MSPs SLEs",
        "MSPs SSO Roles",
        "MSPs SSO",
        "MSPs Tickets",
        "Orgs Admins",
        "Orgs API Tokens",
        "Orgs Assets",
        "Orgs Asset Filters",
        "Orgs Cert",
        "Orgs Clients - Marvis"
        "Orgs Marvis Invites",
        "Orgs Integration Cradlepoint",
        "Orgs CRL",
        "Orgs Integration Juniper",
        "Orgs Integration Zscaler",
        "Orgs SCEP",
        "Orgs Integration JSE",
        "Orgs JSI",
        "Orgs Linked Applications",
        "Orgs NAC IDP",
        "Orgs NAC Portals",
        "Orgs NAC CRL",
        "Orgs Premium Analytics",
        "Orgs Psk Portals",
        "Orgs SDK Invites",
        "Orgs SDK Templates",
        "Orgs SSO Roles",
        "Orgs SSO",
        "Orgs Tickets",
        "Orgs Vars",
        "Sites Asset Filters",
        "Sites Assets",
        "Sites Beacons",
        "Sites JSE",
        "Sites Licenses",
        "Sites Location",
        "Sites RSSI Zones",
        "Sites UI Settings",
        "Sites vBeacons",
        "Sites Zones",
        "Sites Stats - Assets",
        "Sites Stats - Beacons",
        "Sites Stats - Clients SDK",
        "Sites Stats - Zones",
        "Self API Token",
        "Self OAuth2",
        "Self MFA",
        "Samples Webhooks",
        "Utilities Common",
        "Utilities WAN",
        "Utilities LAN",
        "Utilities Wi-Fi",
        "Utilities PCAPs",
        "Utilities Location",
        "Utilities MxEdge",
        "Utilities Upgrade"
]
# Type translation mapping from OpenAPI types to Python types
# This dictionary maps OpenAPI type definitions to their Python equivalents
# Used during code generation to ensure correct parameter types in generated code
TRANSLATION = {
    "integer": "int",    # OpenAPI integer type maps to Python int
    "number": "float",   # OpenAPI number/float type maps to Python float
    "string": "str",     # OpenAPI string type maps to Python str
    "array": "list",     # OpenAPI array type maps to Python list
    "boolean": "bool",   # OpenAPI boolean type maps to Python bool
}

# Template for the tools configuration file
TOOLS_CONFIG_TEMPLATE="""\"\"\"
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
\"\"\"
import importlib.resources
import json
import asyncio
from enum import Enum
from pydantic import Field
from typing import Annotated, Optional
from fastmcp.server.dependencies import get_context
from mistmcp.__server import mcp
from . import tools

tools.self_account.getself.add_tool()

with importlib.resources.path("mistmcp", "tools.json") as json_path:
    with json_path.open() as json_file:
        TOOLS_AVAILABLE = json.load(json_file)

TOOL_REMOVE_FCT = {{}}

class McpToolsCategory(Enum):
{enums}


@mcp.tool(
    name="manageMcpTools",
    description="Used to reconfigure the MCP server and define a different list of tools based on the use case (monitor, troubleshooting, ...). IMPORTANT: This tool requires user confirmation after execution before proceeding with other actions.",
    tags={{"MCP Configuration"}},
    annotations={{
        "title": "manageMcpTools",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False 
    }}
)
async def manageMcpTools(
    enable_mcp_tools_categories:Annotated[list[McpToolsCategory], Field(description=\"\"\"Enable tools within the MCP based on the tool category\"\"\")] = [],
    disable_mcp_tools_categories:Annotated[list[McpToolsCategory], Field(description=\"\"\"Disable tools within the MCP based on the tool category\"\"\")] = [],
    configuration_required:Annotated[Optional[bool], Field(description=\"\"\"
This is to request the 'write' API endpoints, used to create or configure resources in the Mist Cloud. 
Do not use it except if it explicitly requested by the user, and ask the user confirmation before using any 'write' tool!
\"\"\", default=False
)]=False,
) -> str:
    \"\"\"Select the list of tools provided by the MCP server\"\"\"
    
    # Get the MCP server context
    ctx = get_context()
    tools_enabled = []
    tools_disabled = []

     # Disable requested tools based on categories
    for tool in disable_mcp_tools_categories:
        await ctx.info(f"{{tool.value}} -> Trying to unload the category tools")
        # Check if category exists in available tools
        if not TOOLS_AVAILABLE.get(tool.value):
            await ctx.warning(f"{{tool.value}} -> Unknown category")
            continue
            
        # Load each tool in the category
        for module_name in TOOLS_AVAILABLE[tool.value]["tools"]:
            import_name = f"mistmcp.tools.{{tool.value}}.{{module_name}}"
            await ctx.debug(f"{{tool.value}} -> Category available")
            await ctx.debug(f"{{tool.value}}.{{module_name}} -> Unloading the tool")
            try:
                # Import the module containing the tool
                module = importlib.import_module(f"mistmcp.tools.{{tool.value}}")
                await ctx.info(f"{{import_name}} -> module loaded")
                
                # Add the tool to MCP server
                getattr(module, module_name).remove_tool()
                await ctx.info(f"{{module_name}} -> \\"remove_tool()\\" function triggered")
                tools_disabled.append(module_name)
                
            except (ImportError, AttributeError) as e:
                # Handle errors during tool loading
                await ctx.error(f"{{import_name}} -> failed to load the tool: {{str(e)}}")
                continue
    
    # Enable requested tools based on categories
    for tool in enable_mcp_tools_categories:
        await ctx.info(f"{{tool.value}} -> Trying to load the category tools")
        # Check if category exists in available tools
        if not TOOLS_AVAILABLE.get(tool.value):
            await ctx.warning(f"{{tool.value}} -> Unknown category")
            continue
            
        # Load each tool in the category
        for module_name in TOOLS_AVAILABLE[tool.value]["tools"]:
            import_name = f"mistmcp.tools.{{tool.value}}.{{module_name}}"
            await ctx.debug(f"{{tool.value}} -> Category available")
            await ctx.debug(f"{{tool.value}}.{{module_name}} -> Loading the tool")
            try:
                # Import the module containing the tool
                module = importlib.import_module(f"mistmcp.tools.{{tool.value}}")
                await ctx.info(f"{{import_name}} -> module loaded")
                
                # Add the tool to MCP server
                getattr(module, module_name).add_tool()
                await ctx.info(f"{{module_name}} -> \\"add_tool()\\" function triggered")
                tools_enabled.append(module_name)
                
            except (ImportError, AttributeError) as e:
                # Handle errors during tool loading
                await ctx.error(f"{{import_name}} -> failed to load the tool: {{str(e)}}")
                continue

    # Add a small delay to ensure tools are registered with server
    await asyncio.sleep(.5)
    await ctx.session.send_tool_list_changed()
    await asyncio.sleep(.5)
    # Log final list of enabled tools
    message = f\"\"\"
🔧 MCP TOOLS CONFIGURATION COMPLETE 🔧

Tools enabled: {{', '.join(tools_enabled) if tools_enabled else 'None'}}
Tools disabled: {{', '.join(tools_disabled) if tools_disabled else 'None'}}

⚠️  IMPORTANT: STOP PROCESSING AND CONFIRM ⚠️

The MCP server tool configuration has been updated. Before proceeding with any further actions, please confirm that you want to continue with this new tool configuration.

Do you want to proceed? (yes/no)
\"\"\"
    await ctx.info(message)
    
    # Return a message that forces the agent to stop and ask for confirmation
    return f\"\"\"⚠️ STOP: USER CONFIRMATION REQUIRED ⚠️

{{message}}

This tool has completed its configuration. The agent MUST stop here and ask the user for explicit confirmation before proceeding with any other actions.

AGENT INSTRUCTION: Do not continue with any other tools or actions. Present this message to the user and wait for their explicit confirmation to proceed.\"\"\"

"""

# Template for the main __init__.py file
INIT_TEMPLATE="""\"\"\"
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
\"\"\"

{tools_import}
"""

# Template for individual tool files
TOOL_TEMPLATE = """"\"\"\"
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
\"\"\"
import json
import mistapi
from fastmcp.server.dependencies import get_context
from fastmcp.exceptions import ToolError
from mistmcp.__server import mcp
from mistmcp.__mistapi import apisession
{imports}

{models}
{enums}

def add_tool():
    mcp.add_tool(
        fn={operationId},
        name="{operationId}",
        description=\"\"\"{description}\"\"\",
        tags={{"{tag}"}},
        annotations={{
            "title": "{operationId}",
            "readOnlyHint": {readOnlyHint},
            "destructiveHint": {destructiveHint},
            "openWorldHint": True
        }}
    )

def remove_tool():
    mcp.remove_tool("{operationId}")

async def {operationId}({parameters}) -> dict:
    \"\"\"{description}\"\"\"

    response = {mistapi_request}
    
    
    ctx = get_context()
    
    if response.status_code != 200:
        error = {{
            "status_code": response.status_code,
            "message": ""
        }}
        if response.data:
            await ctx.error(f"Got HTTP{{response.status_code}} with details {{response.data}}")
            error["message"] =json.dumps(response.data)
        elif response.status_code == 400:
            await ctx.error(f"Got HTTP{{response.status_code}}")
            error["message"] =json.dumps("Bad Request. The API endpoint exists but its syntax/payload is incorrect, detail may be given")
        elif response.status_code == 401:
            await ctx.error(f"Got HTTP{{response.status_code}}")
            error["message"] =json.dumps("Unauthorized")
        elif response.status_code == 403:
            await ctx.error(f"Got HTTP{{response.status_code}}")
            error["message"] =json.dumps("Unauthorized")
        elif response.status_code == 401:
            await ctx.error(f"Got HTTP{{response.status_code}}")
            error["message"] =json.dumps("Permission Denied")
        elif response.status_code == 404:
            await ctx.error(f"Got HTTP{{response.status_code}}")
            error["message"] =json.dumps("Not found. The API endpoint doesn’t exist or resource doesn’t exist")
        elif response.status_code == 429:
            await ctx.error(f"Got HTTP{{response.status_code}}")
            error["message"] =json.dumps("Too Many Request. The API Token used for the request reached the 5000 API Calls per hour threshold")
        raise ToolError(error)
            
    return response.data
"""


def snake_case(s: str) -> str:
    """Convert a string to snake_case format."""
    return s.lower().replace(" ", "_").replace("-", "_")

def class_name_from_operation_id(operation_id: str) -> str:
    """Convert an operation ID to a proper class name in PascalCase."""
    return ''.join(word.capitalize() for word in operation_id.split('_'))

########
# Parameter Processing Functions

def _extract_param(data: dict):
    """Extract and normalize parameter information from OpenAPI spec."""
    tmp = {}
    if data:
        if data["schema"].get("$ref"):
            ref_name = data["schema"]["$ref"].split("/")[-1:][0]
            ref = openapi_schemas.get(ref_name)
            tmp = {
                "name": data["name"].replace(" ", "_").replace("-", "_"),
                "required": data.get("required", False),
                "format": ref.get("format", None),
                "enum": ref.get("enum", None),
                "type": ref.get("type"),
                "description": data.get("description"),
                "default": ref.get("default"),
                "minimum": ref.get("minimum"),
                "maximum": ref.get("maximum"),
                "minLength": ref.get("minLength"),
                "maxLength": ref.get("maxLength"),
            }
        else:
            tmp = {
                "name": data["name"].replace(" ", "_").replace("-", "_"),
                "required": data.get("required", False),
                "format": data["schema"].get("format", None),
                "enum": data["schema"].get("enum", None),
                "type": data["schema"].get("type"),
                "description": data.get("description"),
                "default": data["schema"].get("default"),
                "minimum": data["schema"].get("minimum"),
                "maximum": data["schema"].get("maximum"),
                "minLength": data["schema"].get("minLength"),
                "maxLength": data["schema"].get("maxLength"),
            }
    return tmp

def _add_import(imports:dict, package:str, module:str=""):
    """Add an import statement to the imports dictionary."""
    if not imports.get(package):
        if module:
            imports[package] = [module]
        else:
            imports[package] = None
    elif not module in imports[package]:
        imports[package].append(module)

def _process_params(endpoint_params: list, imports:dict, models:str, enums:str, parameters:str, mistapi_parameters:str, force_default:bool=False):
    """Process endpoint parameters and generate corresponding Python code."""
    for parameter in endpoint_params:
        if parameter.get("$ref"):
            ref_name = parameter["$ref"].split("/")[-1:][0]
            data = openapi_parameters.get(ref_name)
            tmp_param = _extract_param(data)
        else:
            tmp_param = _extract_param(parameter)

        tmp_type = TRANSLATION.get(tmp_param["type"])
        tmp_optional = ""
        tmp_default = ""
        tmp_mistapi_parameters = ""
        annotations = []

        if tmp_param["description"]:
            _add_import(imports, "pydantic", "Field")
            _add_import(imports, "typing", "Annotated")
            description = tmp_param["description"]
            r = r"\[.*\]\(\$e/.*/([^\)]*)\)"
            r_tmp = re.findall(r, description)
            if r_tmp:
                description = re.sub(r, f"`{r_tmp[0]}`", description)
            annotations.append(f"description=\"\"\"{description.replace('"', '\'').replace("\n", " ")}\"\"\"")
        elif tmp_param['name'].endswith("_id"):
            _add_import(imports, "pydantic", "Field")
            _add_import(imports, "typing", "Annotated")
            annotations.append(f"description=\"\"\"ID of the Mist {tmp_param['name'].replace('_id', '').capitalize()}\"\"\"")
        if tmp_param["minLength"]:
            _add_import(imports, "pydantic", "Field")
            _add_import(imports, "typing", "Annotated")
            annotations.append(f"min_length={tmp_param['minLength']}")
        if tmp_param["maxLength"]:
            _add_import(imports, "pydantic", "Field")
            _add_import(imports, "typing", "Annotated")
            annotations.append(f"max_length={tmp_param['maxLength']}")
        if tmp_param["minimum"]:
            _add_import(imports, "pydantic", "Field")
            _add_import(imports, "typing", "Annotated")
            annotations.append(f"ge={tmp_param['minimum']}")
        if tmp_param["maximum"]:
            _add_import(imports, "pydantic", "Field")
            _add_import(imports, "typing", "Annotated")
            annotations.append(f"le={tmp_param['maximum']}")

        if tmp_param["type"]=="string":

            if tmp_param["format"] == "uuid":
                _add_import(imports, "uuid", "UUID")
                tmp_type = "UUID"
                tmp_mistapi_parameters = f"            {tmp_param['name']}=str({tmp_param['name']}),\n"

            elif tmp_param["enum"]:
                _add_import(imports, "enum", "Enum")
                tmp_enum = f"\nclass {tmp_param['name'].capitalize()}(Enum):\n"
                tmp_choices = []
                for e in tmp_param["enum"]:
                    tmp_choices.append(e.lower())
                    e_tmp = snake_case(e)
                    if e_tmp in ["24", "5", "6"]:
                        e_tmp = f"B{e_tmp}"
                    tmp_enum += f"    {e_tmp.upper()} = \"{e}\"\n"
                if (
                    not tmp_param["required"]
                    and not tmp_param["default"]
                    and not "none" in tmp_choices
                    and force_default):
                    tmp_enum += "    NONE = None\n"
                enums+=tmp_enum
                tmp_type = tmp_param['name'].capitalize()
                if tmp_param["default"]:
                    tmp_default = f" = {tmp_param['name'].capitalize()}.{tmp_param['default'].upper()}"
                elif force_default:
                    tmp_default = f" = {tmp_param['name'].capitalize()}.NONE"
                tmp_mistapi_parameters = f"            {tmp_param['name']}={tmp_param['name']}.value,\n"


        if not tmp_default:
            if tmp_param["required"]:
                tmp_optional = ""
            elif tmp_param["default"]:
                tmp_optional = ""
                if tmp_param["type"]=="string":
                    tmp_default = f" = \"{tmp_param["default"]}\""
                    annotations.append(f"default=\"{tmp_param['default']}\"")
                else:
                    tmp_default = f" = {tmp_param["default"]}"
                    annotations.append(f"default={tmp_param['default']}")
            else:
                _add_import(imports, "typing", "Optional")
                tmp_type = f"Optional[{tmp_type}]"
                tmp_optional = " | None"
                tmp_default = " = None"

        if annotations:
            _add_import(imports, "typing", "Annotated")
            _add_import(imports, "pydantic", "Field")
            tmp_type = f"Annotated[{tmp_type}, Field({','.join(annotations)})]"


        if not tmp_mistapi_parameters:
            tmp_mistapi_parameters = f"            {tmp_param['name']}={tmp_param['name']},\n"

        parameters += f"    {tmp_param['name']}: {tmp_type}{tmp_optional}{tmp_default},\n"
        mistapi_parameters += tmp_mistapi_parameters
    return imports, models, enums, parameters, mistapi_parameters

def gen_endpoint_parameters(path_parameters:list, endpoint:dict):
    """Generate complete parameter definitions for an endpoint."""
    imports = ""
    models = ""
    enums = ""
    parameters = ""
    mistapi_parameters = ""
    tmp_imports = {}
    tmp_imports, models, enums, parameters, mistapi_parameters = _process_params(path_parameters, tmp_imports, models, enums, parameters, mistapi_parameters, False)
    tmp_imports, models, enums, parameters, mistapi_parameters =_process_params(endpoint.get("parameters", []), tmp_imports, models, enums, parameters, mistapi_parameters, True)
    for package, modules in tmp_imports.items():
        if modules:
            imports += f"from {package} import {', '.join(modules)}\n"
        else:
            imports += f"import {package}\n"
    if parameters:
        parameters = f"\n{parameters}"
    return  imports, models, enums, parameters, mistapi_parameters

def _gen_folder_and_file_paths(endpoint: str):
    """Generate appropriate folder and file paths for an endpoint."""
    endpoint_path = endpoint.split("/")
    # remove vars from endpoint path
    tmp = []
    installer = False
    for part in endpoint_path:
        if part == "installer":
            installer = True
        if part != "" and not part.startswith("{"):
            tmp.append(part)
    endpoint_path = tmp

    if installer and len(endpoint_path) > 4:
        folder_path_parts = endpoint_path[0:4]
        file_name = endpoint_path[4:5][0]
    elif len(endpoint_path) > 3:
        folder_path_parts = endpoint_path[0:3]
        file_name = endpoint_path[3:4][0]
    else:
        folder_path_parts = endpoint_path[0:3]
        file_name = endpoint_path[2:3][0]

    if file_name == "128routers":
        file_name = "ssr"
    return folder_path_parts, file_name

def _get_tag_defs()->dict:
    defs = {}
    for tag in openapi_tags:
        if tag.get("name") not in EXCLUDED_TAGS:
            defs[snake_case(tag.get("name")).lower()]={"tools":[], "description":tag.get("description")}
    return defs

def _gen_tools_init(tools_import:dict):
    """Generate import statements for the __init__.py file."""
    tmp =[]
    for tag, modules in tools_import.items():
        #tmp.append(f"from {TOOLS_MODULE}.{tag} import {", ".join(modules)}")
        tmp.append(f"from .{tag} import {", ".join(modules)}")
        #tmp.append(f"from .{tag} import *")
    return "\n".join(tmp)

def main():
    """Main function to process the OpenAPI spec and generate tool files.
    
    This function:
    1. Processes each path in the OpenAPI specification
    2. Generates appropriate Python code for each endpoint
    3. Creates organized directory structure for tools
    4. Generates necessary files with proper imports and configurations
    """
    tag_to_tools: Dict[str, List[str]] = {}
    root_tag_defs = _get_tag_defs()
    root_tools_import={}
    root_enums=[]
    root_functions={}

    for path, methods in openapi_paths.items():
        for method, details in methods.items():
            if method.lower() == "get":
                readOnlyHint = True
                destructiveHint = False
            elif method.lower() == "delete":
                destructiveHint = True
                readOnlyHint = False
                continue
            elif method.lower() in ["post", "put"]:
                destructiveHint = True
                readOnlyHint = False
                continue
            else:
                continue

            tags = details.get("tags", ["Untagged"])
            if len(tags)>0 and tags[0] in EXCLUDED_TAGS:
                continue

            operation_id = details.get("operationId") or snake_case(path.strip("/").replace("/", "_"))
            description = details.get("description", "")

            imports = ""
            models = ""
            enums = ""
            parameters = ""
            mistapi_parameters = ""

            imports, models, enums, parameters, mistapi_parameters = gen_endpoint_parameters(methods.get("parameters", []), details)

            folder_path_parts, file_name = _gen_folder_and_file_paths(path)
            mistapi_request = f"""mistapi.{'.'.join(folder_path_parts)}.{file_name}.{operation_id}(
            apisession,
{mistapi_parameters}    )"""

            tool_code = TOOL_TEMPLATE.format(
                imports=imports,
                models=models,
                enums=enums,
                operationId=operation_id,
                description=description.replace('\n', ''),
                tag=tags[0],
                readOnlyHint=readOnlyHint,
                destructiveHint=destructiveHint,
                parameters=parameters,
                mistapi_request=mistapi_request
            )

            for tag in tags:
                tag_dir = OUTPUT_DIR / snake_case(tag)
                tag_dir.mkdir(parents=True, exist_ok=True)
                init_file = tag_dir / "__init__.py"
                init_file.write_text("")
                tool_file = tag_dir / f"{snake_case(operation_id)}.py"
                tool_file.write_text(tool_code)
                tag_to_tools.setdefault(tag, []).append(str(tool_file))

                ## tool_tools_import
                if not root_tools_import.get(snake_case(tag)):
                    root_tools_import[snake_case(tag)] = []
                root_tools_import[snake_case(tag)].append(snake_case(operation_id))
                ## root_enums
                if f"    {snake_case(tag).upper()} = \"{snake_case(tag).lower()}\"" not in root_enums:
                    root_enums.append(f"    {snake_case(tag).upper()} = \"{snake_case(tag).lower()}\"")
                ## root_functions
                if not root_functions.get(snake_case(snake_case(tag))):
                    root_functions[snake_case(snake_case(tag))] = []                
                root_functions[snake_case(snake_case(tag))].append(f"{snake_case(operation_id)}.add_tool()")
                root_functions[snake_case(snake_case(tag))].append(f"TOOL_REMOVE_FCT.append({snake_case(operation_id)}.remove_tool)")
                ## root_tag_defs
                root_tag_defs[snake_case(snake_case(tag))]["tools"].append(snake_case(operation_id))

    print("Generated tools grouped by tag:")
    for tag, files in tag_to_tools.items():
        print(f"{tag}:")
        for f in files:
            print(f"  - {f}")

    print("Generated tools grouped by tag:")
    for tag, files in tag_to_tools.items():
        print(f"{snake_case(tag).upper()} = \"{snake_case(tag).lower()}\"")

    with open(INIT_FILE, "w") as f:
        f.write(INIT_TEMPLATE.format(tools_import= _gen_tools_init(root_tools_import)))

    with open(TOOLS_FILE, "w") as f:
        json.dump(root_tag_defs, f)
        
    
    with open(TOOLS_CONFIG_FILE, "w") as f:
        f.write(TOOLS_CONFIG_TEMPLATE.format(
                enums="\n".join(root_enums),
                root_tag_defs=json.dumps(root_tag_defs)
            ))
    
if __name__ == "__main__":
    # Clean up existing tools directory
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    
    # Load and parse the OpenAPI specification
    with open(OPENAPI_PATH, "r") as f:
        openapi_json = yaml.safe_load(f)
    openapi_paths = openapi_json.get("paths")
    openapi_tags = openapi_json.get("tags")
    openapi_parameters = openapi_json.get("components", {}).get("parameters")
    openapi_schemas = openapi_json.get("components", {}).get("schemas")
    
    main()