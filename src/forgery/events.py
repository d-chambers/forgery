"""
Module for working with event data.
"""

import pandas as pd
import utm


def add_time(df):
    """Format time correctly in the dataframe."""
    time = pd.to_datetime(df["time(UTC)"])
    return df.drop(columns=["time(UTC)"]).assign(time=time)


def rename_columns(df):
    """Rename some columns to be more explicit."""
    return df.rename()


def add_utm(df):
    """Add utm coordinates for easier plotting."""
    lat = df["latitude"].values
    lon = df["longitude"].values
    east, north, zone_number, zone_letter = utm.from_latlon(lat, lon)
    return df.assign(
        east=east, north=north, zone_number=zone_number, zone_letter=zone_letter
    )


def clean_events(df, max_p_resid=0.25, max_s_resid=0.25):
    """Clean the event dataframe."""
    col_map = {
        "lat": "latitude",
        "lon": "longitude",
        "depth[m_local]": "depth",
        "P_residual[s]": "p_residual",
        "S_residual[s]": "s_residual",
    }
    out = df.pipe(add_time).rename(columns=col_map).pipe(add_utm)
    # Filter out bad locations
    ok = (out["p_residual"] <= max_p_resid) & (out["s_residual"] <= max_s_resid)
    return out[ok]
