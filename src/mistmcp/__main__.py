""""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""
import sys
import getopt
from mistmcp.__server import mcp

LOG_FILE = "./script.log"

mcp_server = mcp


def start():
    try:
        opts, _ = getopt.getopt(
            sys.argv[1:],
            "hs",
            [
                "help",
                "streamable",
            ],
        )
    except getopt.GetoptError as err:
        print(err, file=sys.stderr)
        
    MODE="stdio"
    for o, _ in opts:
        if o in ["-s", "--streamable"]:
            MODE="streamable-http"
            
    try:
        if MODE == "streamable-http":
            mcp_server.run(transport="streamable-http", host="127.0.0.1")
        else:
            mcp_server.run()

    except KeyboardInterrupt:
        print("Mist MCP Server stopped by user")

    except Exception as e:
        print(f"Mist MCP Error: {e}", file=sys.stderr)

        
if __name__ == "__main__":
    start()
