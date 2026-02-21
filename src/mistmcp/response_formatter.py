"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import json

from mistapi.__api_response import APIResponse


def format_response_data(response: APIResponse) -> dict | list:
    """Extract data from an API response and inject ``_next`` pagination URL if present.

    Both Mist pagination mechanisms are handled transparently by the mistapi
    library which always exposes the next-page URL through ``response.next``:
    - Cursor-based (search endpoints): ``response.data["next"]`` URL
    - Header-based (list endpoints): synthesized from ``X-Page-*`` headers

    Returns a plain ``dict`` or ``list``.  If ``response.next`` is set the
    return value is enriched with a ``"_next"`` key so the caller can pass
    that URL to ``getNextPage`` to fetch the subsequent page.
    """
    data = response.data
    if response.next:
        if isinstance(data, list):
            return {"results": data, "_next": response.next}
        elif isinstance(data, dict):
            data = dict(data)
            data["_next"] = response.next
    return data


def format_response(
    response: APIResponse | dict | list, response_format: str
) -> dict | list | str:
    """Format an API response with pagination metadata and optional string serialisation.

    Combines :func:`format_response_data` (pagination injection) with the
    ``response_format`` preference coming from :func:`get_apisession`.
    """
    if isinstance(response, APIResponse):
        data = format_response_data(response)
    else:
        data = response
    if response_format == "string":
        return json.dumps(data)
    return data
