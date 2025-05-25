"""
Tests for data functions.
"""

import pandas as pd
import pytest

from forgery.data import read_16a_survey_data, read_16b_survey_data


class TestReadSurveyData:
    """Ensure the well survey can be read from 16A"""

    @pytest.fixture(scope="class")
    def well_df_16A(self):
        """Load 16A survey data."""
        return read_16a_survey_data()

    @pytest.fixture(scope="class")
    def well_df_16B(self):
        """Load 16B survey data."""
        return read_16b_survey_data()

    @pytest.fixture(scope="class", params=["well_df_16B", "well_df_16A"])
    def well_df(self, request):
        """Meta fixture to aggregate well dataframes."""
        return request.getfixturevalue(request.param)

    def test_output_type(self, well_df):
        """Ensure proper output."""
        required_cols = {"east", "north", "elevation"}
        assert isinstance(well_df, pd.DataFrame)
        assert set(well_df.columns).issuperset(required_cols)
