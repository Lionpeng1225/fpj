import requests


NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"

TAIPEI_LAT_MIN = 24.95
TAIPEI_LAT_MAX = 25.22
TAIPEI_LNG_MIN = 121.43
TAIPEI_LNG_MAX = 121.69


def is_in_taipei_area(lat, lng):
    """
    檢查座標是否在台北市附近範圍。
    避免搜尋結果跑到其他縣市。
    """

    return (
        TAIPEI_LAT_MIN <= lat <= TAIPEI_LAT_MAX
        and TAIPEI_LNG_MIN <= lng <= TAIPEI_LNG_MAX
    )


def search_taipei_locations(query):
    """
    使用 Nominatim API 搜尋台北地點候選。

    回傳格式要維持和原本 web.py 一樣，
    避免前端 JavaScript 壞掉：

    [
        {
            "display_name": "...",
            "lat": "...",
            "lon": "..."
        }
    ]
    """

    if not query:
        return []

    params = {
        "q": query + " 台北",
        "format": "json",
        "limit": 6,
        "addressdetails": 1
    }

    headers = {
        "User-Agent": "Taipei-Orienteering-Game/1.0"
    }

    try:
        response = requests.get(
            NOMINATIM_SEARCH_URL,
            params=params,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        results = []

        for item in data:
            lat = float(item["lat"])
            lng = float(item["lon"])

            if is_in_taipei_area(lat, lng):
                results.append({
                    "display_name": item.get("display_name", ""),
                    "lat": item["lat"],
                    "lon": item["lon"]
                })

        return results

    except Exception as error:
        print("Nominatim API error:", error)
        return []