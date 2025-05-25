"""
Misc utility functions.
"""

import numpy as np
import pandas as pd


def get_reference_point_from_df(df):
    """
    Get the x, y, z reference point from event dataframe.

    Simply use the median of all spatial coordinates.
    """
    columns = ["east", "north"]
    return df[columns].median().values


def get_distance_from_point(df, distance_reference_point):
    """Get the distance to each event from reference point."""
    dist_xy = df[["east", "north"]].values - np.atleast_2d(distance_reference_point)
    dist_m = np.linalg.norm(dist_xy, axis=1)
    return dist_m


def read_first_n_lines_as_text(file_path, lines=10) -> str:
    """
    Reads the first n lines of a file as plain text.

    Parameters
    ----------
    file_path
        Path to the file.
    lines
        Number of lines to read.

    Returns
    -------
        The first n lines of the file as str.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = [next(file).rstrip("\n") for _ in range(lines)]
        out = lines
    except StopIteration:
        print("File has fewer than n lines.")
        out = lines  # Return what was read
    except Exception as e:
        print(f"Error reading file: {e}")
        out = []
    return "\n".join(out)


def get_boundary_points_to_plot(polygon, columns=("east", "north")) -> pd.DataFrame:
    """
    Get xy values to plot from a polygon.

    Fixes common issues, but assumes concavity.
    """
    x, y = polygon.exterior.xy
    return pd.DataFrame({columns[0]: x, columns[1]: y})
