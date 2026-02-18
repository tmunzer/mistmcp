"""
This module generates Python tool files for the Mist MCP (Model Context Protocol) server based on the Mist OpenAPI specification.
It creates a structured set of Python modules that provide programmatic access to Mist's REST APIs with proper validation and error handling.

Key Features:
- Processes Mist OpenAPI specification to generate MCP-compatible tools
- Creates organized directory structure by API categories
- Generates proper parameter validation with Pydantic
- Handles type conversions between OpenAPI and Python types
- Provides comprehensive error handling for API responses
- Manages tool registration and configuration
- Excludes deprecated or internal API endpoints
- Generates configuration files for dynamic tool management

The generated tools support:
- Proper type hints and validation
- Automatic error handling and logging
- Dynamic tool registration/unregistration
- Category-based tool organization
- User confirmation for destructive operations

Author: Thomas Munzer (tmunzer@juniper.net)
License: MIT License
"""

import argparse
import json
import os
import re
import shutil
from pathlib import Path
from typing import Dict, List

import yaml
from templates.tmpl_device_configuration import DEVICE_CONFIGURATION_TEMPLATE
from templates.tmpl_get_object_schema import GET_OBJECT_SCHEMA_TEMPLATE
from templates.tmpl_helper import TOOLS_HELPER
from templates.tmpl_init import INIT_TEMPLATE
from templates.tmpl_req import REQ_OPTIMIZED_TEMPLATE, REQ_TEMPLATE
from templates.tmpl_site_configuration import SITE_CONFIGURATION_TEMPLATE
from templates.tmpl_tool_read import TOOL_TEMPLATE_READ
from templates.tmpl_tool_write import TOOL_TEMPLATE_WRITE

# Configuration Constants
FILE_PATH = os.path.realpath(__file__)
DIR_PATH = os.path.dirname(FILE_PATH)
OPENAPI_PATH = (
    os.path.join(
        DIR_PATH, "../mist_openapi/mist.openapi.yaml"
    )  # Path to the OpenAPI specification file
)
SCHEMAS_CONFIG_PATH = Path(os.path.join(DIR_PATH, "schemas_config.yaml"))
SCHEMAS_DATA_OUTPUT_PATH = Path(
    os.path.join(
        DIR_PATH, "../src/mistmcp/tools/configuration/schemas_data.py")
)
CUSTOM_TOOLS = [
    {
        "name": "getSiteConfiguration",
        "template": SITE_CONFIGURATION_TEMPLATE,
        "tag": "configuration",
    },
    {
        "name": "getDeviceConfiguration",
        "template": DEVICE_CONFIGURATION_TEMPLATE,
        "tag": "configuration",
    },
    {
        "name": "getObjectSchema",
        "template": GET_OBJECT_SCHEMA_TEMPLATE,
        "tag": "configuration",
    },
]
READ_ONLY_HINT = True

OUTPUT_DIR = Path(os.path.join(DIR_PATH, "../src/mistmcp/tools"))

OUTPUT_DIR = Path(
    os.path.join(DIR_PATH, "../src/mistmcp/tools")
)  # Directory where generated tool files will be placed
TOOLS_MODULE = "mistmcp.tools"  # Base module name for imports
INIT_FILE = Path(
    os.path.join(
        DIR_PATH, "../src/mistmcp/tools/__init__.py"
    )  # Path to package __init__ file
)
# TOOLS_FILE = Path("../src/mistmcp/tools.json")  # File storing tool configuration
TOOLS_HELPER_FILE = Path(
    # Helper file for tools
    os.path.join(DIR_PATH, "../src/mistmcp/tool_helper.py")
)
# List of API tags that should be excluded from tool generation
# These tags represent endpoints that are either deprecated, internal,
# or not relevant for general API usage

with open(os.path.join(DIR_PATH, "excluded_tags.yaml"), "r", encoding="utf-8") as f:
    EXCLUDED_TAGS = yaml.safe_load(f)

with open(os.path.join(DIR_PATH, "excluded_operation_ids.yaml"), "r", encoding="utf-8"
          ) as f:
    EXCLUDED_OPERATION_IDS = yaml.safe_load(f)

with open(os.path.join(DIR_PATH, "custom_tags_def.yaml"), "r", encoding="utf-8") as f:
    CUSTOM_TAGS_DEFS = yaml.safe_load(f)

with open(os.path.join(DIR_PATH, "custom_tags.yaml"), "r", encoding="utf-8") as f:
    CUSTOM_TAGS = yaml.safe_load(f)

