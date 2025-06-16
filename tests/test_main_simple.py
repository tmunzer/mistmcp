"""Simple tests for mistmcp __main__ module functions"""

from mistmcp.__main__ import print_help


def test_print_help() -> None:
    """Test that print_help function executes without error"""
    # This will test that the function can be called and doesn't crash
    print_help()  # Should execute without raising any exceptions
