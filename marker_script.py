def get_marker_script(map_name, outer_rings_json):
    """
    回傳地圖點擊標記 JavaScript。

    功能：
    1. 只能在台北市藍色邊界內標記
    2. 只能在虛擬人物圓形範圍內標記
    3. 每一題都有自己的藍色標記
    4. 標記上顯示題號
    5. Enter 固定 / 解除固定目前題目的標記
    6. Backspace 刪除目前題目的標記
    7. 切換題目時不會自動跳到標記位置
    8. 點地圖新增標記時不顯示題目圖片
    9. 提供 window.getMarkerDataForResult() 給結算畫面使用
    """

    script = """
    <script>
        (function() {
            function isPointInRing(lat, lng, ring) {
                var inside = false;
                var x = lng;
                var y = lat;

                for (var i = 0, j = ring.length - 1; i < ring.length; j = i++) {
                    var yi = ring[i][0];
                    var xi = ring[i][1];
                    var yj = ring[j][0];
                    var xj = ring[j][1];

                    var intersects = ((yi > y) !== (yj > y)) &&
                        (x < (xj - xi) * (y - yi) / (yj - yi + 0.0000000001) + xi);

                    if (intersects) {
                        inside = !inside;
                    }
                }

                return inside;
            }

            function isInsideTaipei(lat, lng) {
                var taipeiRings = __OUTER_RINGS_JSON__;

                for (var index = 0; index < taipeiRings.length; index++) {
                    if (isPointInRing(lat, lng, taipeiRings[index])) {
                        return true;
                    }
                }

                return false;
            }

            function isInsideAnswerRange(lat, lng) {
                if (typeof window.isInsideVirtualPersonRange !== "function") {
                    return true;
                }

                return window.isInsideVirtualPersonRange(lat, lng);
            }

            function getCurrentQuestionNumber() {
                if (typeof window.getCurrentQuestionNumber === "function") {
                    return window.getCurrentQuestionNumber();
                }

                var questionNumberElement =
                    document.getElementById("current-question-number");

                if (questionNumberElement) {
                    return parseInt(questionNumberElement.innerText, 10);
                }

                return 1;
            }

            function createNumberMarkerIcon(questionNumber, isLocked) {
                var lockClass = isLocked ? " locked" : "";

                return L.divIcon({
                    className: "",
                    html:
                        '<div class="game-marker-icon' + lockClass + '">' +
                        questionNumber +
                        '</div>',
                    iconSize: [36, 36],
                    iconAnchor: [18, 18],
                    popupAnchor: [0, -18]
                });
            }

            function enableClickMarker() {
                if (typeof __MAP_NAME__ === "undefined") {
                    return;
                }

                var map = __MAP_NAME__;

                if (!window.taipeiGameMarkers) {
                    window.taipeiGameMarkers = {};
                }

                var markers = window.taipeiGameMarkers;

                function updateMarkerData(questionNumber) {
                    if (!markers[questionNumber]) {
                        return;
                    }

                    var latlng = markers[questionNumber].marker.getLatLng();

                    markers[questionNumber].lat = latlng.lat;
                    markers[questionNumber].lng = latlng.lng;
                }

                function updateMarkerIcon(questionNumber) {
                    if (!markers[questionNumber]) {
                        return;
                    }

                    markers[questionNumber].marker.setIcon(
                        createNumberMarkerIcon(
                            questionNumber,
                            markers[questionNumber].locked
                        )
                    );
                }

                function showCenterPopup(message) {
                    L.popup()
                        .setLatLng(map.getCenter())
                        .setContent(message)
                        .openOn(map);
                }

                window.getMarkerDataForResult = function() {
                    var result = {};

                    for (var questionNumber in markers) {
                        if (markers.hasOwnProperty(questionNumber)) {
                            updateMarkerData(questionNumber);

                            result[questionNumber] = {
                                lat: markers[questionNumber].lat,
                                lng: markers[questionNumber].lng,
                                locked: markers[questionNumber].locked
                            };
                        }
                    }

                    return result;
                };

                map.on("click", function(event) {
                    var lat = event.latlng.lat;
                    var lng = event.latlng.lng;
                    var questionNumber = getCurrentQuestionNumber();

                    if (!isInsideTaipei(lat, lng)) {
                        L.popup()
                            .setLatLng([lat, lng])
                            .setContent("請點選台北市藍色邊界範圍內的位置")
                            .openOn(map);

                        return;
                    }

                    if (!isInsideAnswerRange(lat, lng)) {
                        L.popup()
                            .setLatLng([lat, lng])
                            .setContent("棋子只能放在虛擬人物周圍的圓形範圍內")
                            .openOn(map);

                        return;
                    }

                    if (
                        markers[questionNumber] &&
                        markers[questionNumber].locked
                    ) {
                        L.popup()
                            .setLatLng([lat, lng])
                            .setContent(
                                "第 " + questionNumber + " 題的標記已固定<br>" +
                                "如果要重新標記，請先按 Enter 解除固定"
                            )
                            .openOn(map);

                        return;
                    }

                    if (!markers[questionNumber]) {
                        var marker = L.marker([lat, lng], {
                            icon: createNumberMarkerIcon(questionNumber, false)
                        }).addTo(map);

                        markers[questionNumber] = {
                            marker: marker,
                            lat: lat,
                            lng: lng,
                            locked: false
                        };
                    } else {
                        markers[questionNumber].marker.setLatLng([lat, lng]);
                        markers[questionNumber].lat = lat;
                        markers[questionNumber].lng = lng;
                    }

                    updateMarkerData(questionNumber);
                });

                document.addEventListener("keydown", function(event) {
                    var questionNumber = getCurrentQuestionNumber();

                    if (event.key === "Enter") {
                        if (!markers[questionNumber]) {
                            showCenterPopup(
                                "第 " + questionNumber + " 題還沒有標記<br>" +
                                "請先在地圖上點一下"
                            );

                            return;
                        }

                        markers[questionNumber].locked =
                            !markers[questionNumber].locked;

                        updateMarkerIcon(questionNumber);
                        updateMarkerData(questionNumber);

                        if (markers[questionNumber].locked) {
                            showCenterPopup(
                                "第 " + questionNumber + " 題標記已固定"
                            );
                        } else {
                            showCenterPopup(
                                "第 " + questionNumber + " 題標記已解除固定"
                            );
                        }

                        return;
                    }

                    if (event.key === "Backspace") {
                        event.preventDefault();

                        if (!markers[questionNumber]) {
                            showCenterPopup(
                                "第 " + questionNumber + " 題目前沒有標記可以刪除"
                            );

                            return;
                        }

                        map.removeLayer(markers[questionNumber].marker);
                        delete markers[questionNumber];

                        showCenterPopup(
                            "已刪除第 " + questionNumber + " 題的標記"
                        );

                        return;
                    }
                });
            }

            if (document.readyState === "loading") {
                document.addEventListener("DOMContentLoaded", enableClickMarker);
            } else {
                enableClickMarker();
            }
        })();
    </script>
    """

    script = script.replace("__MAP_NAME__", map_name)
    script = script.replace("__OUTER_RINGS_JSON__", outer_rings_json)

    return script