with open(
    os.path.join(DIR_PATH, "tools_optimization.yaml"), "r", encoding="utf-8"
) as f:
    OPTIMIZED_TOOLS = yaml.safe_load(f)
    if not OPTIMIZED_TOOLS:
        OPTIMIZED_TOOLS = {}

# Type translation mapping from OpenAPI types to Python types
# This dictionary maps OpenAPI type definitions to their Python equivalents
# Used during code generation to ensure correct parameter types in generated code
TRANSLATION = {
    "integer": "int",  # OpenAPI integer type maps to Python int
    "number": "float",  # OpenAPI number/float type maps to Python float
    "string": "str",  # OpenAPI string type maps to Python str
    "array": "list",  # OpenAPI array type maps to Python list
    "boolean": "bool",  # OpenAPI boolean type maps to Python bool
    "object": "dict",  # OpenAPI object type maps to Python dict
}


def snake_case(s: str) -> str:
    """Convert a string to snake_case format."""
    return s.lower().replace(" ", "_").replace("-", "_")


def class_name_from_operation_id(operation_id: str) -> str:
    """Convert an operation ID to a proper class name in PascalCase."""
    return "".join(word.capitalize() for word in operation_id.split("_"))


########
# Parameter Processing Functions


def _extract_param(openapi_schemas: dict, data: dict):
    """Extract and normalize parameter information from OpenAPI spec."""
    tmp = {}
    if data:
        if data["schema"].get("$ref"):
            ref_name = data["schema"]["$ref"].split("/")[-1:][0]
            ref = openapi_schemas.get(ref_name, {})
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


def _add_import(imports: dict, package: str, module: str = "") -> None:
    """Add an import statement to the imports dictionary."""
    if not imports.get(package):
        if module:
            imports[package] = [module]
        else:
            imports[package] = None
    elif module not in imports[package]:
        imports[package].append(module)


