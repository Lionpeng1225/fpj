import json

import folium

from boundary_service import get_taipei_outer_rings
from building_collision_service import get_building_collision_json


TAIPEI_MAIN_STATION = {
    "name": "台北車站",
    "lat": 25.0462258,
    "lng": 121.5174848
}

ANSWER_RANGE_RADIUS_METERS = 100

# 每按一次方向鍵約移動 8～9 公尺
MOVE_STEP = 0.00008


def add_virtual_person(
    taipei_map,
    building_collision_enabled=True
):
    """
    加入虛擬人物。

    building_collision_enabled=True：
        人物不能穿越建築物。

    building_collision_enabled=False：
        不載入建築資料，人物可以穿越建築物。
    """

    outer_rings = get_taipei_outer_rings()

    outer_rings_json = json.dumps(
        outer_rings,
        ensure_ascii=False
    )

    if building_collision_enabled:
        building_collision_json = (
            get_building_collision_json()
        )
    else:
        building_collision_json = json.dumps(
            {
                "gridSize": 0.001,
                "buildings": [],
                "grid": {}
            },
            ensure_ascii=False
        )

    collision_enabled_json = (
        "true"
        if building_collision_enabled
        else "false"
    )

    collision_status_text = (
        "建築物阻擋：開啟"
        if building_collision_enabled
        else "建築物阻擋：關閉"
    )

    collision_status_class = (
        "enabled"
        if building_collision_enabled
        else "disabled"
    )

    person_html = """
    <div class="virtual-person-icon">
        🚶
    </div>
    """

    virtual_person_marker = folium.Marker(
        location=[
            TAIPEI_MAIN_STATION["lat"],
            TAIPEI_MAIN_STATION["lng"]
        ],
        popup="虛擬人物目前位置：台北車站",
        tooltip="虛擬人物",
        draggable=False,
        icon=folium.DivIcon(
            html=person_html,
            icon_size=(36, 36),
            icon_anchor=(18, 18),
            popup_anchor=(0, -18)
        )
    )

    virtual_person_marker.add_to(taipei_map)

    marker_name = virtual_person_marker.get_name()
    map_name = taipei_map.get_name()

    html = f"""
    <div
        id="building-collision-status"
        class="{collision_status_class}"
    >
        {collision_status_text}
    </div>

    <style>
        .virtual-person-icon {{
            width: 34px;
            height: 34px;
            border-radius: 50%;
            background-color: white;
            border: 3px solid #333333;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 22px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
            user-select: none;
        }}

        #building-collision-status {{
            position: fixed;
            left: 14px;
            bottom: 112px;
            z-index: 9998;
            padding: 8px 11px;
            border-radius: 10px;
            color: white;
            font-size: 13px;
            font-weight: bold;
            font-family: Arial, "Microsoft JhengHei", sans-serif;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
            pointer-events: none;
        }}

        #building-collision-status.enabled {{
            background-color: rgba(33, 136, 56, 0.92);
        }}

        #building-collision-status.disabled {{
            background-color: rgba(100, 100, 100, 0.92);
        }}
    </style>

    <script>
        (function() {{
            var moveStep = {MOVE_STEP};

            var answerRangeRadiusMeters =
                {ANSWER_RANGE_RADIUS_METERS};

            var taipeiOuterRings =
                {outer_rings_json};

            var buildingCollisionEnabled =
                {collision_enabled_json};

            var buildingCollisionData =
                {building_collision_json};

            window.buildingCollisionEnabled =
                buildingCollisionEnabled;

            window.buildingCollisionData =
                buildingCollisionData;

            function isPointInRing(
                lat,
                lng,
                ring
            ) {{
                var inside = false;
                var x = lng;
                var y = lat;

                for (
                    var i = 0, j = ring.length - 1;
                    i < ring.length;
                    j = i++
                ) {{
                    var yi = ring[i][0];
                    var xi = ring[i][1];
                    var yj = ring[j][0];
                    var xj = ring[j][1];

                    var intersects =
                        ((yi > y) !== (yj > y)) &&
                        (
                            x <
                            (
                                (xj - xi) *
                                (y - yi) /
                                (
                                    yj - yi +
                                    0.0000000001
                                )
                            ) + xi
                        );

                    if (intersects) {{
                        inside = !inside;
                    }}
                }}

                return inside;
            }}

            function isInsideTaipei(
                lat,
                lng
            ) {{
                for (
                    var index = 0;
                    index < taipeiOuterRings.length;
                    index++
                ) {{
                    if (
                        isPointInRing(
                            lat,
                            lng,
                            taipeiOuterRings[index]
                        )
                    ) {{
                        return true;
                    }}
                }}

                return false;
            }}

            function getGridIndex(
                value,
                gridSize
            ) {{
                return Math.floor(
                    value / gridSize
                );
            }}

            function getGridKey(
                latIndex,
                lngIndex
            ) {{
                return (
                    latIndex +
                    ":" +
                    lngIndex
                );
            }}

            function isInsideBuildingBBox(
                lat,
                lng,
                bbox
            ) {{
                if (
                    !bbox ||
                    bbox.length < 4
                ) {{
                    return false;
                }}

                return (
                    lat >= bbox[0] &&
                    lng >= bbox[1] &&
                    lat <= bbox[2] &&
                    lng <= bbox[3]
                );
            }}

            function getNearbyBuildingIndexes(
                lat,
                lng
            ) {{
                if (!buildingCollisionEnabled) {{
                    return [];
                }}

                if (
                    !buildingCollisionData ||
                    !buildingCollisionData.grid ||
                    !buildingCollisionData.buildings
                ) {{
                    return [];
                }}

                var gridSize =
                    buildingCollisionData.gridSize ||
                    0.001;

                var latIndex =
                    getGridIndex(
                        lat,
                        gridSize
                    );

                var lngIndex =
                    getGridIndex(
                        lng,
                        gridSize
                    );

                var indexMap = {{}};
                var result = [];

                for (
                    var dLat = -1;
                    dLat <= 1;
                    dLat++
                ) {{
                    for (
                        var dLng = -1;
                        dLng <= 1;
                        dLng++
                    ) {{
                        var key = getGridKey(
                            latIndex + dLat,
                            lngIndex + dLng
                        );

                        var indexes =
                            buildingCollisionData
                                .grid[key];

                        if (!indexes) {{
                            continue;
                        }}

                        for (
                            var i = 0;
                            i < indexes.length;
                            i++
                        ) {{
                            var buildingIndex =
                                indexes[i];

                            if (
                                !Object.prototype
                                    .hasOwnProperty
                                    .call(
                                        indexMap,
                                        buildingIndex
                                    )
                            ) {{
                                indexMap[
                                    buildingIndex
                                ] = true;

                                result.push(
                                    buildingIndex
                                );
                            }}
                        }}
                    }}
                }}

                return result;
            }}

            function isInsideBuilding(
                lat,
                lng
            ) {{
                if (!buildingCollisionEnabled) {{
                    return false;
                }}

                var buildingIndexes =
                    getNearbyBuildingIndexes(
                        lat,
                        lng
                    );

                var buildings =
                    buildingCollisionData
                        .buildings || [];

                for (
                    var i = 0;
                    i < buildingIndexes.length;
                    i++
                ) {{
                    var building =
                        buildings[
                            buildingIndexes[i]
                        ];

                    if (!building) {{
                        continue;
                    }}

                    if (
                        !isInsideBuildingBBox(
                            lat,
                            lng,
                            building.bbox
                        )
                    ) {{
                        continue;
                    }}

                    if (
                        building.ring &&
                        isPointInRing(
                            lat,
                            lng,
                            building.ring
                        )
                    ) {{
                        return true;
                    }}
                }}

                return false;
            }}

            function doesPathCrossBuilding(
                startLat,
                startLng,
                endLat,
                endLng
            ) {{
                if (!buildingCollisionEnabled) {{
                    return false;
                }}

                var latDifference =
                    endLat - startLat;

                var lngDifference =
                    endLng - startLng;

                var largestDifference =
                    Math.max(
                        Math.abs(
                            latDifference
                        ),
                        Math.abs(
                            lngDifference
                        )
                    );

                var pathCheckStep =
                    0.000015;

                var checkCount =
                    Math.max(
                        1,
                        Math.ceil(
                            largestDifference /
                            pathCheckStep
                        )
                    );

                for (
                    var index = 1;
                    index <= checkCount;
                    index++
                ) {{
                    var ratio =
                        index / checkCount;

                    var checkLat =
                        startLat +
                        latDifference * ratio;

                    var checkLng =
                        startLng +
                        lngDifference * ratio;

                    if (
                        isInsideBuilding(
                            checkLat,
                            checkLng
                        )
                    ) {{
                        return true;
                    }}
                }}

                return false;
            }}

            function setupVirtualPerson() {{
                if (
                    typeof {marker_name} ===
                    "undefined"
                ) {{
                    console.error(
                        "找不到虛擬人物標記"
                    );

                    return;
                }}

                if (
                    typeof {map_name} ===
                    "undefined"
                ) {{
                    console.error(
                        "找不到 Folium 地圖"
                    );

                    return;
                }}

                var virtualPersonMarker =
                    {marker_name};

                var map =
                    {map_name};

                var startLat =
                    {TAIPEI_MAIN_STATION["lat"]};

                var startLng =
                    {TAIPEI_MAIN_STATION["lng"]};

                window.virtualPersonMarker =
                    virtualPersonMarker;

                window.virtualPersonRangeRadiusMeters =
                    answerRangeRadiusMeters;

                var rangeCircle =
                    L.circle(
                        [
                            startLat,
                            startLng
                        ],
                        {{
                            radius:
                                answerRangeRadiusMeters,

                            color:
                                "#333333",

                            weight:
                                2,

                            fillColor:
                                "#3388ff",

                            fillOpacity:
                                0.12,

                            dashArray:
                                "6, 6",

                            interactive:
                                false
                        }}
                    ).addTo(map);

                window.virtualPersonRangeCircle =
                    rangeCircle;

                window.getVirtualPersonLatLng =
                    function() {{
                        return (
                            virtualPersonMarker
                                .getLatLng()
                        );
                    }};

                window.isInsideVirtualPersonRange =
                    function(lat, lng) {{
                        var personLatLng =
                            virtualPersonMarker
                                .getLatLng();

                        var targetLatLng =
                            L.latLng(
                                lat,
                                lng
                            );

                        var distance =
                            map.distance(
                                personLatLng,
                                targetLatLng
                            );

                        return (
                            distance <=
                            answerRangeRadiusMeters
                        );
                    }};

                window.isInsideTaipeiBoundary =
                    function(lat, lng) {{
                        return isInsideTaipei(
                            lat,
                            lng
                        );
                    }};

                window.isInsideBuilding =
                    function(lat, lng) {{
                        return isInsideBuilding(
                            lat,
                            lng
                        );
                    }};

                function showBoundaryWarning() {{
                    L.popup()
                        .setLatLng(
                            virtualPersonMarker
                                .getLatLng()
                        )
                        .setContent(
                            "虛擬人物不能移出台北市邊界"
                        )
                        .openOn(map);
                }}

                function showBuildingWarning() {{
                    L.popup()
                        .setLatLng(
                            virtualPersonMarker
                                .getLatLng()
                        )
                        .setContent(
                            "前方是建築物，虛擬人物不能穿越"
                        )
                        .openOn(map);
                }}

                function notifyPersonPositionChanged(
                    newLat,
                    newLng,
                    movementType
                ) {{
                    window.dispatchEvent(
                        new CustomEvent(
                            "virtualPersonMoved",
                            {{
                                detail: {{
                                    lat:
                                        newLat,

                                    lng:
                                        newLng,

                                    movementType:
                                        movementType ||
                                        "walking"
                                }}
                            }}
                        )
                    );

                    if (
                        typeof window
                            .updateMrtButtonState ===
                        "function"
                    ) {{
                        window
                            .updateMrtButtonState();
                    }}

                    if (
                        typeof window
                            .scheduleStreetViewUpdate ===
                        "function"
                    ) {{
                        window
                            .scheduleStreetViewUpdate();
                    }}

                    if (
                        window
                            .walkabilityLayerEnabled &&
                        typeof window
                            .scheduleWalkabilityRender ===
                            "function"
                    ) {{
                        window
                            .scheduleWalkabilityRender();
                    }}
                }}

                function applyVirtualPersonPosition(
                    newLat,
                    newLng,
                    options
                ) {{
                    options =
                        options || {{}};

                    virtualPersonMarker
                        .setLatLng([
                            newLat,
                            newLng
                        ]);

                    rangeCircle
                        .setLatLng([
                            newLat,
                            newLng
                        ]);

                    var popupText =
                        "虛擬人物目前位置<br>" +
                        "緯度：" +
                        newLat.toFixed(6) +
                        "<br>" +
                        "經度：" +
                        newLng.toFixed(6) +
                        "<br>" +
                        "作答範圍：" +
                        answerRangeRadiusMeters +
                        " 公尺<br>" +
                        (
                            buildingCollisionEnabled
                                ? "建築物阻擋：開啟"
                                : "建築物阻擋：關閉"
                        );

                    if (options.locationName) {{
                        popupText +=
                            "<br>目前地點：" +
                            options.locationName;
                    }}

                    virtualPersonMarker
                        .bindPopup(
                            popupText
                        );

                    if (options.openPopup) {{
                        virtualPersonMarker
                            .openPopup();
                    }}

                    if (
                        options.panMap !== false
                    ) {{
                        map.panTo(
                            [
                                newLat,
                                newLng
                            ],
                            {{
                                animate:
                                    true,

                                duration:
                                    0.15
                            }}
                        );
                    }}

                    notifyPersonPositionChanged(
                        newLat,
                        newLng,
                        options.movementType
                    );

                    return true;
                }}

                function moveVirtualPerson(
                    newLat,
                    newLng,
                    options
                ) {{
                    options =
                        options || {{}};

                    if (
                        !Number.isFinite(
                            newLat
                        ) ||
                        !Number.isFinite(
                            newLng
                        )
                    ) {{
                        return false;
                    }}

                    if (
                        !isInsideTaipei(
                            newLat,
                            newLng
                        )
                    ) {{
                        if (!options.silent) {{
                            showBoundaryWarning();
                        }}

                        return false;
                    }}

                    var currentLatLng =
                        virtualPersonMarker
                            .getLatLng();

                    if (
                        buildingCollisionEnabled &&
                        isInsideBuilding(
                            newLat,
                            newLng
                        )
                    ) {{
                        if (!options.silent) {{
                            showBuildingWarning();
                        }}

                        return false;
                    }}

                    if (
                        buildingCollisionEnabled &&
                        !options.skipPathCollision &&
                        doesPathCrossBuilding(
                            currentLatLng.lat,
                            currentLatLng.lng,
                            newLat,
                            newLng
                        )
                    ) {{
                        if (!options.silent) {{
                            showBuildingWarning();
                        }}

                        return false;
                    }}

                    return (
                        applyVirtualPersonPosition(
                            newLat,
                            newLng,
                            options
                        )
                    );
                }}

                window.moveVirtualPersonToLatLng =
                    function(
                        lat,
                        lng,
                        options
                    ) {{
                        return (
                            moveVirtualPerson(
                                Number(lat),
                                Number(lng),
                                options || {{}}
                            )
                        );
                    }};

                document.addEventListener(
                    "keydown",
                    function(event) {{
                        var key =
                            event.key;

                        if (
                            key !== "ArrowUp" &&
                            key !== "ArrowDown" &&
                            key !== "ArrowLeft" &&
                            key !== "ArrowRight"
                        ) {{
                            return;
                        }}

                        var activeElement =
                            document.activeElement;

                        if (
                            activeElement &&
                            (
                                activeElement
                                    .tagName ===
                                    "INPUT" ||

                                activeElement
                                    .tagName ===
                                    "TEXTAREA" ||

                                activeElement
                                    .tagName ===
                                    "SELECT" ||

                                activeElement
                                    .isContentEditable
                            )
                        ) {{
                            return;
                        }}

                        event.preventDefault();

                        var currentLatLng =
                            virtualPersonMarker
                                .getLatLng();

                        var newLat =
                            currentLatLng.lat;

                        var newLng =
                            currentLatLng.lng;

                        if (
                            key ===
                            "ArrowUp"
                        ) {{
                            newLat +=
                                moveStep;
                        }}

                        if (
                            key ===
                            "ArrowDown"
                        ) {{
                            newLat -=
                                moveStep;
                        }}

                        if (
                            key ===
                            "ArrowLeft"
                        ) {{
                            newLng -=
                                moveStep;
                        }}

                        if (
                            key ===
                            "ArrowRight"
                        ) {{
                            newLng +=
                                moveStep;
                        }}

                        moveVirtualPerson(
                            newLat,
                            newLng,
                            {{
                                movementType:
                                    "walking",

                                skipPathCollision:
                                    false,

                                panMap:
                                    true
                            }}
                        );
                    }}
                );

                notifyPersonPositionChanged(
                    startLat,
                    startLng,
                    "initial"
                );
            }}

            if (
                document.readyState ===
                "loading"
            ) {{
                document.addEventListener(
                    "DOMContentLoaded",
                    setupVirtualPerson
                );
            }} else {{
                setupVirtualPerson();
            }}
        }})();
    </script>
    """

    taipei_map.get_root().html.add_child(
        folium.Element(html)
    )