#!/usr/bin/env python3
"""Test script to verify tools are loaded correctly"""

import asyncio
import os
import sys

# Set basic environment
os.environ["MIST_APITOKEN"] = "test"
os.environ["MIST_HOST"] = "api.mist.com"

# Add src to path for imports
sys.path.insert(0, "src")

from mistmcp.server_factory import load_tools, mcp


async def main():
    print("Testing MCP Server Tools Loading...")
    print("=" * 50)

    print("✓ MCP instance created")

    # Load tools
    load_tools()
    print("✓ Tools loaded")

    # Get tools count
    tools = await mcp.get_tools()
    tool_count = len(tools)

    print(f"✓ Total tools registered: {tool_count}")

    if tool_count > 0:
        print("\nFirst 10 tools:")
        for i, (name, tool) in enumerate(list(tools.items())[:10]):
            print(f"  {i + 1:2d}. {name}")
    else:
        print("\n❌ ERROR: No tools found!")
        return 1

    print(f"\n✅ SUCCESS: {tool_count} tools are properly registered")
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
