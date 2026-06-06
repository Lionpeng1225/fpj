# mrt_service.py
import folium

from mrt_data import MRT_LINES


def draw_mrt_line(route_group, line_name, color, stations):
    """
    畫出捷運路線。
    """

    if len(stations) < 2:
        return

    locations = []

    for station in stations:
        locations.append([
            station["lat"],
            station["lng"]
        ])

    folium.PolyLine(
        locations=locations,
        color=color,
        weight=5,
        opacity=0.85,
        tooltip=line_name
    ).add_to(route_group)


def draw_mrt_station(route_group, line_name, color, station):
    """
    畫出捷運站點。
    """

    station_lat = station["lat"]
    station_lng = station["lng"]
    station_name = station["name"]

    popup_html = f"""
    <div style="font-family: Microsoft JhengHei, Arial; font-size: 14px;">
        <b>{station_name}</b><br>
        路線：{line_name}
    </div>
    """

    folium.CircleMarker(
        location=[station_lat, station_lng],
        radius=4,
        color=color,
        weight=2,
        fill=True,
        fill_color="white",
        fill_opacity=1,
        tooltip=f"{line_name}：{station_name}",
        popup=folium.Popup(popup_html, max_width=220)
    ).add_to(route_group)


def add_mrt_routes(taipei_map):
    """
    在地圖上加入台北市內捷運路線與站點。
    """

    for line_name, line_data in MRT_LINES.items():
        color = line_data["color"]
        stations = line_data["stations"]

        if not stations:
            continue

        route_group = folium.FeatureGroup(
            name=line_name,
            show=True
        )

        draw_mrt_line(
            route_group,
            line_name,
            color,
            stations
        )

        for station in stations:
            draw_mrt_station(
                route_group,
                line_name,
                color,
                station
            )

        route_group.add_to(taipei_map)

    folium.LayerControl(
        position="bottomleft",
        collapsed=True
    ).add_to(taipei_map)

    return taipei_map