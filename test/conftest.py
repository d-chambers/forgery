"""Test config for forgery."""

import altair
import pytest


@pytest.fixture(scope="session", autouse=True)
def configure_altair():
    """Configure plotly to use browser renderer."""
    altair.renderers.enable("browser")
