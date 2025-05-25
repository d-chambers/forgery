"""
Implementation of the traffic light system.
"""

import pandas as pd

from forgery.constants import (
    M_1_24_HOUR_LIMIT,
    AMBER_DISTANCE,
    RED_DISTANCE,
    RED_MAGNITUDE,
    ALERT_COLOR_MAP,
)


def _amber_alert(mag, dist_m):
    """Return a series with index as time indicating if amber alert is on."""
    # NOTE: Since the Cape Station events are excluded, I am assuming all events
    # are related to forge. Need to update this assumption later if used on real
    # data.
    in_dist = dist_m <= AMBER_DISTANCE

    mag_gt_1 = mag[(mag >= 1) & (in_dist)]

    # Determine which times are in yellow
    td = pd.to_timedelta(24, "h")
    m_gt_1_count = mag_gt_1.rolling(td).count()

    amber_big_count = m_gt_1_count > M_1_24_HOUR_LIMIT

    events_gt_2 = (mag >= 2) & (in_dist)

    out = pd.concat([amber_big_count, events_gt_2], axis=0)
    return out


def _red_alert(mag, distance_m):
    """Determine if red alert is active"""
    out = (mag >= RED_MAGNITUDE) & (distance_m <= RED_DISTANCE)
    return out


def get_traffic_light_label(df, dist_m) -> pd.DataFrame:
    """
    Get a dataframe indicating traffic light level and time.

    Parameters
    ----------
    df
        The dataframe containing the event data.
    distance_reference_point
        The point (in UTM easting/northing) for determining distances.
    """
    # First determine distance
    mag = df.set_index("time")["magnitude"]

    amber_alert = _amber_alert(mag, dist_m)
    amber_times = amber_alert[amber_alert].index.values
    amber = pd.Series(index=amber_times, dtype=object)
    amber[:] = "amber"

    red_alert = _red_alert(mag, dist_m)
    red_times = red_alert[red_alert].index.values
    red = pd.Series(index=red_times, dtype=object)
    red[:] = "red"

    out = (
        pd.concat([red, amber], axis=0)
        .loc[lambda x: ~x.index.duplicated()]
        .sort_index()
        .to_frame(name="alert")
        .reset_index()
        .rename(columns={"index": "time"})
        .assign(color=lambda x: x["alert"].map(ALERT_COLOR_MAP))
    )
    # Drop cases where the amber and red alerts are going
    return out