def _process_params(
    openapi_schemas: dict,
    openapi_parameters: dict,
    endpoint_params: list,
    imports: dict,
    models: str,
    enums: str,
    parameters: str,
    mistapi_parameters: str,
    force_default: bool = False,
    optimization_parameter_name: str | None = None,
):
    """Process endpoint parameters and generate corresponding Python code."""
    for parameter in endpoint_params:
        if parameter.get("name") == "optimization_parameter_name":
            continue
        if parameter.get("$ref"):
            ref_name = parameter["$ref"].split("/")[-1:][0]
            data = openapi_parameters.get(ref_name, {})
            tmp_param = _extract_param(openapi_schemas, data)
        else:
            tmp_param = _extract_param(openapi_schemas, parameter)

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
            cleaned_description = description.replace(
                '"', "'").replace("\n", " ")
            annotations.append(f'description="""{cleaned_description}"""')
        elif tmp_param["name"].endswith("_id"):
            _add_import(imports, "pydantic", "Field")
            _add_import(imports, "typing", "Annotated")
            annotations.append(
                f'description="""ID of the Mist {tmp_param["name"].replace("_id", "").capitalize()}"""'
            )
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

        if tmp_param["type"] == "string":
            if tmp_param["format"] == "uuid":
                _add_import(imports, "uuid", "UUID")
                tmp_type = "UUID"
                if tmp_param["required"]:
                    tmp_mistapi_parameters = (
                        f"            {tmp_param['name']}=str({tmp_param['name']}),\n"
                    )
                else:
                    tmp_mistapi_parameters = f"            {tmp_param['name']}=str({tmp_param['name']}) if {tmp_param['name']} else None,\n"

            elif tmp_param["enum"]:
                _add_import(imports, "enum", "Enum")
                tmp_enum = f"\nclass {tmp_param['name'].capitalize()}(Enum):\n"
                tmp_choices = []
                for entry in tmp_param["enum"]:
                    # discard empty enums
                    if entry == "":
                        continue
                    e = entry.replace("/", "_").replace("-", "_")
                    tmp_choices.append(e.lower())
                    e_tmp = snake_case(e)
                    if e_tmp in ["24", "5", "6"]:
                        e_tmp = f"B{e_tmp}"
                    tmp_enum += f'    {e_tmp.upper()} = "{e}"\n'
                if (
                    not tmp_param["required"]
                    and not tmp_param["default"]
                    and "none" not in tmp_choices
                    and force_default
                ):
                    tmp_enum += "    NONE = None\n"
                enums += tmp_enum
                tmp_type = tmp_param["name"].capitalize()
                if tmp_param["default"]:
                    tmp_default = f" = {tmp_param['name'].capitalize()}.{tmp_param['default'].upper()}"
                    tmp_mistapi_parameters = f"            {tmp_param['name']}={tmp_param['name']}.value if {tmp_param['name']} else {tmp_param['name'].capitalize()}.{tmp_param['default'].upper()}.value,\n"
                elif force_default:
                    tmp_default = f" = {tmp_param['name'].capitalize()}.NONE"
                    tmp_mistapi_parameters = f"            {tmp_param['name']}={tmp_param['name']}.value if {tmp_param['name']} else None,\n"
                else:
                    tmp_mistapi_parameters = (
                        f"            {tmp_param['name']}={tmp_param['name']}.value,\n"
                    )
        elif tmp_param["type"] == "array":
            if (
                tmp_param.get("items", {}).get("$ref")
                or tmp_param.get("items", {}).get("type") == "string"
            ):
                _add_import(imports, "typing", "List")
                item_type = "str"
                if tmp_param.get("items", {}).get("$ref"):
                    ref_name = tmp_param["items"]["$ref"].split("/")[-1:][0]
                    ref = openapi_schemas.get(ref_name, {})
                    if ref.get("type") and TRANSLATION.get(ref.get("type")):
                        item_type = TRANSLATION.get(ref.get("type"))
                tmp_type = f"List[{item_type}]"
            else:
                _add_import(imports, "typing", "List")
                item_type = TRANSLATION.get(
                    tmp_param.get("items", {}).get("type", "string"), "str"
                )
                tmp_type = f"List[{item_type}]"

        if not tmp_default:
            if tmp_param["required"]:
                tmp_optional = ""
            # elif tmp_param["default"]:
            #     tmp_optional = ""
            #     if tmp_param["type"] == "string":
            #         tmp_default = f' = "{tmp_param["default"]}"'
            #         annotations.append(f'default="{tmp_param["default"]}"')
            #     else:
            #         tmp_default = f" = {tmp_param['default']}"
            #         annotations.append(f"default={tmp_param['default']}")
            else:
                _add_import(imports, "typing", "Optional")
                tmp_type = f"Optional[{tmp_type} | None]"
                # tmp_optional = " | None"
                tmp_default = " = None"
        elif not tmp_param["required"]:
            _add_import(imports, "typing", "Optional")
            tmp_type = f"Optional[{tmp_type} | None]"

        if annotations:
            _add_import(imports, "typing", "Annotated")
            _add_import(imports, "pydantic", "Field")
            tmp_type = f"Annotated[{tmp_type}, Field({','.join(annotations)})]"

        if not tmp_mistapi_parameters:
            tmp_mistapi_parameters = f"            {tmp_param['name']}={tmp_param['name']} if {tmp_param['name']} else None,\n"

        parameters += (
            f"    {tmp_param['name']}: {tmp_type}{tmp_optional}{tmp_default},\n"
        )

        if parameter.get("name") != optimization_parameter_name:
            mistapi_parameters += tmp_mistapi_parameters
    return imports, models, enums, parameters, mistapi_parameters


def gen_endpoint_parameters(
    openapi_parameters: dict,
    openapi_schemas: dict,
    path_parameters: list,
    endpoint: dict,
    optimization_parameter_name: str | None = None,
):
    """Generate complete parameter definitions for an endpoint."""
    imports = ""
    models = ""
    enums = ""
    parameters = ""
    mistapi_parameters = ""
    tmp_imports: dict = {}
    tmp_imports, models, enums, parameters, mistapi_parameters = _process_params(
        openapi_schemas,
        openapi_parameters,
        path_parameters,
        tmp_imports,
        models,
        enums,
        parameters,
        mistapi_parameters,
        False,
        optimization_parameter_name,
    )
    tmp_imports, models, enums, parameters, mistapi_parameters = _process_params(
        openapi_schemas,
        openapi_parameters,
        endpoint.get("parameters", []),
        tmp_imports,
        models,
        enums,
        parameters,
        mistapi_parameters,
        True,
        optimization_parameter_name,
    )
    for package, modules in tmp_imports.items():
        if modules:
            imports += f"from {package} import {', '.join(modules)}\n"
        else:
            imports += f"import {package}\n"
    if parameters:
        parameters = f"\n{parameters}"
    return imports, models, enums, parameters, mistapi_parameters


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


