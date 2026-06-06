import folium


def add_walkability_layer(taipei_map):
    """
    在地圖上加入「可走 / 不可走」視覺化圖層。

    顯示方式：
    1. 紅色半透明建築物 = 不能走
    2. 台北市邊界內，沒有紅色建築物的位置 = 可以走
    3. 為了避免卡頓，只在地圖放大到 zoom >= 16 時顯示目前畫面內的建築物
    """

    map_name = taipei_map.get_name()

    html = f"""
    <button id="walkability-toggle-button" onclick="toggleWalkabilityLayer()">
        顯示可走範圍
    </button>

    <div id="walkability-legend" style="display: none;">
        <div class="walkability-title">行走範圍說明</div>

        <div class="walkability-row">
            <span class="walkability-color blocked"></span>
            <span>紅色建築物：不能走</span>
        </div>

        <div class="walkability-row">
            <span class="walkability-color walkable"></span>
            <span>沒有紅色覆蓋：可走</span>
        </div>

        <div id="walkability-status">
            請放大地圖查看建築物
        </div>
    </div>

    <style>
        #walkability-toggle-button {{
            position: fixed;
            right: 16px;
            bottom: 310px;
            z-index: 10001;
            padding: 10px 14px;
            border: none;
            border-radius: 12px;
            background-color: #222222;
            color: white;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 3px 12px rgba(0, 0, 0, 0.30);
            font-family: Arial, "Microsoft JhengHei", sans-serif;
        }}

        #walkability-toggle-button:hover {{
            background-color: #000000;
        }}

        #walkability-toggle-button.active {{
            background-color: #d93025;
        }}

        #walkability-legend {{
            position: fixed;
            right: 16px;
            bottom: 360px;
            z-index: 10001;
            width: 230px;
            padding: 12px;
            background-color: rgba(255, 255, 255, 0.96);
            border-radius: 14px;
            box-shadow: 0 3px 14px rgba(0, 0, 0, 0.28);
            font-family: Arial, "Microsoft JhengHei", sans-serif;
            box-sizing: border-box;
        }}

        .walkability-title {{
            font-size: 15px;
            font-weight: bold;
            margin-bottom: 8px;
        }}

        .walkability-row {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            margin-bottom: 7px;
            color: #333333;
        }}

        .walkability-color {{
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 1px solid #777777;
            display: inline-block;
            flex-shrink: 0;
        }}

        .walkability-color.blocked {{
            background-color: rgba(217, 48, 37, 0.45);
            border-color: #d93025;
        }}

        .walkability-color.walkable {{
            background-color: rgba(46, 160, 67, 0.20);
            border-color: #2ea043;
        }}

        #walkability-status {{
            margin-top: 8px;
            padding: 8px;
            background-color: #f1f3f5;
            border-radius: 8px;
            color: #444444;
            font-size: 12px;
            line-height: 1.4;
        }}

        @media (max-width: 780px) {{
            #walkability-toggle-button {{
                right: 10px;
                bottom: 270px;
            }}

            #walkability-legend {{
                right: 10px;
                bottom: 318px;
                width: 220px;
            }}
        }}
    </style>

    <script>
        window.walkabilityLayerEnabled = false;
        window.walkabilityLayerGroup = null;
        window.walkabilityCanvasRenderer = null;
        window.walkabilityRenderTimer = null;

        function getWalkabilityMap() {{
            if (typeof {map_name} !== "undefined") {{
                return {map_name};
            }}

            return null;
        }}

        function setWalkabilityStatus(message) {{
            var statusElement = document.getElementById("walkability-status");

            if (statusElement) {{
                statusElement.innerText = message;
            }}
        }}

        function getWalkabilityCollisionData() {{
            if (window.buildingCollisionData) {{
                return window.buildingCollisionData;
            }}

            return null;
        }}

        function clearWalkabilityLayer() {{
            if (window.walkabilityLayerGroup) {{
                window.walkabilityLayerGroup.clearLayers();
            }}
        }}

        function getGridIndex(value, gridSize) {{
            return Math.floor(value / gridSize);
        }}

        function getGridKey(latIndex, lngIndex) {{
            return latIndex + ":" + lngIndex;
        }}

        function bboxIntersectsBounds(bbox, bounds) {{
            var minLat = bbox[0];
            var minLng = bbox[1];
            var maxLat = bbox[2];
            var maxLng = bbox[3];

            var south = bounds.getSouth();
            var north = bounds.getNorth();
            var west = bounds.getWest();
            var east = bounds.getEast();

            if (maxLat < south) {{
                return false;
            }}

            if (minLat > north) {{
                return false;
            }}

            if (maxLng < west) {{
                return false;
            }}

            if (minLng > east) {{
                return false;
            }}

            return true;
        }}

        function getBuildingIndexesInCurrentBounds(bounds, collisionData) {{
            var gridSize = collisionData.gridSize || 0.001;
            var grid = collisionData.grid || {{}};

            var south = bounds.getSouth();
            var north = bounds.getNorth();
            var west = bounds.getWest();
            var east = bounds.getEast();

            var minLatIndex = getGridIndex(south, gridSize);
            var maxLatIndex = getGridIndex(north, gridSize);
            var minLngIndex = getGridIndex(west, gridSize);
            var maxLngIndex = getGridIndex(east, gridSize);

            var indexMap = {{}};
            var result = [];

            for (var latIndex = minLatIndex; latIndex <= maxLatIndex; latIndex++) {{
                for (var lngIndex = minLngIndex; lngIndex <= maxLngIndex; lngIndex++) {{
                    var key = getGridKey(latIndex, lngIndex);
                    var indexes = grid[key];

                    if (!indexes) {{
                        continue;
                    }}

                    for (var i = 0; i < indexes.length; i++) {{
                        var buildingIndex = indexes[i];

                        if (!indexMap[buildingIndex]) {{
                            indexMap[buildingIndex] = true;
                            result.push(buildingIndex);
                        }}
                    }}
                }}
            }}

            return result;
        }}

        function drawBuildingPolygon(map, building) {{
            if (!building || !building.ring || building.ring.length < 4) {{
                return;
            }}

            var polygon = L.polygon(building.ring, {{
                color: "#d93025",
                weight: 1,
                opacity: 0.75,
                fillColor: "#d93025",
                fillOpacity: 0.38,
                interactive: false,
                renderer: window.walkabilityCanvasRenderer
            }});

            window.walkabilityLayerGroup.addLayer(polygon);
        }}

        function renderWalkabilityLayer() {{
            if (!window.walkabilityLayerEnabled) {{
                return;
            }}

            var map = getWalkabilityMap();

            if (!map) {{
                return;
            }}

            var collisionData = getWalkabilityCollisionData();

            if (
                !collisionData ||
                !collisionData.buildings ||
                !collisionData.grid
            ) {{
                setWalkabilityStatus(
                    "找不到建築物碰撞資料，請先確認 building_collision_service.py 是否已接上"
                );
                return;
            }}

            if (!window.walkabilityLayerGroup) {{
                window.walkabilityLayerGroup = L.layerGroup().addTo(map);
            }}

            if (!window.walkabilityCanvasRenderer) {{
                window.walkabilityCanvasRenderer = L.canvas({{
                    padding: 0.5
                }});
            }}

            clearWalkabilityLayer();

            if (map.getZoom() < 16) {{
                setWalkabilityStatus(
                    "請把地圖放大到 16 級以上，才會顯示詳細建築物範圍"
                );
                return;
            }}

            var bounds = map.getBounds();
            var buildingIndexes = getBuildingIndexesInCurrentBounds(
                bounds,
                collisionData
            );

            var buildings = collisionData.buildings;
            var drawnCount = 0;
            var maxDrawCount = 2200;

            for (var i = 0; i < buildingIndexes.length; i++) {{
                if (drawnCount >= maxDrawCount) {{
                    break;
                }}

                var building = buildings[buildingIndexes[i]];

                if (!building) {{
                    continue;
                }}

                if (!bboxIntersectsBounds(building.bbox, bounds)) {{
                    continue;
                }}

                drawBuildingPolygon(map, building);
                drawnCount++;
            }}

            if (buildingIndexes.length > maxDrawCount) {{
                setWalkabilityStatus(
                    "目前畫面建築物太多，已先顯示 " +
                    maxDrawCount +
                    " 棟。可以再放大查看更細範圍。"
                );
            }} else {{
                setWalkabilityStatus(
                    "目前畫面顯示 " +
                    drawnCount +
                    " 棟不可通行建築物。紅色區域不能走，其餘道路與空地可走。"
                );
            }}
        }}

        function scheduleWalkabilityRender() {{
            if (!window.walkabilityLayerEnabled) {{
                return;
            }}

            if (window.walkabilityRenderTimer) {{
                clearTimeout(window.walkabilityRenderTimer);
            }}

            window.walkabilityRenderTimer = setTimeout(function() {{
                renderWalkabilityLayer();
            }}, 180);
        }}

        function toggleWalkabilityLayer() {{
            var map = getWalkabilityMap();
            var button = document.getElementById("walkability-toggle-button");
            var legend = document.getElementById("walkability-legend");

            if (!map) {{
                return;
            }}

            window.walkabilityLayerEnabled = !window.walkabilityLayerEnabled;

            if (window.walkabilityLayerEnabled) {{
                if (button) {{
                    button.classList.add("active");
                    button.innerText = "隱藏可走範圍";
                }}

                if (legend) {{
                    legend.style.display = "block";
                }}

                if (!window.walkabilityLayerGroup) {{
                    window.walkabilityLayerGroup = L.layerGroup().addTo(map);
                }}

                renderWalkabilityLayer();
            }} else {{
                if (button) {{
                    button.classList.remove("active");
                    button.innerText = "顯示可走範圍";
                }}

                if (legend) {{
                    legend.style.display = "none";
                }}

                clearWalkabilityLayer();
            }}
        }}

        function setupWalkabilityLayerEvents() {{
            var map = getWalkabilityMap();

            if (!map) {{
                return;
            }}

            map.on("moveend", scheduleWalkabilityRender);
            map.on("zoomend", scheduleWalkabilityRender);
        }}

        if (document.readyState === "loading") {{
            document.addEventListener("DOMContentLoaded", setupWalkabilityLayerEvents);
        }} else {{
            setupWalkabilityLayerEvents();
        }}
    </script>
    """

    taipei_map.get_root().html.add_child(folium.Element(html))