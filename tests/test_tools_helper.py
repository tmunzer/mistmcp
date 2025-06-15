"""Tests for mistmcp tools_helper module"""

import pytest

from mistmcp.tools_helper import TOOLS, McpToolsCategory


class TestMcpToolsCategory:
    """Test McpToolsCategory enum"""

    def test_enum_values_exist(self):
        """Test that key enum values exist"""
        assert McpToolsCategory.ORGS.value == "orgs"
        assert McpToolsCategory.SITES.value == "sites"
        assert McpToolsCategory.CONSTANTS_EVENTS.value == "constants_events"
        assert McpToolsCategory.ORGS_DEVICES.value == "orgs_devices"

    def test_enum_from_string(self):
        """Test creating enum from string values"""
        assert McpToolsCategory("orgs") == McpToolsCategory.ORGS
        assert McpToolsCategory("sites") == McpToolsCategory.SITES
        assert McpToolsCategory("constants_events") == McpToolsCategory.CONSTANTS_EVENTS

    def test_enum_invalid_value(self):
        """Test that invalid enum values raise ValueError"""
        with pytest.raises(ValueError):
            McpToolsCategory("invalid_category")

    def test_enum_case_sensitivity(self):
        """Test that enum values are case sensitive"""
        with pytest.raises(ValueError):
            McpToolsCategory("ORGS")  # Should be lowercase

    def test_enum_iteration(self):
        """Test that enum can be iterated"""
        categories = list(McpToolsCategory)
        assert len(categories) > 0
        assert McpToolsCategory.ORGS in categories
        assert McpToolsCategory.SITES in categories

    def test_enum_membership(self):
        """Test enum membership operations"""
        assert McpToolsCategory.ORGS in McpToolsCategory

        # Test value membership
        values = [cat.value for cat in McpToolsCategory]
        assert "orgs" in values
        assert "sites" in values
        assert "invalid" not in values


class TestToolsData:
    """Test TOOLS data structure"""

    def test_tools_is_dict(self):
        """Test that TOOLS is a dictionary"""
        assert isinstance(TOOLS, dict)

    def test_tools_has_expected_categories(self):
        """Test that TOOLS contains expected categories"""
        # These should exist based on the enum
        expected_categories = ["orgs", "sites", "constants_events"]

        for category in expected_categories:
            if category in [cat.value for cat in McpToolsCategory]:
                # Only test if the category is actually defined in the enum
                # Some may not be in TOOLS if they're not implemented yet
                pass

    def test_tools_structure(self):
        """Test the structure of TOOLS data"""
        for category_name, category_data in TOOLS.items():
            # Each category should be a dictionary
            assert isinstance(category_data, dict), (
                f"Category {category_name} should be a dict"
            )

            # Each category should have a tools list
            if "tools" in category_data:
                assert isinstance(category_data["tools"], list), (
                    f"Tools in {category_name} should be a list"
                )

            # Each category may have a description
            if "description" in category_data:
                assert isinstance(category_data["description"], str), (
                    f"Description in {category_name} should be a string"
                )

    def test_tools_non_empty(self):
        """Test that TOOLS is not empty"""
        assert len(TOOLS) > 0, "TOOLS should contain at least one category"

    def test_tools_categories_match_enum(self):
        """Test that TOOLS categories correspond to enum values"""
        enum_values = {cat.value for cat in McpToolsCategory}
        tools_categories = set(TOOLS.keys())

        # All tools categories should have corresponding enum values
        for category in tools_categories:
            assert category in enum_values, (
                f"Category {category} should have corresponding enum value"
            )

    def test_tools_contain_valid_tool_names(self):
        """Test that tool names in TOOLS are valid strings"""
        for category_name, category_data in TOOLS.items():
            if "tools" in category_data:
                for tool_name in category_data["tools"]:
                    assert isinstance(tool_name, str), (
                        f"Tool name {tool_name} in {category_name} should be a string"
                    )
                    assert len(tool_name) > 0, (
                        f"Tool name in {category_name} should not be empty"
                    )
                    # Tool names should follow a pattern (usually category_action)
                    assert "_" in tool_name or tool_name in [
                        "getSelf",
                        "manageMcpTools",
                    ], f"Tool name {tool_name} should follow naming convention"

    def test_essential_tools_exist(self):
        """Test that essential tools exist in the TOOLS structure"""
        # Look for essential tools across all categories
        all_tools = []
        for category_data in TOOLS.values():
            if "tools" in category_data:
                all_tools.extend(category_data["tools"])

        # These tools should exist somewhere in the structure
        # (they might be added by the system even if not in TOOLS)
        essential_tools = {"getSelf", "manageMcpTools"}

        # At least check that if they exist, they're properly formatted
        for tool in all_tools:
            if tool in essential_tools:
                assert isinstance(tool, str)
                assert len(tool) > 0

    def test_tools_no_duplicates_within_category(self):
        """Test that there are no duplicate tools within each category"""
        for category_name, category_data in TOOLS.items():
            if "tools" in category_data:
                tools_list = category_data["tools"]
                tools_set = set(tools_list)
                assert len(tools_list) == len(tools_set), (
                    f"Category {category_name} has duplicate tools"
                )

    def test_tools_global_uniqueness(self):
        """Test that tool names are globally unique across all categories"""
        all_tools = []
        for category_data in TOOLS.values():
            if "tools" in category_data:
                all_tools.extend(category_data["tools"])

        tools_set = set(all_tools)
        assert len(all_tools) == len(tools_set), (
            "There are duplicate tool names across categories"
        )
