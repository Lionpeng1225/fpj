# mrt_menu_service.py
import json
import folium

from mrt_data import MRT_LINES
from mrt_menu_data import (
    STATION_CODE_MAP,
    LINE_STATION_ORDER,
    MRT_TRANSFER_DATA
)
from mrt_menu_style import get_mrt_menu_style
from mrt_menu_script import get_mrt_menu_script


def build_mrt_menu_data():
    """
    整合捷運選單需要的資料。

    這裡保留在 mrt_menu_service.py，
    是因為它是「捷運選單功能」的主要資料整理流程，
    不是單純靜態資料，也不是純 CSS / JS。
    """

    menu_data = {}

    for line_name, station_names in LINE_STATION_ORDER.items():
        if line_name not in MRT_LINES:
            continue

        line_info = MRT_LINES[line_name]
        line_color = line_info["color"]

        station_lookup = {}

        for station in line_info["stations"]:
            station_lookup[station["name"]] = station

        menu_stations = []

        for station_name in station_names:
            if station_name not in station_lookup:
                continue

            station = station_lookup[station_name]
            station_code = STATION_CODE_MAP[line_name].get(station_name, "")

            menu_stations.append({
                "code": station_code,
                "name": station_name,
                "lat": station["lat"],
                "lng": station["lng"],
            })

        menu_data[line_name] = {
            "color": line_color,
            "stations": menu_stations,
        }

    return menu_data


def build_mrt_menu_html(mrt_menu_json, mrt_transfer_json, map_name):
    """
    組合捷運選單的 HTML、CSS、JavaScript。

    這裡也保留在 service 裡，
    讓 mrt_menu_service.py 不會變成只有 import 和呼叫函式。
    """

    html = f"""
    {get_mrt_menu_style()}

    <button id="mrt-menu-button" class="disabled" onclick="toggleMrtMenu()">
        附近無捷運站
    </button>

    <div id="mrt-menu-panel">
        <div id="mrt-menu-header">
            <span>使用捷運</span>
            <button id="mrt-menu-close" onclick="closeMrtMenu()">×</button>
        </div>

        <div id="mrt-menu-content"></div>
    </div>

    {get_mrt_menu_script(mrt_menu_json, mrt_transfer_json, map_name)}
    """

    return html


def add_mrt_menu(taipei_map):
    """
    在左下角加入「使用捷運」功能。

    功能包含：
    1. 只有人物 100 公尺範圍內有捷運站時才能使用捷運
    2. 五條路線都顯示
    3. 可用路線可以展開
    4. 不可用路線變淡且不能展開
    5. 點擊站名後，虛擬人物會移動到該站
    """

    mrt_menu_data = build_mrt_menu_data()

    mrt_menu_json = json.dumps(mrt_menu_data, ensure_ascii=False)
    mrt_transfer_json = json.dumps(MRT_TRANSFER_DATA, ensure_ascii=False)

    map_name = taipei_map.get_name()

    html = build_mrt_menu_html(
        mrt_menu_json=mrt_menu_json,
        mrt_transfer_json=mrt_transfer_json,
        map_name=map_name
    )

    taipei_map.get_root().html.add_child(folium.Element(html))