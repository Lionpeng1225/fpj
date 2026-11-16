# 臺北市線上定向越野
## Taipei Online Orienteering

一個以臺北市為遊戲場景的互動式線上定向越野遊戲。玩家根據街景圖片判斷地點，在地圖上探索、移動虛擬人物並提交答案；結算時，系統以步行路線距離計分。

本專案是「計算機程式設計一」期末專題，採用 Flask 建立網站，並將地圖、題目、移動、捷運、街景與結算拆成獨立模組。

## 功能

- **臺北市互動地圖**：顯示臺北市範圍與行政區邊界，並限制遊戲地圖的瀏覽範圍。
- **兩種題目難度**：
  - 簡單模式從臺北市地標題庫隨機出題。
  - 困難模式從多條道路的街景位置抽題。
  - 每場遊戲最多抽出 10 題。
- **街景辨識**：題目使用 Google Street View 圖片；遊戲畫面也能查看虛擬人物附近的街景。
- **虛擬人物探索**：使用鍵盤移動人物；人物不能走出臺北市邊界。開始遊戲前可選擇是否啟用建築物碰撞。
- **答案標記**：在人物附近的允許範圍內點擊地圖放置答案標記；按 Enter 固定或解除固定目前題目的標記，按 Backspace 刪除標記。
- **捷運移動**：地圖顯示臺北捷運路線與站點；人物接近車站時可使用捷運選單移動至可到達的站點。
- **地點搜尋**：透過 Nominatim 搜尋臺北市地點。
- **步行路線與結算**：透過 OSRM 計算玩家答案到正確答案的步行路線、距離與時間，並於結果地圖標示兩個位置和路線。
- **可走範圍圖層**：啟用建築物阻擋時，可開關建築物範圍顯示；放大地圖後會顯示紅色建築物區域。

## 遊戲流程

1. 在首頁選擇開始遊戲，或先閱讀遊戲規則。
2. 選擇簡單或困難模式，並設定是否啟用建築物阻擋。
3. 查看題目街景圖片與提示，使用地圖探索臺北市。
4. 需要時移動虛擬人物、查看周圍街景或搭乘捷運。
5. 在人物附近點擊地圖放置答案標記。可切換題目並返回修改尚未固定的標記。
6. 完成題目後按下結算，查看每題的答案、步行距離、路線、時間及分數。

每題滿分 100 分，每相差 1 公里扣 10 分，最低為 0 分：

    分數 = max(0, 100 - 步行距離（公里） × 10)

未作答的題目得 0 分；若路線服務無法回傳距離，該題也無法取得距離分數。結果面板顯示各題成績與平均分數，分數顯示至小數點後兩位。

## 使用技術與外部服務

| 技術／服務 | 用途 |
| --- | --- |
| Python、Flask | 網站路由、遊戲頁面與搜尋／路線 API |
| Folium、Leaflet | 互動式地圖與瀏覽器端地圖操作 |
| Shapely | 臺北市邊界與建築物幾何處理 |
| Google Street View Static API | 題目街景圖片 |
| Google Maps JavaScript API | 人物附近的互動式街景 |
| Nominatim（OpenStreetMap） | 臺北市地點搜尋 |
| OSRM 公開路由服務 | 計算步行距離、時間與路線 |

地點搜尋與路線計算需要網路連線。公開服務可能有使用限制或暫時無法連線；Google Maps 服務則需依 Google Cloud 的 API、金鑰與帳務設定使用。

## 安裝與執行

### 需求

- Python 3.9 或更新版本
- Git（若從 GitHub 複製專案）
- 7-Zip 或可解壓縮 .7z 的工具
- Google Maps API 金鑰（使用街景功能時）

目前 GitHub 專案沒有提供 requirements.txt，請先安裝所需套件：

    python -m pip install Flask folium requests shapely python-dotenv

若資料包只有 GeoPackage 建築資料（.gpkg）而沒有 GeoJSON，還需要安裝 GeoPandas：

    python -m pip install geopandas

### 1. 取得專案並安裝套件

    git clone https://github.com/Lionpeng1225/fpj.git
    cd fpj

建議建立虛擬環境，再安裝上述套件。

Windows PowerShell：

    py -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install Flask folium requests shapely python-dotenv

macOS / Linux：

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install Flask folium requests shapely python-dotenv

### 2. 解壓縮地圖資料

專案根目錄的 data.7z 存放遊戲使用的地圖與建築物資料。將它解壓縮到專案根目錄，並確認解壓後的 data 資料夾位於 web.py 旁邊。至少需要：

- data/taipei_boundary.geojson：臺北市邊界資料。
- 建築物資料：data/taipei_buildings.geojson 或 data/buildings.gpkg。若使用 GeoPackage，請安裝 GeoPandas。
- 若已存在，data/taipei_buildings_collision.json 是供碰撞判斷使用的預處理資料；缺少時程式會嘗試從建築物來源建立。