def _get_tag_defs(openapi_tags) -> dict:
    defs = {}
    for tag in openapi_tags:
        if tag.get("name") in EXCLUDED_TAGS or CUSTOM_TAGS.get(tag.get("name").lower()):
            continue
        else:
            defs[snake_case(tag.get("name")).lower()] = {
                "tools": [],
                "description": re.sub(
                    r"API Call", "tool", tag.get("description", ""), flags=re.IGNORECASE
                ),
            }
    for tag in CUSTOM_TAGS_DEFS:
        defs[snake_case(tag).lower()] = {
            "tools": [],
            "description": CUSTOM_TAGS_DEFS[tag],
        }
    return defs


def _gen_tools_init(tools_import: dict):
    """Generate import statements for the __init__.py file."""
    tmp = []
    for tag, modules in tools_import.items():
        for module in modules:
            # tmp.append(f"from {TOOLS_MODULE}.{tag}.{module} import {module}")
            tmp.append(f"from .{tag} import {module} as {module}")
        # tmp.append(f"from {TOOLS_MODULE}.{tag} import {", ".join(modules)}")
        # tmp.append(f"from .{tag} import {', '.join(modules)}")
        # tmp.append(f"from .{tag} import *")
    return "\n".join(tmp)


def main(openapi_paths, openapi_tags, openapi_parameters, openapi_schemas) -> None:
    """Main function to process the OpenAPI spec and generate tool files.

    This function:
    1. Processes each path in the OpenAPI specification
    2. Generates appropriate Python code for each endpoint
    3. Creates organized directory structure for tools
    4. Generates necessary files with proper imports and configurations
    """
    tag_to_tools: Dict[str, List[str]] = {}
    root_tag_defs = _get_tag_defs(openapi_tags)
    root_tools_import: dict = {}
    root_enums: list = []
    root_functions: dict = {}
    processed_operation_ids = []

    for func in CUSTOM_TOOLS:
        func_name = func["name"]
        func_tmpl = func["template"]
        func_tag = func.get("tag", "untagged")

        tag_dir = OUTPUT_DIR / snake_case(func_tag)
        tag_dir.mkdir(parents=True, exist_ok=True)
        init_file = tag_dir / "__init__.py"
        init_file.write_text("", encoding="utf-8")
        tool_file = tag_dir / f"{snake_case(func_name)}.py"
        tool_file.write_text(func_tmpl, encoding="utf-8")
        tag_to_tools.setdefault(func_tag, []).append(str(tool_file))

        #  tool_tools_import
        if not root_tools_import.get(snake_case(func_tag)):
            root_tools_import[snake_case(func_tag)] = []
        root_tools_import[snake_case(func_tag)].append(snake_case(func_name))
        # root_enums
        if (
            f'    {snake_case(func_tag).upper()} = "{snake_case(func_tag).lower()}"'
            not in root_enums
        ):
            root_enums.append(
                f'    {snake_case(func_tag).upper()} = "{snake_case(func_tag).lower()}"'
            )
        # root_functions
        if not root_functions.get(snake_case(snake_case(func_tag))):
            root_functions[snake_case(snake_case(func_tag))] = []
        root_functions[snake_case(snake_case(func_tag))].append(
            f"{snake_case(func_name)}.add_tool()"
        )
        # root_tag_defs
        root_tag_defs[snake_case(snake_case(func_tag))
                      ]["tools"].append(func_name)

    for func_name, func_data in OPTIMIZED_TOOLS.items():
        if (func_data.get("type") == "tool_consolidation") and (func_data.get("read_only_hint") is True or READ_ONLY_HINT is False):
            description = func_data.get("description", "")
            tag = func_data.get("tags", [])[0]
            enums_optim = []
            request = "\n"
            match_name = func_data.get("match_name", "object_type")
            if func_data.get("match_name"):
                request += f"    object_type = {func_data.get('match_name')}\n"
            request += "    match object_type.value:\n"

            for object_type, details in func_data.get("requests", {}).items():
                enums_optim.append(object_type)
                request += f"        case '{object_type}':\n"
                if func_data.get("read_only_hint") is False:
                    if details.get("update") and details.get("create"):
                        request += (
                            f"            if {func_data.get('if_filter', 'object_id')}:\n"
                            f"                response = {details['update'].get('function', '')}\n"
                            f"                await process_response(response)\n"
                            f"                data = response.data\n"
                            f"            else:\n"
                        )
                        processed_operation_ids.append(
                            details["update"].get("operationId", "").lower()
                        )
                    elif details.get("update"):
                        request += (
                            f"            response = {details['update'].get('function', '')}\n"
                            f"            await process_response(response)\n"
                            f"            data = response.data\n"
                        )
                        processed_operation_ids.append(
                            details["update"].get("operationId", "").lower()
                        )
                    if details.get("create"):
                        request += (
                            f"                response = {details['create'].get('function', '')}\n"
                            f"                await process_response(response)\n"
                            f"                data = response.data\n"
                        )
                        processed_operation_ids.append(
                            details["create"].get("operationId", "").lower()
                        )
                else:
                    if details.get("get") and details.get("list"):
                        request += (
                            f"            if {func_data.get('if_filter', 'object_id')}:\n"
                            f"                response = {details['get'].get('function', '')}\n"
                            f"                await process_response(response)\n"
                            f"                data = response.data\n"
                            f"            else:\n"
                        )
                        processed_operation_ids.append(
                            details["get"].get("operationId", "").lower()
                        )

                    elif details.get("get"):
                        request += (
                            f"            response = {details['get'].get('function', '')}\n"
                            f"            await process_response(response)\n"
                            f"            data = response.data\n"
                        )
                        processed_operation_ids.append(
                            details["get"].get("operationId", "").lower()
                        )
                    if details.get("list") and details.get("list", {}).get("reduce", False):
                        reduce_attribute = details["list"].get(
                            "reduce_attribute", "name")
                        request += (
                            f"                response = {details['list'].get('function', '')}\n"
                            f"                await process_response(response)\n"
                            f"                data = {{\n"
                            f"                    item.get('{reduce_attribute}'): item.get('id')\n"
                            f"                    for item in response.data\n"
                            f"                    if item.get('{reduce_attribute}')\n"
                            f"                }}\n"
                        )
                        processed_operation_ids.append(
                            details["list"].get("operationId", "").lower()
                        )
                    elif details.get("list"):
                        request += (
                            f"                response = {details['list'].get('function', '')}\n"
                            f"                await process_response(response)\n"
                            f"                data = response.data\n"
                        )
                        processed_operation_ids.append(
                            details["list"].get("operationId", "").lower()
                        )
            request += f"""
        case _:
            raise ToolError({{
                "status_code": 400,
                "message": f"Invalid object_type: {{object_type.value}}. Valid values are: {{[e.value for e in {match_name.capitalize()}]}}",
            }})
            """

            for param in func_data.get("parameters", []):
                if param.get("name") == match_name:
                    param["schema"]["enum"] = enums_optim
            imports, models, enums, parameters, mistapi_parameters = (
                gen_endpoint_parameters(
                    openapi_parameters,
                    openapi_schemas,
                    func_data.get("parameters", []),
                    {},
                    None,
                )
            )

            folder_path_parts, file_name = _gen_folder_and_file_paths(
                "/api/v1/orgs/{org_id}/consolidated"
            )

            if func_data.get("read_only_hint") is True:
                tool_code = TOOL_TEMPLATE_READ.format(
                    class_name=func_name.capitalize(),
                    imports=imports,
                    models=models,
                    enums=enums,
                    operationId=func_name,
                    description=description.replace("\n", ""),
                    tag=tag,
                    readOnlyHint=func_data.get("read_only_hint", False),
                    destructiveHint=func_data.get("destructive_hint", True),
                    parameters=parameters,
                    request=request,
                )
            else:
                tool_code = TOOL_TEMPLATE_WRITE.format(
                    class_name=func_name.capitalize(),
                    imports=imports,
                    models=models,
                    enums=enums,
                    operationId=func_name,
                    description=description.replace("\n", ""),
                    tag=tag,
                    readOnlyHint=func_data.get("read_only_hint", True),
                    destructiveHint=func_data.get("destructive_hint", True),
                    parameters=parameters,
                    request=request,
                )

            tag_dir = OUTPUT_DIR / snake_case(tag)
            tag_dir.mkdir(parents=True, exist_ok=True)
            init_file = tag_dir / "__init__.py"
            init_file.write_text("", encoding="utf-8")
            tool_file = tag_dir / f"{snake_case(func_name)}.py"
            tool_file.write_text(tool_code, encoding="utf-8")
            tag_to_tools.setdefault(tag, []).append(str(tool_file))

            #  tool_tools_import
            if not root_tools_import.get(snake_case(tag)):
                root_tools_import[snake_case(tag)] = []
            root_tools_import[snake_case(tag)].append(snake_case(func_name))
            # root_enums
            if (
                f'    {snake_case(tag).upper()} = "{snake_case(tag).lower()}"'
                not in root_enums
            ):
                root_enums.append(
                    f'    {snake_case(tag).upper()} = "{snake_case(tag).lower()}"'
                )
            # root_functions
            if not root_functions.get(snake_case(snake_case(tag))):
                root_functions[snake_case(snake_case(tag))] = []
            root_functions[snake_case(snake_case(tag))].append(
                f"{snake_case(func_name)}.add_tool()"
            )
            root_functions[snake_case(snake_case(tag))].append(
                f"TOOL_REMOVE_FCT.append({snake_case(func_name)}.remove_tool)"
            )
            # root_tag_defs
            root_tag_defs[snake_case(snake_case(tag))
                          ]["tools"].append(func_name)

    for path, methods in openapi_paths.items():
        for method, details in methods.items():
            if method.lower() == "get":
                read_only_hint = True
                destructive_hint = False
            elif method.lower() == "delete":
                destructive_hint = True
                read_only_hint = False
                continue
            elif method.lower() in ["post", "put"]:
                destructive_hint = True
                read_only_hint = False
                continue
            else:
                continue

            imports = ""
            models = ""
            enums = ""
            parameters = ""
            mistapi_parameters = ""
            tag = ""
            optimization_parameter_name = ""
            optimization_request = ""
            request = ""

            tags = details.get("tags", ["Untagged"])
            if len(tags) > 0 and tags[0] in EXCLUDED_TAGS:
                continue

            operation_id = details.get("operationId") or snake_case(
                path.strip("/").replace("/", "_")
            )
            if operation_id in EXCLUDED_OPERATION_IDS:
                continue
            if operation_id.lower() in processed_operation_ids:
                continue
            if operation_id.startswith("count"):
                continue
            if OPTIMIZED_TOOLS.get(operation_id):
                if OPTIMIZED_TOOLS[operation_id].get("skip", False):
                    continue
                for new_parameter in OPTIMIZED_TOOLS[operation_id].get(
                    "add_parameters", []
                ):
                    parameter = {
                        "name": new_parameter["name"],
                        "description": new_parameter.get("description", ""),
                        "in": "query",
                        "schema": {
                            "type": new_parameter["schema"]["type"],
                        },
                    }
                    if new_parameter.get("format"):
                        parameter["schema"]["format"] = new_parameter["format"]

                    if not details.get("parameters"):
                        details["parameters"] = []
                    details["parameters"].append(parameter)

                    optimization_parameter_name = new_parameter["name"]
                    optimization_request = OPTIMIZED_TOOLS[operation_id].get(
                        "custom_request"
                    )
            processed_operation_ids.append(operation_id.lower())
            description = details.get("description", "")

            tag = tags[0]
            if CUSTOM_TAGS.get(tag.lower()):
                tag = CUSTOM_TAGS[tag.lower()]

            imports, models, enums, parameters, mistapi_parameters = (
                gen_endpoint_parameters(
                    openapi_parameters,
                    openapi_schemas,
                    methods.get("parameters", []),
                    details,
                    optimization_parameter_name,
                )
            )

            folder_path_parts, file_name = _gen_folder_and_file_paths(path)
            mistapi_request = f"""mistapi.{".".join(folder_path_parts)}.{file_name}.{operation_id}(
            apisession,
{mistapi_parameters}    )"""

            if optimization_parameter_name:
                request = REQ_OPTIMIZED_TEMPLATE.format(
                    parameter=optimization_parameter_name,
                    custom_request=optimization_request,
                    request=mistapi_request,
                )
            else:
                request = REQ_TEMPLATE.format(request=mistapi_request)

            tool_code = TOOL_TEMPLATE_READ.format(
                class_name=operation_id.capitalize(),
                imports=imports,
                models=models,
                enums=enums,
                operationId=operation_id,
                description=description.replace("\n", ""),
                tag=tag,
                readOnlyHint=read_only_hint,
                destructiveHint=destructive_hint,
                parameters=parameters,
                request=request,
            )

            tag_dir = OUTPUT_DIR / snake_case(tag)
            tag_dir.mkdir(parents=True, exist_ok=True)
            init_file = tag_dir / "__init__.py"
            init_file.write_text("", encoding="utf-8")
            tool_file = tag_dir / f"{snake_case(operation_id)}.py"
            tool_file.write_text(tool_code)
            tag_to_tools.setdefault(tag, []).append(str(tool_file))

            #  tool_tools_import
            if not root_tools_import.get(snake_case(tag)):
                root_tools_import[snake_case(tag)] = []
            root_tools_import[snake_case(tag)].append(snake_case(operation_id))
            # root_enums
            if (
                f'    {snake_case(tag).upper()} = "{snake_case(tag).lower()}"'
                not in root_enums
            ):
                root_enums.append(
                    f'    {snake_case(tag).upper()} = "{snake_case(tag).lower()}"'
                )
            # root_functions
            if not root_functions.get(snake_case(snake_case(tag))):
                root_functions[snake_case(snake_case(tag))] = []
            root_functions[snake_case(snake_case(tag))].append(
                f"{snake_case(operation_id)}.add_tool()"
            )
            root_functions[snake_case(snake_case(tag))].append(
                f"TOOL_REMOVE_FCT.append({snake_case(operation_id)}.remove_tool)"
            )
            # root_tag_defs
            root_tag_defs[snake_case(snake_case(tag))
                          ]["tools"].append(operation_id)

    final_tag_tools = {}
    for tag_name, tag_data in root_tag_defs.items():
        if tag_data.get("tools"):
            final_tag_tools[tag_name] = tag_data
        else:
            print(f"Warning: Tag '{tag_name}' has no tools defined, skipping.")

    print("Generated tools grouped by tag:")
    for tag, files in tag_to_tools.items():
        print(f"{tag}:")
        for file in files:
            print(f"  - {file}")

    print("Generated tools grouped by tag:")
    for tag, files in tag_to_tools.items():
        print(f'{snake_case(tag).upper()} = "{snake_case(tag).lower()}"')

    with open(INIT_FILE, "w", encoding="utf-8") as f_init:
        f_init.write(
            INIT_TEMPLATE.format(
                tools_import=_gen_tools_init(root_tools_import))
        )

    with open(TOOLS_HELPER_FILE, "w", encoding="utf-8") as f_tool:
        f_tool.write(
            TOOLS_HELPER.format(
                enums="\n".join(root_enums),
                tools=json.dumps(final_tag_tools, indent=4, sort_keys=True),
            )
        )

    print(" TAGS SUMMARY ".center(80, "-"))
    tools = 0
    for tag, tag_data in final_tag_tools.items():
        tools += len(tag_data["tools"])
        print(f"{tag}: {len(tag_data['tools'])} tools")

    print(" CATEGORY SUMMARY ".center(80, "-"))
    print(f"Total API Calls: {len(processed_operation_ids)}")
    print(f"Total categories: {len(final_tag_tools)}")
    print(f"Total tools: {tools}")


