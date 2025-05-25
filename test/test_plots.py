"""
Tests for forgery plotting functions.
"""

from forgery.data import shp_data, csv_data, get_well_data

from forgery.plot import plot_event_mag_time, plot_map_2d


class TestMagTime:
    """Test plotting magnitude and time."""

    def test_mag_time(self):
        """Ensure the mag/time plot works."""
        df = csv_data["events"]
        # boundary = shp_data['extents']
        tjaart = plot_event_mag_time(df)
        # There are weird class hierarchies, just check for the word chart.
        assert "Chart" in str(type(tjaart))


class TestMap2D:
    """Test plotting the 2D map."""

    def test_plot_map(self):
        """Plot the map."""
        df = csv_data["events"]
        permit = shp_data["extents"].iloc[1]["geometry"]
        well_map = get_well_data()
        plot_map_2d(df, permit, well_dict=well_map)
