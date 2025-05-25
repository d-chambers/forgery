"""
Make MPL plots.
"""

import pandas as pd
import altair as alt
from functools import reduce
from operator import add


from forgery.tls import get_traffic_light_label
from forgery.utils import (
    get_reference_point_from_df,
    get_distance_from_point,
    get_boundary_points_to_plot,
)


def plot_event_mag_time(
    event_df, distance_reference_point=None, buffer=pd.Timedelta(days=0.5)
):
    """
    Make a magnitude vs time plot.

    Parameters
    ----------
    event_df
        The dataframe of events.
    distance_reference_point
        The point (in UTM easting, northing) for determining distances.
        If None, take the median of the events.
    """
    if distance_reference_point is None:
        distance_reference_point = get_reference_point_from_df(event_df)

    dist_m = get_distance_from_point(event_df, distance_reference_point)
    traffic_light = get_traffic_light_label(event_df, dist_m)

    x_min = event_df["time"].min() - buffer
    x_max = event_df["time"].max() + buffer
    # zoom = alt.selection_interval(bind='scales')

    events_chart = (
        alt.Chart(event_df)
        .mark_point()
        .encode(
            x=alt.X(
                "time:T",
                title="Date",
                axis=alt.Axis(format="%B %d"),
                scale=alt.Scale(domain=[x_min, x_max]),
            ),
            y=alt.Y("magnitude:Q", title="Magnitude", axis=alt.Axis(format=".1f")),
            size=alt.Size(
                "magnitude:Q", scale=alt.Scale(range=[10, 200]), title="Magnitude"
            ),
            # color='depth',
        )
    )

    alerts = list(traffic_light["alert"].unique())
    colors = list(traffic_light["color"].unique())

    light_charts = (
        alt.Chart(traffic_light)
        .mark_rule(strokeWidth=2)
        .encode(
            x="time:T",
            color=alt.Color(
                "alert:N",
                scale=alt.Scale(domain=alerts, range=colors),
                legend=alt.Legend(title="Alert"),
            ),
        )
    )

    tjaart = light_charts + events_chart
    return tjaart


def plot_map_2d(event_df, boundary, well_dict={}, plot_center=None):
    """
    Make a 2D plot of the events.
    """
    if plot_center is None:
        plot_center = get_reference_point_from_df(event_df)

    x_lims = plot_center[0] - 1_000, plot_center[0] + 1_000
    y_lims = plot_center[1] - 1_000, plot_center[1] + 1_000

    charts = []

    poly_coords = get_boundary_points_to_plot(polygon=boundary)
    alt_x = alt.X(
        "east:Q",
        scale=alt.Scale(zero=False, domain=x_lims),
        title="East (m)",
    )
    alt_y = alt.Y(
        "north:Q",
        scale=alt.Scale(zero=False, domain=y_lims),
        title="North (m)",
        axis=alt.Axis(tickCount=6),
    )

    zoom = alt.selection_interval(bind="scales")

    # Base seismic events points
    points = (
        alt.Chart(event_df)
        .mark_circle()
        .encode(
            x=alt_x,
            y=alt_y,
            color=alt.Color(
                "depth:Q", scale=alt.Scale(scheme="viridis", zero=False), title="Depth"
            ),
            size=alt.Size(
                "magnitude:Q", scale=alt.Scale(range=[10, 200]), title="Magnitude"
            ),
            tooltip=["magnitude", "depth"],
        )
    )
    charts.append(points)

    # Polygon outline (closed path)
    polygon_line = (
        alt.Chart(poly_coords)
        .mark_line(color="green", strokeWidth=2)
        .encode(
            x=alt_x,
            y=alt_y,
            order="index:Q",
        )
    )
    charts.append(polygon_line)

    # Add well data
    for well_name, df in well_dict.items():
        well_chart = (
            alt.Chart(df)
            .mark_line(color="gray")
            .encode(x=alt_x, y=alt_y, order="index:Q")
        )
        charts.append(well_chart)

    # # Combine all
    chart = (
        reduce(add, charts)
        .properties(title="FORGE Circulation Seismicity")
        .add_selection(zoom)
    )
    return chart
