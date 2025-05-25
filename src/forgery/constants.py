from pathlib import Path

# Explicit paths registering data.
here = Path(__file__).parent

data_path = here / "data"

_CSV_DATA_REGISTRY = {
    "events": data_path / "forge_events.csv",
    "surface": data_path / "land_surface_vertices.csv",
    "faults": [
        data_path / "Negro_Mag_Fault_vertices.csv",
        data_path / "Opal_Mound_Fault_vertices.csv",
    ],
    "granitoid": data_path / "top_granitoid_vertices.csv",
}

_SHAPE_FILE_REGISTRY = {"extents": data_path / "FORGE_Extent" / "FORGE_extent.shp"}

# The number of events that can occur in 24 hours without activating amber
# level.
M_1_24_HOUR_LIMIT = 10

# The distance to reference point to activate amber alert.
AMBER_DISTANCE = 3_000  # in m

# The distance to reference point for activating red level
RED_DISTANCE = 15_000

# The magnitude to trigger red alarm
RED_MAGNITUDE = 3.0

# Color map for plotting different alerts
ALERT_COLOR_MAP = {
    "amber": "#FFBF00",
    "red": "#ff4545",
}