# ---------------------------------------------------------------------------
# Schema pre-resolution for getObjectSchema tool
# ---------------------------------------------------------------------------

_SCHEMAS_DATA_FILE_HEADER = '''\
"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
Generated by mcp_generator/generate_from_openapi.py from schemas_config.yaml
and the Mist OpenAPI specification. Re-run the generator to update.
--------------------------------------------------------------------------------
"""

import json as _json

# Pre-resolved JSON schemas keyed by schema_name (= schemas_config.yaml entry key).
# Structure per entry:
#   "schema":       fully-resolved schema dict
#   "_schema_name": OAS component/schemas name used to resolve this entry
SCHEMAS_DATA: dict = _json.loads(
'''


def _resolve_schema_for_generator(
    schema: dict,
    all_schemas: dict,
    visited: frozenset = frozenset(),
    depth: int = 0,
    max_depth: int = 10,
) -> dict:
    """Recursively resolve $ref references in a schema (used at generation time).

    Circular references are detected via `visited` and replaced with a sentinel.
    """
    if depth >= max_depth:
        return {"$comment": "max depth reached"}
    if not isinstance(schema, dict):
        return schema
    resolved = {}
    for key, value in schema.items():
        if key == "$ref":
            ref_name = (
                value.split("/")[-1]
                if value.startswith("#/components/schemas/")
                else None
            )
            if ref_name and ref_name not in visited:
                ref_schema = all_schemas.get(ref_name)
                if ref_schema is not None:
                    resolved.update(
                        _resolve_schema_for_generator(
                            ref_schema, all_schemas, visited | {
                                ref_name}, depth + 1, max_depth
                        )
                    )
                    continue
            resolved[key] = (
                f"#{ref_name} (circular reference)" if ref_name in visited else value
            )
        elif key == "properties" and isinstance(value, dict):
            resolved[key] = {
                k: _resolve_schema_for_generator(
                    v, all_schemas, visited, depth + 1, max_depth)
                for k, v in value.items()
            }
        elif key in ("allOf", "anyOf", "oneOf") and isinstance(value, list):
            resolved[key] = [
                _resolve_schema_for_generator(
                    item, all_schemas, visited, depth + 1, max_depth)
                for item in value
            ]
        elif key in ("items", "additionalProperties") and isinstance(value, dict):
            resolved[key] = _resolve_schema_for_generator(
                value, all_schemas, visited, depth + 1, max_depth
            )
        else:
            resolved[key] = value
    return resolved


