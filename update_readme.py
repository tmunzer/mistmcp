#!/usr/bin/env python3
"""
Script to update the Tool Categories section in README.md
"""

import sys

sys.path.insert(0, "src")

from mistmcp.tool_helper import TOOLS


def clean_description(description):
    """Clean and summarize description to be single line"""
    if not description:
        return ""

    # Remove newlines and extra spaces
    cleaned = " ".join(description.split())

    # Escape pipes in descriptions
    cleaned = cleaned.replace("|", "\\|")

    # If description is too long, take first sentence or truncate
    if len(cleaned) > 200:
        # Try to find first sentence
        first_sentence = cleaned.split(".")[0]
        if len(first_sentence) < 150:
            cleaned = first_sentence + "."
        else:
            # Truncate at word boundary
            words = cleaned.split()
            truncated = []
            length = 0
            for word in words:
                if length + len(word) + 1 > 150:
                    break
                truncated.append(word)
                length += len(word) + 1
            cleaned = " ".join(truncated) + "..."

    return cleaned


def generate_table():
    """Generate the markdown table from TOOLS dictionary"""
    table_lines = [
        "| Category | Description | Tools | Tool List |",
        "|----------|-------------|-------|-----------|",
    ]

    for category, info in TOOLS.items():
        description = clean_description(info.get("description", ""))
        tools = info.get("tools", [])
        tool_count = len(tools)
        tool_list = ", ".join([f"`{tool}`" for tool in tools])

        # Format the row
        row = f"| **{category}** | {description} | {tool_count} | {tool_list} |"
        table_lines.append(row)

    return "\n".join(table_lines)


def update_readme():
    """Update the README.md file with new table"""
    with open("README.md", "r") as f:
        content = f.read()

    # Find the start and end markers for the Tool Categories section
    start_marker = "## 🔧 Tool Categories"
    end_marker = "## ⚠️ Current Limitations"

    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)

    if start_idx == -1 or end_idx == -1:
        print("Could not find Tool Categories section markers")
        return False

    # Generate new content
    new_section = f"""## 🔧 Tool Categories

The server organizes tools into logical categories. Use `manageMcpTools` to enable categories as needed:

### Essential Tools (Always Available)
- **`getSelf`** - User and organization information
- **`manageMcpTools`** - Enable/disable tool categories dynamically (only in managed mode)

### Available Tool Categories

{generate_table()}

Each client session maintains independent tool configurations for complete isolation.

"""

    # Replace the section
    new_content = content[:start_idx] + new_section + content[end_idx:]

    # Write back to file
    with open("README.md", "w") as f:
        f.write(new_content)

    print("✅ README.md updated successfully!")
    return True


if __name__ == "__main__":
    update_readme()
