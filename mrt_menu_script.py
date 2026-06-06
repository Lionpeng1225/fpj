# mrt_menu_script.py


def get_mrt_menu_script(mrt_menu_json, mrt_transfer_json, map_name):
    """
    回傳捷運選單互動 JavaScript。

    功能：
    1. 檢查虛擬人物 100 公尺範圍內是否有捷運站
    2. 沒有捷運站時，使用捷運按鈕不可用
    3. 五條路線都顯示，但不可用路線會變淡、不能展開
    4. 可用路線可以展開
    5. 點擊站名後，虛擬人物會移動到該站
    """

    script = """
    <script>
        window.mrtMenuData = __MRT_MENU_JSON__;
        window.mrtTransferData = __MRT_TRANSFER_JSON__;
        window.canUseMrt = false;
        window.nearbyMrtStations = [];
        window.availableMrtLines = [];
        window.mrtOpenLineStates = {};
        window.lastAvailableMrtLinesKey = "";

        function getMrtMapInstance() {
            if (typeof __MAP_NAME__ !== "undefined") {
                return __MAP_NAME__;
            }

            return null;
        }

        function getAllMrtStationsForMenu() {
            var stations = [];

            for (var lineName in window.mrtMenuData) {
                if (!window.mrtMenuData.hasOwnProperty(lineName)) {
                    continue;
                }

                var line = window.mrtMenuData[lineName];

                for (var i = 0; i < line.stations.length; i++) {
                    var station = line.stations[i];

                    stations.push({
                        lineName: lineName,
                        lineColor: line.color,
                        code: station.code,
                        name: station.name,
                        lat: station.lat,
                        lng: station.lng
                    });
                }
            }

            return stations;
        }

        function findNearbyMrtStations() {
            var map = getMrtMapInstance();

            if (!map) {
                return [];
            }

            if (
                typeof window.getVirtualPersonLatLng !== "function" ||
                typeof window.virtualPersonRangeRadiusMeters === "undefined"
            ) {
                return [];
            }

            var personLatLng = window.getVirtualPersonLatLng();
            var radiusMeters = window.virtualPersonRangeRadiusMeters;
            var allStations = getAllMrtStationsForMenu();
            var nearbyStations = [];

            for (var i = 0; i < allStations.length; i++) {
                var station = allStations[i];
                var stationLatLng = L.latLng(station.lat, station.lng);
                var distance = map.distance(personLatLng, stationLatLng);

                if (distance <= radiusMeters) {
                    station.distance = distance;
                    nearbyStations.push(station);
                }
            }

            nearbyStations.sort(function(a, b) {
                return a.distance - b.distance;
            });

            return nearbyStations;
        }

        function getAvailableMrtLinesFromNearbyStations(nearbyStations) {
            var lineMap = {};
            var lines = [];

            for (var i = 0; i < nearbyStations.length; i++) {
                var station = nearbyStations[i];

                if (!lineMap[station.lineName]) {
                    lineMap[station.lineName] = true;
                    lines.push(station.lineName);
                }
            }

            return lines;
        }

        function getAvailableLinesKey(lines) {
            return lines.slice().sort().join("|");
        }

        function isLineAvailable(lineName) {
            for (var i = 0; i < window.availableMrtLines.length; i++) {
                if (window.availableMrtLines[i] === lineName) {
                    return true;
                }
            }

            return false;
        }

        function updateMrtButtonState() {
            var button = document.getElementById("mrt-menu-button");
            var panel = document.getElementById("mrt-menu-panel");

            if (!button) {
                return;
            }

            var nearbyStations = findNearbyMrtStations();
            var availableLines = getAvailableMrtLinesFromNearbyStations(nearbyStations);
            var newAvailableLinesKey = getAvailableLinesKey(availableLines);
            var availableLinesChanged = newAvailableLinesKey !== window.lastAvailableMrtLinesKey;

            window.nearbyMrtStations = nearbyStations;
            window.availableMrtLines = availableLines;
            window.canUseMrt = nearbyStations.length > 0;

            if (window.canUseMrt) {
                button.classList.remove("disabled");
                button.innerText = "使用捷運";
            } else {
                button.classList.add("disabled");
                button.innerText = "附近無捷運站";

                if (panel) {
                    panel.style.display = "none";
                }
            }

            window.lastAvailableMrtLinesKey = newAvailableLinesKey;

            if (availableLinesChanged) {
                rerenderMrtMenuIfOpen();
            }
        }

        function moveVirtualPersonToMrtStation(lat, lng, stationCode, stationName) {
            var map = getMrtMapInstance();

            if (!map) {
                return;
            }

            if (typeof window.virtualPersonMarker === "undefined") {
                return;
            }

            window.virtualPersonMarker.setLatLng([lat, lng]);

            if (typeof window.virtualPersonRangeCircle !== "undefined") {
                window.virtualPersonRangeCircle.setLatLng([lat, lng]);
            }

            window.virtualPersonMarker.bindPopup(
                "虛擬人物目前位置<br>" +
                stationCode + " " + stationName
            );

            map.panTo([lat, lng], {
                animate: true,
                duration: 0.25
            });

            setTimeout(function() {
                updateMrtButtonState();
                renderMrtMenu();
            }, 80);
        }

        function toggleMrtMenu() {
            updateMrtButtonState();

            if (!window.canUseMrt) {
                return;
            }

            var panel = document.getElementById("mrt-menu-panel");

            if (!panel) {
                return;
            }

            if (panel.style.display === "none" || panel.style.display === "") {
                panel.style.display = "block";
                renderMrtMenu();
            } else {
                panel.style.display = "none";
            }
        }

        function closeMrtMenu() {
            var panel = document.getElementById("mrt-menu-panel");

            if (panel) {
                panel.style.display = "none";
            }
        }

        function toggleMrtLine(lineId, lineName) {
            if (!isLineAvailable(lineName)) {
                return;
            }

            var list = document.getElementById(lineId);
            var arrow = document.getElementById(lineId + "-arrow");

            if (!list) {
                return;
            }

            var willOpen = list.style.display === "none" || list.style.display === "";

            if (willOpen) {
                list.style.display = "block";
                window.mrtOpenLineStates[lineName] = true;

                if (arrow) {
                    arrow.innerText = "▲";
                }
            } else {
                list.style.display = "none";
                window.mrtOpenLineStates[lineName] = false;

                if (arrow) {
                    arrow.innerText = "▼";
                }
            }
        }

        function getTransferDotsHtml(lineName, stationCode) {
            var key = lineName + "|" + stationCode;
            var transfers = window.mrtTransferData[key];

            if (!transfers || transfers.length === 0) {
                return "";
            }

            var html = '<span class="mrt-transfer-dots">';

            for (var i = 0; i < transfers.length; i++) {
                html +=
                    '<span class="mrt-transfer-dot" ' +
                    'title="可轉乘：' + transfers[i].line + '" ' +
                    'style="background-color:' + transfers[i].color + ';">' +
                    '</span>';
            }

            html += '</span>';

            return html;
        }

        function escapeSingleQuote(text) {
            return String(text).replace(/'/g, "\\\\'");
        }

        function renderMrtMenu() {
            var content = document.getElementById("mrt-menu-content");

            if (!content) {
                return;
            }

            var html = "";
            var lineIndex = 0;

            for (var lineName in window.mrtMenuData) {
                if (!window.mrtMenuData.hasOwnProperty(lineName)) {
                    continue;
                }

                var line = window.mrtMenuData[lineName];
                var lineId = "mrt-line-" + lineIndex;
                var available = isLineAvailable(lineName);
                var blockClass = available ? "mrt-line-block" : "mrt-line-block unavailable";
                var isOpen = available && window.mrtOpenLineStates[lineName] === true;
                var arrowText = available ? (isOpen ? "▲" : "▼") : "不可用";
                var listDisplay = isOpen ? "block" : "none";

                html += '<div class="' + blockClass + '">';

                html +=
                    '<button class="mrt-line-title" onclick="toggleMrtLine(\\'' + lineId + '\\', \\'' + lineName + '\\')">' +
                        '<span class="mrt-line-left">' +
                            '<span class="mrt-line-color" style="background-color:' + line.color + ';"></span>' +
                            '<span>' + lineName + '</span>' +
                        '</span>' +
                        '<span id="' + lineId + '-arrow">' + arrowText + '</span>' +
                    '</button>';

                html += '<div class="mrt-station-list" id="' + lineId + '" style="display:' + listDisplay + ';">';

                for (var i = 0; i < line.stations.length; i++) {
                    var station = line.stations[i];
                    var transferDotsHtml = getTransferDotsHtml(lineName, station.code);

                    html +=
                        '<div class="mrt-station-item" ' +
                            'onclick="moveVirtualPersonToMrtStation(' +
                                station.lat + ', ' +
                                station.lng + ', ' +
                                '\\'' + escapeSingleQuote(station.code) + '\\', ' +
                                '\\'' + escapeSingleQuote(station.name) + '\\'' +
                            ')">' +
                            '<span class="mrt-station-code">' + station.code + '</span>' +
                            '<span class="mrt-station-name">' + station.name + '</span>' +
                            transferDotsHtml +
                        '</div>';
                }

                html += '</div>';
                html += '</div>';

                lineIndex++;
            }

            content.innerHTML = html;
        }

        function rerenderMrtMenuIfOpen() {
            var panel = document.getElementById("mrt-menu-panel");

            if (!panel) {
                return;
            }

            if (panel.style.display === "block") {
                renderMrtMenu();
            }
        }

        function startMrtButtonWatcher() {
            updateMrtButtonState();

            setInterval(function() {
                updateMrtButtonState();
            }, 200);
        }

        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", startMrtButtonWatcher);
        } else {
            startMrtButtonWatcher();
        }
    </script>
    """

    script = script.replace("__MRT_MENU_JSON__", mrt_menu_json)
    script = script.replace("__MRT_TRANSFER_JSON__", mrt_transfer_json)
    script = script.replace("__MAP_NAME__", map_name)

    return script