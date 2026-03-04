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

from mistmcp.logger import logger


def _get_total(response: APIResponse) -> int | None:
    """Extract total entries count from an API response if available.

    The total count of entries in a paginated list response can be provided by
    Mist in two ways:
    - In the response body under the "total" key (common in list endpoints)
    - In the "X-Page-Total" response header (common in search endpoints)

    This function checks both places and returns the total count as an integer
    if found, or None if not available.
    """
    total = None
    if response.headers and "X-Page-Total" in response.headers:
        try:
            total = int(response.headers["X-Page-Total"])
        except ValueError:
            pass
    elif isinstance(response.data, dict) and "total" in response.data:
        try:
            total = int(response.data["total"])
        except (ValueError, TypeError):
            pass
    return total


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
    total = _get_total(response)

    data = response.data

    if response.next:
        if isinstance(data, list):
            data = {"results": data, "next": response.next, "has_more": True}
            if total is not None:
                data["total"] = int(total)
        elif isinstance(data, dict):
            data = dict(data)
            data["next"] = response.next
            data["has_more"] = True
            if total is not None and "total" not in data:
                data["total"] = int(total)
    else:
        if isinstance(data, dict):
            data = dict(data)
            data["has_more"] = False

    return data


def format_response(
    response: APIResponse | dict | list, response_format: str
) -> dict | list | str:
    """Format an API response with pagination metadata and optional string serialisation.

    Combines :func:`format_response_data` (pagination injection) with the
    ``response_format`` preference coming from :func:`get_apisession`.
    """
    if isinstance(response, APIResponse):
        logger.debug("Formatting API response with pagination metadata")
        data = format_response_data(response)
    else:
        data = response
    if response_format == "string":
        logger.debug("Serializing response data to JSON string")
        return json.dumps(data)
    logger.debug("Returning response data as dict/list")
    return data