解壓縮後的資料夾結構應類似：

```text
fpj/
├── web.py
├── data.7z
├── data/
│   ├── taipei_boundary.geojson
│   └── taipei_buildings.geojson   # 或 buildings.gpkg
└── templates/
```

若啟動時出現找不到邊界檔案的錯誤，請確認 GeoJSON 檔案實際位於 data 子資料夾，而不是多包了一層資料夾。

### 3. 設定 Google Maps API 金鑰

在專案根目錄建立 .env，內容如下：

```dotenv
GOOGLE_STREET_VIEW_API_KEY=你的_Google_Maps_API_Key
```

程式使用此環境變數載入題目街景圖片和人物周圍街景。請在 Google Cloud 專案中啟用 **Street View Static API** 與 **Maps JavaScript API**，並依 Google 的要求設定帳務、金鑰限制及使用配額。不要把真實金鑰提交到 GitHub；.env 已列入 .gitignore。由於金鑰會用於瀏覽器端地圖／街景請求，請依 Google 的建議限制可使用的 API 與 HTTP referrer。

### 4. 啟動網站

在專案根目錄執行：

```bash
python web.py
```

接著使用瀏覽器開啟 http://127.0.0.1:5000 。目前程式使用 Flask 開發伺服器與除錯模式，適合本機課程展示；正式對外部署前，應改用適合部署的 WSGI 伺服器並停用除錯模式。

## 網頁路由與 API

| 路徑 | 說明 |
| --- | --- |
| / | 遊戲首頁 |
| /rules | 遊戲規則頁 |
| /difficulty | 難度及建築物阻擋設定 |
| /game/easy | 簡單模式遊戲 |
| /game/hard | 困難模式遊戲 |
| /api/search?q=地點 | 搜尋臺北市地點，回傳候選位置 |
| /api/route?start_lat=...&start_lng=...&end_lat=...&end_lng=... | 計算兩組座標間的步行路線 |

## 專案結構

```text
fpj/
├── web.py                         # Flask 網站入口、頁面路由與 API
├── map_service.py                 # Folium 地圖、範圍與邊界
├── boundary_service.py            # 臺北市 GeoJSON 邊界載入與處理
├── question_bank.py               # 簡單／困難題庫與街景圖片網址
├── game_panel_service.py          # 題目面板與提示
├── question_image_script.py       # 題目切換與圖片互動
├── marker_service.py              # 答案標記前端程式入口
├── marker_script.py               # 標記放置、範圍與固定／刪除
├── virtual_person_service.py      # 人物移動、邊界與碰撞判斷
├── building_service.py            # 建築物 GeoJSON／GeoPackage 載入
├── building_collision_service.py  # 碰撞資料建立、載入與網格索引
├── walkability_layer_service.py   # 建築物可走範圍圖層
├── mrt_data.py                    # 捷運路線與站點資料
├── mrt_service.py                 # 地圖上的捷運路線與站點
├── mrt_menu_data.py               # 捷運選單資料
├── mrt_menu_service.py            # 捷運選單介面
├── mrt_menu_script.py             # 捷運站點選擇及人物移動
├── geocoding_service.py           # Nominatim 臺北地點搜尋
├── route_service.py               # OSRM 步行路線請求
├── result_service.py              # 結算面板組裝
├── result_panel_script.py         # 路線、距離、計分與結果呈現
├── result_panel_style.py          # 結算面板樣式
├── street_view_service.py         # 人物附近 Google 街景面板
├── templates/
│   ├── index.html                 # 首頁
│   ├── difficulty.html            # 難度及遊戲設定頁
│   └── rules.html                 # 遊戲規則頁
└── data/                          # 解壓縮後的邊界與建築物資料
```

## 常見問題

- **找不到 data/taipei_boundary.geojson**：確認已解壓縮 data.7z，且 data 資料夾與 web.py 同層。
- **建築物碰撞無資料或載入失敗**：確認建築物 GeoJSON／GeoPackage 已解壓縮。GeoPackage 需要 GeoPandas；首次使用時程式可能需要建立碰撞 JSON。
- **街景圖片或人物街景沒有顯示**：確認 .env 位於專案根目錄、變數名稱正確、金鑰有效，且 Google Cloud 已啟用對應 API 並允許目前的網域或本機 referrer。
- **搜尋或結算沒有結果**：確認網路連線，並稍後重試 Nominatim 或 OSRM；公開端點可能限流或暫時不可用。
- **pip install 找不到套件**：確認已啟用本專案的虛擬環境，並使用 python -m pip 安裝依賴。

## 專案與資料說明

本專案依課程期末專題提案實作，將題目、地圖、人物移動、碰撞、捷運、搜尋、街景及計分功能拆分成模組。地圖資料、Google Maps API、Nominatim 與 OSRM 均受各自的授權、服務條款、配額或使用限制約束；使用前請確認相應規範。