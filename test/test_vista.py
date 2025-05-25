"""
Tests for plotting things with pyvista.
"""

import pytest

from forgery.vista import ForgeVistaScene


class TestVista:
    """Simply scene creation test."""

    @pytest.fixture()
    def default_scene(self):
        """Get the default forge pyvista scene."""
        return ForgeVistaScene()()

    def test_scene_creation(self, default_scene):
        """Ensure the scene was created."""
