"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import mistapi
from fastmcp.exceptions import ClientError, NotFoundError
from fastmcp.server.dependencies import get_http_request
from starlette.requests import Request

from mistmcp.config import config
from mistmcp.logger import logger, mask_token


async def get_apisession() -> tuple[mistapi.APISession, str]:
    response_format = "json"

    if config.transport_mode == "http":
        try:
            apitoken = ""
            request: Request = get_http_request()
            cloud = (
                request.query_params.get("cloud", "")
                .replace("https://", "")
                .replace("http://", "")
            )
            if not cloud and request.headers.get("X-Mist-Cloud", ""):
                cloud = request.headers.get(
                    "X-Mist-Cloud", "").replace("https://", "").replace("http://", "")

            if request.headers.get("Authorization", None):
                apitoken = request.headers.get("Authorization", "").replace(
                    "Bearer ", ""
                )
            else:
                apitoken = request.headers.get("X-Authorization", "").replace(
                    "Bearer ", ""
                )

            if request.query_params.get("output", "").lower() == "string":
                response_format = "string"
        except NotFoundError as exc:
            raise ClientError(
                "HTTP request context not found. Are you using HTTP transport?"
            ) from exc

        if not cloud and not apitoken:
            raise ClientError(
                "Missing required parameters: 'X-Mist-Cloud' header or 'cloud' query parameter, and 'Authorization' or 'X-Authorization' header"
            )
        if not cloud:
            raise ClientError(
                "Missing required parameters: 'X-Mist-Cloud' header or 'cloud' query parameter"
            )
        if not apitoken:
            raise ClientError(
                "Missing required parameters: 'Authorization' or 'X-Authorization' header"
            )
    else:
        apitoken = config.mist_apitoken
        cloud = config.mist_host if config.mist_host else "api.mist.com"
        response_format = config.response_format

        if not cloud and not apitoken:
            raise ClientError(
                "Missing required parameters: mist_host and mist_apitoken in config"
            )
        if not cloud:
            raise ClientError(
                "Missing required parameter: mist_host in config"
            )
        if not apitoken:
            raise ClientError(
                "Missing required parameter: mist_apitoken in config"
            )

    logger.info("API request — host: %s, token: %s",
                cloud, mask_token(apitoken))

    apisession = mistapi.APISession(
        host=cloud,
        apitoken=apitoken,
    )

    return apisession, response_format
