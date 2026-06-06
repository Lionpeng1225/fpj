import folium

from boundary_service import get_taipei_outer_rings


TAIPEI_CENTER = [25.068, 121.545]

TAIPEI_BOUNDS = [
    [24.9500, 121.4300],
    [25.2200, 121.6900]
]


def add_gray_mask(taipei_map, outer_rings):
    """
    在台北市外圍加上灰色遮罩。
    台北市內部會透過 evenodd 規則挖空。
    """

    outer_boundary = [
        [26.0, 120.5],
        [26.0, 122.5],
        [24.0, 122.5],
        [24.0, 120.5],
        [26.0, 120.5],
    ]

    mask_boundaries = [outer_boundary] + outer_rings

    folium.Polygon(
        locations=mask_boundaries,
        color="gray",
        weight=0,
        fill=True,
        fill_color="gray",
        fill_opacity=0.75,
        fill_rule="evenodd",
        interactive=False
    ).add_to(taipei_map)


def add_city_boundary_line(taipei_map, outer_rings):
    """
    畫出台北市邊界線。
    """

    for ring in outer_rings:
        folium.PolyLine(
            locations=ring,
            color="blue",
            weight=3,
            tooltip="台北市邊界"
        ).add_to(taipei_map)


def create_taipei_map():
    """
    建立台北市遊戲地圖。

    這個函式只負責：
    1. 建立 Folium 地圖
    2. 限制台北市視野範圍
    3. 加入灰色遮罩
    4. 加入台北市邊界線
    """

    outer_rings = get_taipei_outer_rings()

    taipei_map = folium.Map(
        location=TAIPEI_CENTER,
        zoom_start=12,
        min_zoom=11,
        max_zoom=18
    )

    taipei_map.fit_bounds(TAIPEI_BOUNDS)

    add_gray_mask(taipei_map, outer_rings)
    add_city_boundary_line(taipei_map, outer_rings)

    return taipei_map


def render_map_html(taipei_map):
    """
    將 Folium 地圖轉成 Flask 可以回傳的 HTML。
    """

    return taipei_map.get_root().render()