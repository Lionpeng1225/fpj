import json
import math
from pathlib import Path

from shapely.geometry import shape

try:
    import geopandas as gpd
except ImportError:
    gpd = None


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

BUILDINGS_GPKG = DATA_DIR / "buildings.gpkg"
BUILDINGS_GEOJSON = DATA_DIR / "taipei_buildings.geojson"
BUILDING_COLLISION_FILE = DATA_DIR / "taipei_buildings_collision.json"

TAIPEI_MIN_LAT = 24.9500
TAIPEI_MAX_LAT = 25.2200
TAIPEI_MIN_LNG = 121.4300
TAIPEI_MAX_LNG = 121.6900

# 簡化建築物外框，數值越大越省資料，但越不精準
# 0.00002 約等於 2 公尺左右
SIMPLIFY_TOLERANCE = 0.00002

# 前端碰撞檢查用網格，0.001 度約 100 公尺
GRID_SIZE = 0.001


def is_in_taipei_bbox(min_lat, min_lng, max_lat, max_lng):
    """
    檢查建築物 bbox 是否和台北市大略範圍有交集。
    """

    if max_lat < TAIPEI_MIN_LAT:
        return False

    if min_lat > TAIPEI_MAX_LAT:
        return False

    if max_lng < TAIPEI_MIN_LNG:
        return False

    if min_lng > TAIPEI_MAX_LNG:
        return False

    return True


def get_cell_index(value):
    return math.floor(value / GRID_SIZE)


def get_cell_key(lat_index, lng_index):
    return f"{lat_index}:{lng_index}"


def add_building_to_grid(grid, building_index, bbox):
    """
    把建築物放進它 bbox 覆蓋到的網格中。

    bbox 格式：
    [min_lat, min_lng, max_lat, max_lng]
    """

    min_lat, min_lng, max_lat, max_lng = bbox

    min_lat_index = get_cell_index(min_lat)
    max_lat_index = get_cell_index(max_lat)
    min_lng_index = get_cell_index(min_lng)
    max_lng_index = get_cell_index(max_lng)

    for lat_index in range(min_lat_index, max_lat_index + 1):
        for lng_index in range(min_lng_index, max_lng_index + 1):
            key = get_cell_key(lat_index, lng_index)

            if key not in grid:
                grid[key] = []

            grid[key].append(building_index)


def polygon_to_collision_building(polygon):
    """
    將 shapely Polygon 轉成前端碰撞需要的格式。
    """

    if not polygon.is_valid:
        polygon = polygon.buffer(0)

    if polygon.is_empty:
        return None

    polygon = polygon.simplify(
        SIMPLIFY_TOLERANCE,
        preserve_topology=True
    )

    if polygon.is_empty:
        return None

    min_lng, min_lat, max_lng, max_lat = polygon.bounds

    if not is_in_taipei_bbox(min_lat, min_lng, max_lat, max_lng):
        return None

    ring = []

    for lng, lat in polygon.exterior.coords:
        ring.append([lat, lng])

    if len(ring) < 4:
        return None

    return {
        "bbox": [
            min_lat,
            min_lng,
            max_lat,
            max_lng
        ],
        "ring": ring
    }


def geometry_to_collision_buildings(geometry):
    """
    支援 Polygon / MultiPolygon。
    """

    buildings = []

    if geometry.is_empty:
        return buildings

    if not geometry.is_valid:
        geometry = geometry.buffer(0)

    if geometry.geom_type == "Polygon":
        building = polygon_to_collision_building(geometry)

        if building is not None:
            buildings.append(building)

    elif geometry.geom_type == "MultiPolygon":
        for polygon in geometry.geoms:
            building = polygon_to_collision_building(polygon)

            if building is not None:
                buildings.append(building)

    return buildings


def load_building_geometries():
    """
    讀取建築物資料。

    優先順序：
    1. data/taipei_buildings.geojson
    2. data/buildings.gpkg
    """

    if BUILDINGS_GEOJSON.exists():
        with open(BUILDINGS_GEOJSON, "r", encoding="utf-8") as file:
            geojson_data = json.load(file)

        geometries = []

        for feature in geojson_data.get("features", []):
            if not feature.get("geometry"):
                continue

            geometries.append(shape(feature["geometry"]))

        return geometries

    if BUILDINGS_GPKG.exists():
        if gpd is None:
            raise ImportError(
                "要讀取 data/buildings.gpkg，請先安裝 geopandas：pip install geopandas"
            )

        gdf = gpd.read_file(BUILDINGS_GPKG, layer="buildings")

        # 確保座標系是 WGS84 經緯度
        if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs(epsg=4326)

        # 先用 bbox 粗篩，避免處理非台北市建築物
        gdf = gdf.cx[
            TAIPEI_MIN_LNG:TAIPEI_MAX_LNG,
            TAIPEI_MIN_LAT:TAIPEI_MAX_LAT
        ]

        return list(gdf.geometry)

    raise FileNotFoundError(
        "找不到建築物資料。請確認 data/buildings.gpkg 或 data/taipei_buildings.geojson 是否存在。"
    )


def build_collision_data():
    """
    建立前端碰撞資料。
    """

    geometries = load_building_geometries()

    buildings = []
    grid = {}

    for geometry in geometries:
        collision_buildings = geometry_to_collision_buildings(geometry)

        for building in collision_buildings:
            building_index = len(buildings)
            buildings.append(building)
            add_building_to_grid(
                grid=grid,
                building_index=building_index,
                bbox=building["bbox"]
            )

    return {
        "gridSize": GRID_SIZE,
        "buildings": buildings,
        "grid": grid
    }


def save_collision_data():
    """
    產生 data/taipei_buildings_collision.json。
    """

    DATA_DIR.mkdir(exist_ok=True)

    collision_data = build_collision_data()

    with open(BUILDING_COLLISION_FILE, "w", encoding="utf-8") as file:
        json.dump(
            collision_data,
            file,
            ensure_ascii=False,
            separators=(",", ":")
        )

    print("已產生建築物碰撞資料：", BUILDING_COLLISION_FILE)
    print("建築物數量：", len(collision_data["buildings"]))
    print("網格數量：", len(collision_data["grid"]))


def load_collision_data():
    """
    載入碰撞資料。

    如果 data/taipei_buildings_collision.json 不存在，
    就自動從 buildings.gpkg / taipei_buildings.geojson 產生。
    """

    if not BUILDING_COLLISION_FILE.exists():
        save_collision_data()

    with open(BUILDING_COLLISION_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def get_building_collision_json():
    """
    給 virtual_person_service.py 使用。
    回傳 JSON 字串，直接塞進前端 JavaScript。
    """

    try:
        collision_data = load_collision_data()
        return json.dumps(collision_data, ensure_ascii=False)

    except Exception as error:
        print("建築物碰撞資料載入失敗：", error)

        empty_data = {
            "gridSize": GRID_SIZE,
            "buildings": [],
            "grid": {}
        }

        return json.dumps(empty_data, ensure_ascii=False)


if __name__ == "__main__":
    save_collision_data()