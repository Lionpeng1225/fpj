import json

from marker_style import get_marker_style
from marker_script import get_marker_script


def add_click_marker_script(html, map_name, outer_rings):
    """
    地圖點擊標記功能入口。

    這個檔案現在只負責組合：
    1. 台北市邊界資料
    2. marker CSS
    3. marker JavaScript

    實際樣式放在：
    marker_style.py

    實際互動邏輯放在：
    marker_script.py
    """

    outer_rings_json = json.dumps(outer_rings, ensure_ascii=False)

    marker_html = (
        get_marker_style()
        + "\n"
        + get_marker_script(map_name, outer_rings_json)
    )

    if "</body>" in html:
        return html.replace("</body>", marker_html + "\n</body>")

    return html + marker_html