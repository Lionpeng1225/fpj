def get_result_panel_script(questions_json):
    """
    回傳結算畫面的 JavaScript。
    questions_json 會由 result_service.py 傳進來。
    """

    script = """
    <script>
        window.gameQuestionsForResult = __QUESTIONS_JSON__;
        window.resultMapInstance = null;
        window.resultMapLayers = [];

        function formatDistance(meters) {
            if (meters === null || meters === undefined) {
                return "無法計算";
            }

            if (meters < 1000) {
                return Math.round(meters) + " 公尺";
            }

            return (meters / 1000).toFixed(2) + " 公里";
        }

        function formatDuration(seconds) {
            if (seconds === null || seconds === undefined) {
                return "—";
            }

            var minutes = Math.round(seconds / 60);
            return minutes + " 分鐘";
        }

        function calculateScore(distanceMeters, hasAnswer) {
            if (!hasAnswer) {
                return 0;
            }

            if (distanceMeters === null || distanceMeters === undefined) {
                return 0;
            }

            var distanceKm = distanceMeters / 1000;
            var score = 100 - distanceKm * 10;

            if (score < 0) {
                score = 0;
            }

            return score;
        }

        function formatScore(score) {
            return score.toFixed(2);
        }

        function getDistanceClass(meters) {
            if (meters === null || meters === undefined) {
                return "missing-distance";
            }

            if (meters < 3000) {
                return "good-distance";
            }

            if (meters < 7000) {
                return "normal-distance";
            }

            return "bad-distance";
        }

        function getScoreClass(score) {
            if (score >= 80) {
                return "score-good";
            }

            if (score >= 50) {
                return "score-normal";
            }

            return "score-bad";
        }

        async function getOsrmDistance(startLat, startLng, endLat, endLng) {
            var url =
                "/api/route" +
                "?start_lat=" + encodeURIComponent(startLat) +
                "&start_lng=" + encodeURIComponent(startLng) +
                "&end_lat=" + encodeURIComponent(endLat) +
                "&end_lng=" + encodeURIComponent(endLng);

            try {
                var response = await fetch(url);
                var data = await response.json();

                if (!data.routes || data.routes.length === 0) {
                    return {
                        distance: null,
                        duration: null,
                        geometry: null
                    };
                }

                return {
                    distance: data.routes[0].distance,
                    duration: data.routes[0].duration,
                    geometry: data.routes[0].geometry
                };
            } catch (error) {
                console.log("OSRM calculation failed:", error);

                return {
                    distance: null,
                    duration: null,
                    geometry: null
                };
            }
        }

        function createPlayerIcon(questionNumber) {
            return L.divIcon({
                className: "",
                html:
                    '<div class="result-player-icon">' +
                    questionNumber +
                    '</div>',
                iconSize: [34, 34],
                iconAnchor: [17, 17],
                popupAnchor: [0, -18]
            });
        }

        function createAnswerIcon(questionNumber) {
            return L.divIcon({
                className: "",
                html:
                    '<div class="result-answer-icon">' +
                    questionNumber +
                    '</div>',
                iconSize: [34, 34],
                iconAnchor: [17, 17],
                popupAnchor: [0, -18]
            });
        }

        function clearResultMapLayers() {
            if (!window.resultMapInstance) {
                return;
            }

            for (var i = 0; i < window.resultMapLayers.length; i++) {
                window.resultMapInstance.removeLayer(window.resultMapLayers[i]);
            }

            window.resultMapLayers = [];
        }

        function initResultMap() {
            if (window.resultMapInstance) {
                window.resultMapInstance.remove();
                window.resultMapInstance = null;
            }

            window.resultMapInstance = L.map("result-map").setView(
                [25.068, 121.545],
                12
            );

            L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
                maxZoom: 19,
                attribution: "&copy; OpenStreetMap contributors"
            }).addTo(window.resultMapInstance);
        }

        function addLayerToResultMap(layer) {
            layer.addTo(window.resultMapInstance);
            window.resultMapLayers.push(layer);
        }

        function addAnswerOnlyToMap(questionNumber, question) {
            var answerLatLng = [question.lat, question.lng];

            var answerMarker = L.marker(answerLatLng, {
                icon: createAnswerIcon(questionNumber)
            }).bindPopup(
                "<b>第 " + questionNumber + " 題：實際地點</b><br>" +
                question.id + ". " + question.name + "<br>" +
                "玩家未作答<br>" +
                "得分：0.00 分<br>" +
                "座標：" + question.lat.toFixed(6) + ", " + question.lng.toFixed(6)
            );

            addLayerToResultMap(answerMarker);
        }

        function addQuestionResultToMap(questionNumber, question, marker, osrmResult, score) {
            var playerLatLng = [marker.lat, marker.lng];
            var answerLatLng = [question.lat, question.lng];

            var playerMarker = L.marker(playerLatLng, {
                icon: createPlayerIcon(questionNumber)
            }).bindPopup(
                "<b>第 " + questionNumber + " 題：玩家標記</b><br>" +
                question.id + ". " + question.name + "<br>" +
                "座標：" + marker.lat.toFixed(6) + ", " + marker.lng.toFixed(6) + "<br>" +
                "得分：" + formatScore(score) + " 分"
            );

            var answerMarker = L.marker(answerLatLng, {
                icon: createAnswerIcon(questionNumber)
            }).bindPopup(
                "<b>第 " + questionNumber + " 題：實際地點</b><br>" +
                question.id + ". " + question.name + "<br>" +
                "座標：" + question.lat.toFixed(6) + ", " + question.lng.toFixed(6)
            );

            addLayerToResultMap(playerMarker);
            addLayerToResultMap(answerMarker);

            if (
                osrmResult.geometry &&
                osrmResult.geometry.coordinates &&
                osrmResult.geometry.coordinates.length > 0
            ) {
                var routeLatLngs = osrmResult.geometry.coordinates.map(function(coord) {
                    return [coord[1], coord[0]];
                });

                var routeLine = L.polyline(routeLatLngs, {
                    color: "#ff7f0e",
                    weight: 4,
                    opacity: 0.8
                }).bindPopup(
                    "第 " + questionNumber + " 題 OSRM 步行路線<br>" +
                    "距離：" + formatDistance(osrmResult.distance) + "<br>" +
                    "時間：" + formatDuration(osrmResult.duration) + "<br>" +
                    "得分：" + formatScore(score) + " 分"
                );

                addLayerToResultMap(routeLine);
            } else {
                var straightLine = L.polyline([playerLatLng, answerLatLng], {
                    color: "#ff7f0e",
                    weight: 3,
                    opacity: 0.7,
                    dashArray: "6, 8"
                }).bindPopup(
                    "第 " + questionNumber + " 題兩點連線<br>" +
                    "OSRM 無法計算路線<br>" +
                    "得分：0.00 分"
                );

                addLayerToResultMap(straightLine);
            }
        }

        function fitResultMapToLayers() {
            if (!window.resultMapInstance || window.resultMapLayers.length === 0) {
                return;
            }

            var group = L.featureGroup(window.resultMapLayers);
            window.resultMapInstance.fitBounds(group.getBounds().pad(0.15));
        }

        window.showGameResult = async function() {
            var questions = window.gameQuestionsForResult || [];
            var markerData = {};

            if (typeof window.getMarkerDataForResult === "function") {
                markerData = window.getMarkerDataForResult();
            }

            document.getElementById("result-overlay").style.display = "flex";
            document.getElementById("result-loading").style.display = "block";
            document.getElementById("result-summary").innerHTML = "";
            document.getElementById("result-list").innerHTML = "";

            setTimeout(function() {
                initResultMap();
            }, 50);

            await new Promise(function(resolve) {
                setTimeout(resolve, 120);
            });

            clearResultMapLayers();

            var answeredCount = 0;
            var totalScore = 0;
            var totalPossibleScore = questions.length * 100;
            var resultListHtml = "";

            for (var i = 0; i < questions.length; i++) {
                var question = questions[i];
                var questionNumber = i + 1;
                var marker = markerData[questionNumber];

                if (marker) {
                    answeredCount++;

                    var osrmResult = await getOsrmDistance(
                        marker.lat,
                        marker.lng,
                        question.lat,
                        question.lng
                    );

                    var distance = osrmResult.distance;
                    var duration = osrmResult.duration;
                    var score = calculateScore(distance, true);

                    totalScore += score;

                    addQuestionResultToMap(
                        questionNumber,
                        question,
                        marker,
                        osrmResult,
                        score
                    );

                    resultListHtml +=
                        '<div class="result-item">' +
                            '<div class="result-question-number">第 ' + questionNumber + ' 題</div>' +
                            '<div class="result-question-name">' +
                                question.id + '. ' + question.name +
                            '</div>' +
                            '<div class="result-distance ' + getDistanceClass(distance) + '">' +
                                formatDistance(distance) +
                            '</div>' +
                            '<div class="result-duration">' +
                                formatDuration(duration) +
                            '</div>' +
                            '<div class="result-score ' + getScoreClass(score) + '">' +
                                formatScore(score) + ' 分' +
                            '</div>' +
                        '</div>';
                } else {
                    var missingScore = 0;
                    totalScore += missingScore;

                    addAnswerOnlyToMap(questionNumber, question);

                    resultListHtml +=
                        '<div class="result-item">' +
                            '<div class="result-question-number">第 ' + questionNumber + ' 題</div>' +
                            '<div class="result-question-name">' +
                                question.id + '. ' + question.name +
                            '</div>' +
                            '<div class="result-distance missing-distance">尚未作答</div>' +
                            '<div class="result-duration missing-distance">—</div>' +
                            '<div class="result-score score-missing">0.00 分</div>' +
                        '</div>';
                }

                document.getElementById("result-list").innerHTML = resultListHtml;
            }

            fitResultMapToLayers();

            var averageScore = questions.length > 0
                ? totalScore / questions.length
                : 0;

            document.getElementById("result-summary").innerHTML =
                '<div class="summary-card">' +
                    '<div class="number">' + questions.length + '</div>' +
                    '<div class="label">總題數</div>' +
                '</div>' +
                '<div class="summary-card">' +
                    '<div class="number">' + answeredCount + '</div>' +
                    '<div class="label">已標記題數</div>' +
                '</div>' +
                '<div class="summary-card">' +
                    '<div class="number">' + formatScore(totalScore) + ' / ' + totalPossibleScore + '</div>' +
                    '<div class="label">總分</div>' +
                '</div>' +
                '<div class="summary-card">' +
                    '<div class="number">' + formatScore(averageScore) + '</div>' +
                    '<div class="label">平均分數</div>' +
                '</div>';

            document.getElementById("result-loading").style.display = "none";

            setTimeout(function() {
                if (window.resultMapInstance) {
                    window.resultMapInstance.invalidateSize();
                    fitResultMapToLayers();
                }
            }, 200);
        };
    </script>
    """

    return script.replace("__QUESTIONS_JSON__", questions_json)