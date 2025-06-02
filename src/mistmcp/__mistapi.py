""""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""
import mistapi
ENV_FILE = "~/.mist_env_ld_ro"
LOG_FILE = "./script.log"


# Create an HTTP client for your API

apisession = mistapi.APISession(env_file=ENV_FILE)
apisession.login()
