"""
building_service.py
--------------------

This module provides helper functions for loading and processing the
geographic footprint of buildings within Taipei City.  It follows a
similar pattern to ``boundary_service.py``: load a GeoJSON file from
``data/taipei_buildings.geojson`` and convert each geometry into a list
of latitude/longitude coordinate pairs.  The resulting data can be
consumed by the front‑end to prevent the virtual person from
walking through buildings.

The GeoJSON file must contain a ``FeatureCollection`` where each
feature's geometry is either a ``Polygon`` or a ``MultiPolygon``.  If
the file is missing, the caller will receive a ``FileNotFoundError``.

Users of this module should ensure that the ``data/taipei_buildings.geojson``
file is present and up‑to‑date.  A common source for such data is
OpenStreetMap's building footprint exports.
"""

import json
from pathlib import Path

from shapely.geometry import shape

try:
    # geopandas is an optional dependency used to read GeoPackage
    import geopandas as gpd  # type: ignore
except ImportError:
    gpd = None

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
BUILDINGS_FILE = DATA_DIR / "taipei_buildings.geojson"

# Optional GeoPackage containing building footprints.  If present,
# building_service will attempt to load this file when the GeoJSON
# counterpart is missing.  The layer name is assumed to be "buildings".
BUILDINGS_GPKG = DATA_DIR / "buildings.gpkg"

# Approximate bounding box for Taipei City.  Buildings whose centroid
# falls outside this box will be ignored when reading from the
# GeoPackage.  Adjust these values if you need a more precise extent.
TAIPEI_MIN_LAT = 24.9500
TAIPEI_MAX_LAT = 25.2200
TAIPEI_MIN_LNG = 121.4300
TAIPEI_MAX_LNG = 121.6900


def load_taipei_buildings():
    """Load building footprints for Taipei City.

    This function first attempts to load ``data/taipei_buildings.geojson``
    if it exists.  When that file is missing, it falls back to
    ``data/buildings.gpkg`` provided geopandas is installed.  The
    GeoPackage is expected to have a layer named "buildings".  Only
    features whose centroid lies within the Taipei bounding box are
    returned.  If neither file is available or geopandas is not
    installed, a ``FileNotFoundError`` is raised.
    """
    if BUILDINGS_FILE.exists():
        with open(BUILDINGS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    # Fallback to GPKG if GeoJSON is unavailable
    if BUILDINGS_GPKG.exists():
        if gpd is None:
            raise FileNotFoundError(
                "要讀取 buildings.gpkg，需要先安裝 geopandas (pip install geopandas)"
            )
        # Read only the buildings layer
        gdf = gpd.read_file(BUILDINGS_GPKG, layer="buildings")
        # Filter by bounding box of Taipei City
        centroids = gdf.geometry.centroid
        mask = (
            (centroids.y >= TAIPEI_MIN_LAT)
            & (centroids.y <= TAIPEI_MAX_LAT)
            & (centroids.x >= TAIPEI_MIN_LNG)
            & (centroids.x <= TAIPEI_MAX_LNG)
        )
        filtered = gdf.loc[mask]
        # Convert to a minimal GeoJSON-like dict
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {key: row[key] for key in row.index if key != "geometry"},
                    "geometry": row.geometry.__geo_interface__,
                }
                for _, row in filtered.iterrows()
            ],
        }

    raise FileNotFoundError(
        "找不到台北市建築資料。請將 taipei_buildings.geojson 或 buildings.gpkg 放到 data 目錄。"
    )


def get_taipei_building_rings() -> list[list[list[float]]]:
    """Return a list of building outlines for Taipei City.

    Each building outline is represented as a list of [lat, lng]
    coordinate pairs describing the exterior ring of the building.  If a
    building is represented as a MultiPolygon, each polygon within the
    multi‑geometry is returned separately.  Invalid geometries are
    corrected using a zero‑distance buffer.  The function will
    automatically load data from ``taipei_buildings.geojson`` or fall
    back to ``buildings.gpkg`` using :func:`load_taipei_buildings`.
    """
    geojson_data = load_taipei_buildings()
    rings: list[list[list[float]]] = []
    for feature in geojson_data.get("features", []):
        geometry = shape(feature.get("geometry"))
        # Fix invalid geometries (self‑intersections etc.)
        if not geometry.is_valid:
            geometry = geometry.buffer(0)
        if geometry.geom_type == "Polygon":
            ring: list[list[float]] = []
            for lng, lat in geometry.exterior.coords:
                ring.append([lat, lng])
            rings.append(ring)
        elif geometry.geom_type == "MultiPolygon":
            for polygon in geometry.geoms:
                r: list[list[float]] = []
                for lng, lat in polygon.exterior.coords:
                    r.append([lat, lng])
                rings.append(r)
    return rings