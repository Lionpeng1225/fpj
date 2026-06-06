import json
import folium

from result_panel_style import get_result_panel_style
from result_panel_script import get_result_panel_script


def add_result_panel(taipei_map, questions):
    """
    結算遊戲結果面板。

    這個檔案現在只負責組合結算面板：
    1. HTML 結構
    2. CSS 樣式
    3. JavaScript 功能

    CSS 已分離到：
    result_panel_style.py

    JavaScript 已分離到：
    result_panel_script.py
    """

    questions_json = json.dumps(questions, ensure_ascii=False)

    html = f"""
    <div id="result-overlay" style="display: none;">
        <div id="result-panel">
            <div class="result-header">
                <h2>遊戲結算</h2>
            </div>

            <div id="result-loading" style="display: none;">
                正在使用 OSRM API 計算真實步行距離，請稍候...
            </div>

            <div id="result-summary"></div>

            <div id="result-map"></div>

            <div id="result-list"></div>

            <div class="result-actions">
                <button onclick="window.location.href='/'" class="home-result-button">
                    返回主畫面
                </button>
            </div>
        </div>
    </div>

    {get_result_panel_style()}

    {get_result_panel_script(questions_json)}
    """

    taipei_map.get_root().html.add_child(folium.Element(html))