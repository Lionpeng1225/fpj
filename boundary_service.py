import json
from pathlib import Path

from shapely.geometry import shape
from shapely.ops import unary_union


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
GEOJSON_FILE = DATA_DIR / "taipei_boundary.geojson"


def load_taipei_boundary():
    if not GEOJSON_FILE.exists():
        raise FileNotFoundError("找不到 data/taipei_boundary.geojson")

    with open(GEOJSON_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def get_taipei_outer_rings():
    """
    將 12 個行政區合併成台北市外框。
    回傳格式：
    [
        [[lat, lng], [lat, lng], ...]
    ]
    """
    geojson_data = load_taipei_boundary()

    polygons = []

    for feature in geojson_data["features"]:
        polygon = shape(feature["geometry"])

        if not polygon.is_valid:
            polygon = polygon.buffer(0)

        polygons.append(polygon)

    city_boundary = unary_union(polygons)

    if not city_boundary.is_valid:
        city_boundary = city_boundary.buffer(0)

    outer_rings = []

    if city_boundary.geom_type == "Polygon":
        ring = []

        for lng, lat in city_boundary.exterior.coords:
            ring.append([lat, lng])

        outer_rings.append(ring)

    elif city_boundary.geom_type == "MultiPolygon":
        for polygon in city_boundary.geoms:
            ring = []

            for lng, lat in polygon.exterior.coords:
                ring.append([lat, lng])

            outer_rings.append(ring)

    return outer_rings