import folium
import os
from dotenv import load_dotenv

# 請換成你自己的 Google Maps JavaScript API Key
# 注意：
# 1. 這個功能需要啟用 Maps JavaScript API
# 2. 建議不要把真正的 API Key 放到公開 GitHub
#GOOGLE_MAPS_JAVASCRIPT_API_KEY = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
load_dotenv()
GOOGLE_MAPS_JAVASCRIPT_API_KEY= os.getenv("GOOGLE_STREET_VIEW_API_KEY")


def add_street_view_panel(taipei_map):
    """
    右下角人物所在地街景面板。

    功能：
    1. 顯示虛擬人物目前所在地附近的 Google 街景
    2. 可以用滑鼠拖曳旋轉視角
    3. 人物移動後，街景會自動更新
    4. 若附近沒有街景，會顯示提示
    5. 可收合右下角面板
    """

    html = f"""
    <div id="street-view-panel">
        <div id="street-view-header">
            <span>人物周圍街景</span>
            <button id="street-view-collapse-button" onclick="toggleStreetViewPanel()">
                －
            </button>
        </div>

        <div id="street-view-body">
            <div id="street-view-box"></div>
            <div id="street-view-status">
                正在載入人物所在地街景...
            </div>
        </div>
    </div>

    <style>
        #street-view-panel {{
            position: fixed;
            right: 16px;
            bottom: 16px;
            width: 340px;
            height: 280px;
            z-index: 9998;
            background-color: white;
            border-radius: 16px;
            box-shadow: 0 4px 18px rgba(0, 0, 0, 0.32);
            overflow: hidden;
            font-family: Arial, "Microsoft JhengHei", sans-serif;
            box-sizing: border-box;
        }}

        #street-view-panel.collapsed {{
            height: 46px;
        }}

        #street-view-header {{
            height: 46px;
            padding: 0 12px 0 14px;
            background-color: #222222;
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: bold;
            box-sizing: border-box;
        }}

        #street-view-collapse-button {{
            width: 30px;
            height: 30px;
            border: none;
            border-radius: 8px;
            background-color: white;
            color: #222222;
            font-size: 20px;
            font-weight: bold;
            cursor: pointer;
            line-height: 1;
        }}

        #street-view-collapse-button:hover {{
            background-color: #eeeeee;
        }}

        #street-view-body {{
            position: relative;
            height: 234px;
            background-color: #eeeeee;
        }}

        #street-view-box {{
            width: 100%;
            height: 100%;
        }}

        #street-view-status {{
            position: absolute;
            left: 10px;
            right: 10px;
            bottom: 10px;
            padding: 8px 10px;
            background-color: rgba(0, 0, 0, 0.68);
            color: white;
            font-size: 13px;
            border-radius: 8px;
            line-height: 1.4;
            pointer-events: none;
        }}

        #street-view-panel.collapsed #street-view-body {{
            display: none;
        }}

        @media (max-width: 780px) {{
            #street-view-panel {{
                width: 300px;
                height: 250px;
                right: 10px;
                bottom: 10px;
            }}

            #street-view-body {{
                height: 204px;
            }}
        }}
    </style>

    <script>
        window.streetViewPanelCollapsed = false;
        window.virtualPersonStreetView = null;
        window.virtualPersonStreetViewService = null;
        window.lastStreetViewLat = null;
        window.lastStreetViewLng = null;
        window.streetViewUpdateTimer = null;

        function toggleStreetViewPanel() {{
            var panel = document.getElementById("street-view-panel");
            var button = document.getElementById("street-view-collapse-button");

            if (!panel || !button) {{
                return;
            }}

            window.streetViewPanelCollapsed = !window.streetViewPanelCollapsed;

            if (window.streetViewPanelCollapsed) {{
                panel.classList.add("collapsed");
                button.innerText = "＋";
            }} else {{
                panel.classList.remove("collapsed");
                button.innerText = "－";

                setTimeout(function() {{
                    if (window.virtualPersonStreetView) {{
                        google.maps.event.trigger(window.virtualPersonStreetView, "resize");
                    }}
                }}, 120);
            }}
        }}

        function setStreetViewStatus(message) {{
            var statusElement = document.getElementById("street-view-status");

            if (statusElement) {{
                statusElement.innerText = message;
            }}
        }}

        function getVirtualPersonPositionForStreetView() {{
            if (typeof window.getVirtualPersonLatLng !== "function") {{
                return null;
            }}

            var latLng = window.getVirtualPersonLatLng();

            if (!latLng) {{
                return null;
            }}

            return {{
                lat: latLng.lat,
                lng: latLng.lng
            }};
        }}

        function hasStreetViewPositionChanged(position) {{
            if (
                window.lastStreetViewLat === null ||
                window.lastStreetViewLng === null
            ) {{
                return true;
            }}

            var latDifference = Math.abs(position.lat - window.lastStreetViewLat);
            var lngDifference = Math.abs(position.lng - window.lastStreetViewLng);

            return latDifference > 0.00008 || lngDifference > 0.00008;
        }}

        function rememberStreetViewPosition(position) {{
            window.lastStreetViewLat = position.lat;
            window.lastStreetViewLng = position.lng;
        }}

        function updateVirtualPersonStreetView(forceUpdate) {{
            if (
                !window.virtualPersonStreetView ||
                !window.virtualPersonStreetViewService
            ) {{
                return;
            }}

            var position = getVirtualPersonPositionForStreetView();

            if (!position) {{
                setStreetViewStatus("尚未取得人物位置");
                return;
            }}

            if (!forceUpdate && !hasStreetViewPositionChanged(position)) {{
                return;
            }}

            rememberStreetViewPosition(position);

            setStreetViewStatus(
                "正在搜尋附近街景：" +
                position.lat.toFixed(6) +
                ", " +
                position.lng.toFixed(6)
            );

            window.virtualPersonStreetViewService.getPanorama(
                {{
                    location: position,
                    radius: 100,
                    preference: google.maps.StreetViewPreference.NEAREST,
                    source: google.maps.StreetViewSource.OUTDOOR
                }},
                function(data, status) {{
                    if (status === google.maps.StreetViewStatus.OK) {{
                        window.virtualPersonStreetView.setPosition(
                            data.location.latLng
                        );

                        window.virtualPersonStreetView.setPov({{
                            heading: 0,
                            pitch: 0
                        }});

                        setStreetViewStatus(
                            "目前顯示人物附近街景，可用滑鼠拖曳旋轉視角"
                        );
                    }} else {{
                        setStreetViewStatus(
                            "人物附近找不到可用街景，請移動到道路附近再試"
                        );
                    }}
                }}
            );
        }}

        function scheduleStreetViewUpdate() {{
            if (window.streetViewUpdateTimer) {{
                clearTimeout(window.streetViewUpdateTimer);
            }}

            window.streetViewUpdateTimer = setTimeout(function() {{
                updateVirtualPersonStreetView(false);
            }}, 350);
        }}

        window.initVirtualPersonStreetView = function() {{
            var streetViewBox = document.getElementById("street-view-box");

            if (!streetViewBox) {{
                return;
            }}

            var startPosition = getVirtualPersonPositionForStreetView();

            if (!startPosition) {{
                startPosition = {{
                    lat: 25.0462258,
                    lng: 121.5174848
                }};
            }}

            window.virtualPersonStreetViewService =
                new google.maps.StreetViewService();

            window.virtualPersonStreetView =
                new google.maps.StreetViewPanorama(
                    streetViewBox,
                    {{
                        position: startPosition,
                        pov: {{
                            heading: 0,
                            pitch: 0
                        }},
                        zoom: 1,
                        addressControl: false,
                        fullscreenControl: false,
                        motionTracking: false,
                        motionTrackingControl: false,
                        linksControl: true,
                        panControl: true,
                        zoomControl: true,
                        enableCloseButton: false
                    }}
                );

            updateVirtualPersonStreetView(true);

            setInterval(function() {{
                scheduleStreetViewUpdate();
            }}, 600);
        }};
    </script>

    <script
        src="https://maps.googleapis.com/maps/api/js?key={GOOGLE_MAPS_JAVASCRIPT_API_KEY}&callback=initVirtualPersonStreetView"
        async
        defer>
    </script>
    """

    taipei_map.get_root().html.add_child(folium.Element(html))