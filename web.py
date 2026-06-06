from flask import Flask, render_template, request, jsonify

from map_service import create_taipei_map, render_map_html
from boundary_service import get_taipei_outer_rings
from question_bank import get_random_questions

from game_panel_service import add_question_panel
from marker_service import add_click_marker_script
from game_menu_service import add_game_menu
from result_service import add_result_panel

from geocoding_service import search_taipei_locations
from route_service import get_osrm_route
from mrt_service import add_mrt_routes
from mrt_menu_service import add_mrt_menu
from virtual_person_service import add_virtual_person
from street_view_service import add_street_view_panel
from walkability_layer_service import add_walkability_layer


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/difficulty")
def difficulty():
    return render_template("difficulty.html")


@app.route("/game/<level>")
def game(level):
    questions = get_random_questions(level, 10)

    taipei_map = create_taipei_map()
    outer_rings = get_taipei_outer_rings()

    # 加入捷運路線與站點
    add_mrt_routes(taipei_map)

    # 加入左下角「使用捷運」按鈕
    add_mrt_menu(taipei_map)

    # 加入虛擬人物
    add_virtual_person(taipei_map)

    # 加入右下角人物所在地街景
    add_street_view_panel(taipei_map)

    # 加入可走 / 不可走圖層
    add_walkability_layer(taipei_map)

    # 加入遊戲功能
    add_question_panel(taipei_map, questions, level)
    add_game_menu(taipei_map)
    add_result_panel(taipei_map, questions)

    html = render_map_html(taipei_map)

    html = add_click_marker_script(
        html,
        taipei_map.get_name(),
        outer_rings
    )

    return html


@app.route("/rules")
def rules():
    return render_template("rules.html")


@app.route("/api/search")
def search_location():
    """
    地點搜尋 API 路由。
    實際的 Nominatim API 呼叫在 geocoding_service.py。
    """

    query = request.args.get("q", "").strip()

    if not query:
        return jsonify([])

    results = search_taipei_locations(query)

    return jsonify(results)


@app.route("/api/route")
def get_route():
    """
    路線距離 API 路由。
    實際的 OSRM API 呼叫在 route_service.py。
    """

    start_lat = request.args.get("start_lat")
    start_lng = request.args.get("start_lng")
    end_lat = request.args.get("end_lat")
    end_lng = request.args.get("end_lng")

    if not all([start_lat, start_lng, end_lat, end_lng]):
        return jsonify({
            "error": "缺少座標參數",
            "routes": []
        })

    route_data = get_osrm_route(
        start_lat=start_lat,
        start_lng=start_lng,
        end_lat=end_lat,
        end_lng=end_lng
    )

    return jsonify(route_data)


if __name__ == "__main__":
    app.run(debug=True)