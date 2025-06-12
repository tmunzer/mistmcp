""" "
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import os

import mistapi
from dotenv import load_dotenv

LOG_FILE = "./script.log"

load_dotenv()
ENV_FILE = os.getenv("MIST_ENV_FILE", "~/.mist_env")

# Create an HTTP client for your API


apisession = mistapi.APISession(env_file=ENV_FILE)
apisession.login()
