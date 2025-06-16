"""Tests for mistmcp __version module"""

from mistmcp.__version import __version__


def test_version_exists() -> None:
    """Test that version is defined"""
    assert __version__ is not None
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_version_format() -> None:
    """Test that version follows semantic versioning pattern"""
    # Should be in format like "0.55.11" or similar
    parts = __version__.split(".")
    assert len(parts) >= 2  # At least major.minor
    for part in parts:
        assert part.isdigit()  # All parts should be numeric
