"""
Module for loading/interacting with data.
"""

import abc

import re
import pandas as pd
import geopandas
import pint
from pathlib import Path
from functools import cache

from forgery.constants import _CSV_DATA_REGISTRY, _SHAPE_FILE_REGISTRY, data_path

from forgery.events import clean_events
from forgery.utils import read_first_n_lines_as_text

_CLEANING_FUNCTIONS = {
    "events": [clean_events],
}

foot = pint.Unit("ft")
meter = pint.Unit("m")


class _DataLoader(abc.ABC):
    def __init__(self, data_registry, load_kwargs=None):
        self.data_registry = data_registry
        self._cache = {}
        self._load_kwargs = {} if load_kwargs is None else load_kwargs

    def _load_path(self, path, key):
        clean_funcs = _CLEANING_FUNCTIONS.get(key, [])
        obj = self.load_func(path)
        for func in clean_funcs:
            obj = func(obj)
        return obj

    def __getitem__(self, key):
        if key not in self._cache:
            value = self.data_registry[key]

            if isinstance(value, str | Path):
                obj = self._load_path(value, key)
            else:
                obj = {x.name: self._load_path(x, key) for x in value}
            self._cache[key] = obj
        return self._cache[key]

    @abc.abstractmethod
    def load_func(self, path):
        """Load the data."""


class CSVDataLoader(_DataLoader):
    """Simple class to load CSV data."""

    def load_func(self, path):
        return pd.read_csv(path)


class ShapeFileLoader(_DataLoader):
    """Load a shape file."""

    def load_func(self, path):
        return geopandas.read_file(path)


csv_data = CSVDataLoader(_CSV_DATA_REGISTRY)
shp_data = ShapeFileLoader(_SHAPE_FILE_REGISTRY)


def extract_16a_metadata(text):
    """Extract the outrageously messy header data for well 16a"""

    def clean_unit(unit_str):
        out = (
            unit_str.replace("'", "")
            .replace('"', "")
            .replace(",", "")
            .strip()
            .replace("us", "")  # us gets mixed up with micro
        )
        return out

    def extract_multi_word_field(label):
        pattern = rf"{label}\.*:,((?:[^,]+,)+)"
        match = re.search(pattern, text)
        out = None
        if match:
            parts = [p.strip() for p in match.group(1).split(",") if p.strip()]
            out = " ".join(parts)
            if label == "Well":
                out = out.split(" ")[0]
        return out

    def extract_numeric_with_unit(label):
        pattern = rf"{label}.*?:,([\d\.]+),([^,]+),"
        match = re.search(pattern, text)
        if match:
            value, unit_str = match.groups()
            unit_str_clean = clean_unit(unit_str)
            quantity = float(value) * pint.Quantity(unit_str_clean)
            return quantity.to(meter)
        return None

    results = {
        "client": extract_multi_word_field("Client"),
        "field": extract_multi_word_field("Field"),
        "well": extract_multi_word_field("Well"),
        "north": extract_numeric_with_unit(r"Latitude,\(\+N/S-\)"),
        "east": extract_numeric_with_unit(r"Departure,\(\+E/W-\)"),
        "kb_elevation": extract_numeric_with_unit(r"KB,above,permanent"),
        "gl_elevation": extract_numeric_with_unit(r"GL,above,permanent"),
    }

    return results


def read_16a_survey_data(path=data_path / "well_data" / "16A_survey.csv"):
    """Read the well location data from 16A."""
    header_txt = read_first_n_lines_as_text(path, 75)
    info = extract_16a_metadata(header_txt)
    columns = [
        "number",
        "measured_depth",
        "inclination",  # inclination
        "azimuth",  # azimuth
        "length",
        "vertical_depth",  # true vertical depth (TVD)
        "section",
        "delta_north",
        "delta_east",
        "horizontal_displacement",
        "azimuth_2?",
        "unknown",
        "tool",
        "qual",
        "",
    ]

    df = pd.read_csv(path, skiprows=76, header=None).drop(columns=[0, 16])
    df.columns = columns

    delta_east = (df["delta_east"].values * foot).to(meter)
    delta_north = (df["delta_north"].values * foot).to(meter)
    delta_elevation = -(df["vertical_depth"].values * foot).to(meter)

    east = info["east"] + delta_east
    north = info["north"] + delta_north
    elevation = info["kb_elevation"] + delta_elevation

    out = pd.DataFrame(
        {
            "east": east.magnitude,
            "north": north.magnitude,
            "elevation": elevation.magnitude,
        }
    )

    return out


def extract_16b_metadata(text):
    """
    Extracts easting, northing, elevations (KB and GL), units, and date from a metadata block.

    Parameters:
    - text (str): The metadata block as a string.

    Returns:
    - dict: Extracted values with keys: easting, northing, kb_elev, gl_elev, units, date
    """
    patterns = {
        "easting": re.compile(r"WELL EASTING\s*,,:\s*([\d.]+)([a-zA-Z]+)"),
        "northing": re.compile(r"WELL NORTHING\s*,,:\s*([\d.]+)([a-zA-Z]+)"),
        "kb_elev": re.compile(r"KB ELEV\s*,,:\s*([\d.]+)([a-zA-Z]+)"),
        "gl_elev": re.compile(r"GL ELEV\s*,,:\s*([\d.]+)([a-zA-Z]+)"),
        "date": re.compile(r"DATE\s*,,:\s*([\d/]+)"),
    }

    result = {}
    meter = pint.Quantity("m")
    for key, pattern in patterns.items():
        match = pattern.search(text)
        if match:
            if key == "date":
                result[key] = pd.to_datetime(match.group(1), format="%m/%d/%Y")
            else:
                units = pint.Quantity(match.group(2))
                quant = float(match.group(1)) * units
                result[key] = quant.to(meter)

    return result


def read_16b_survey_data(path=data_path / "well_data" / "16B_survey.csv"):
    """Read the well locations for 16B."""
    columns = [
        "measured_depth",
        "inclination",
        "azimuth",
        "true_vertical_depth",
        "subsea_true_vertical_depth",
        "north_south_displacement",
        "northing",
        "east_west_displacement",
        "easting",
        "vertical_section",
        "dog_leg_severity",
    ]

    header_txt = read_first_n_lines_as_text(path, 17)
    # Fortunately, this well already has coord location; leave this here
    # in case we need it later.
    info = extract_16b_metadata(header_txt)  # noqa

    df = pd.read_csv(path, skiprows=24, header=None, names=columns)
    east = (df["easting"].values * foot).to(meter)
    north = (df["northing"].values * foot).to(meter)
    elevation = (df["subsea_true_vertical_depth"].values * foot).to(meter)

    out = pd.DataFrame(
        {
            "east": east.magnitude,
            "north": north.magnitude,
            "elevation": elevation.magnitude,
        }
    )
    return out


@cache
def get_well_data():
    """Read the well data into a dict."""
    out = {
        "16a": read_16a_survey_data(),
        "16b": read_16b_survey_data(),
    }
    return out