def generate_schemas_data(all_schemas: dict) -> None:
    """Read schemas_config.yaml, resolve each OAS schema, and write schemas_data.py.

    Format of schemas_config.yaml: {enum_name: oas_schema_name, ...}
    A bare key (no value) defaults the OAS schema name to the entry key itself.

    Each unique OAS schema name is resolved exactly once (cached by name), even
    when several enum names point to the same OAS schema.  The output is a Python
    module containing a single SCHEMAS_DATA dict that can be imported with zero
    I/O overhead at runtime.
    """
    raw_config = yaml.safe_load(
        SCHEMAS_CONFIG_PATH.read_text(encoding="utf-8")) or {}
    # raw_config: {enum_name: oas_schema_name | None, ...}

    # Cache resolved schemas by OAS name to avoid redundant work.
    resolved_cache: Dict[str, dict] = {}

    def get_resolved(schema_name: str) -> dict:
        if schema_name not in resolved_cache:
            raw_schema = all_schemas.get(schema_name)
            if raw_schema is None:
                print(
                    f"  WARNING: schema '{schema_name}' not found in OAS — stored as empty dict")
                resolved_cache[schema_name] = {}
            else:
                resolved_cache[schema_name] = _resolve_schema_for_generator(
                    raw_schema, all_schemas, visited=frozenset({schema_name})
                )
        return resolved_cache[schema_name]

    schemas_data: Dict[str, dict] = {}
    for enum_name, oas_name in raw_config.items():
        oas_name = oas_name or enum_name   # bare YAML key → fall back to key itself
        schemas_data[enum_name] = {
            "schema": get_resolved(oas_name),
            "_schema_name": oas_name,
        }

    json_str = json.dumps(schemas_data, indent=2, ensure_ascii=False)
    # Escape backslashes and triple-quote delimiters inside the JSON string so the
    # raw string literal in the generated Python file is syntactically valid.
    json_str_escaped = json_str.replace("\\", "\\\\").replace("'''", "\\'''")
    content = _SCHEMAS_DATA_FILE_HEADER + "'''\n" + json_str_escaped + "\n'''\n)\n"
    SCHEMAS_DATA_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SCHEMAS_DATA_OUTPUT_PATH.write_text(content, encoding="utf-8")
    size_kb = SCHEMAS_DATA_OUTPUT_PATH.stat().st_size // 1024
    print(
        f"schemas_data.py written: {len(schemas_data)} entries, ~{size_kb} KB")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate tools from OpenAPI specification.")
    parser.add_argument("--openapi", type=str, default=OPENAPI_PATH,
                        help="Path to the OpenAPI specification file.")
    parser.add_argument("-r", "--read_only", type=str,
                        help="Set read_only_hint to True for all tools.", default=True)
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    args = parser.parse_args()

    if str(args.read_only).lower() in ["false", "0", "no"]:
        READ_ONLY_HINT = False

    # Clean up existing tools directory
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    # Load and parse the OpenAPI specification
    with open(args.openapi, "r", encoding="utf-8") as f:
        openapi_json = yaml.safe_load(f)
    OPENAPI_PATHS = openapi_json.get("paths")
    OPENAPI_TAGS = openapi_json.get("tags")
    OPENAPI_PARAMETERS = openapi_json.get("components", {}).get("parameters")
    OPENAPI_SCHEMAS = openapi_json.get("components", {}).get("schemas")

    main(OPENAPI_PATHS, OPENAPI_TAGS, OPENAPI_PARAMETERS, OPENAPI_SCHEMAS)
    print("Tool generation completed successfully. READ_ONLY_HINT is set to", READ_ONLY_HINT)
    print(args.read_only)

    print("\nGenerating schemas_data.py...")
    generate_schemas_data(OPENAPI_SCHEMAS)
    print("schemas_data.py generation completed successfully.")
