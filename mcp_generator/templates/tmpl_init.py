# Template for the main __init__.py file
INIT_TEMPLATE = '''"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

{tools_import}
'''

REQ_TEMPLATE = """
    response = {request}
"""

REQ_OPTIMIZED_TEMPLATE = """
    if {parameter}:
        response = {custom_request}
    else:
        response = {request}
"""
