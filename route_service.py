import requests


OSRM_ROUTE_URL = "https://router.project-osrm.org/route/v1/foot"


def get_osrm_route(start_lat, start_lng, end_lat, end_lng):
    """
    使用 OSRM API 計算真實步行距離與時間。

    OSRM 的座標格式是：
    lng,lat

    這裡回傳原本 OSRM 的 JSON 格式，
    避免前端 JavaScript 原本讀 routes[0].distance 的地方壞掉。
    """

    try:
        coordinates = f"{start_lng},{start_lat};{end_lng},{end_lat}"

        url = f"{OSRM_ROUTE_URL}/{coordinates}"

        params = {
            "overview": "full",
            "geometries": "geojson",
            "steps": "false"
        }

        response = requests.get(
            url,
            params=params,
            timeout=15
        )

        response.raise_for_status()

        return response.json()

    except Exception as error:
        print("OSRM API error:", error)

        return {
            "error": "OSRM API 連線失敗",
            "routes": []
        }