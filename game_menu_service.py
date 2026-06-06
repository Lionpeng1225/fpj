import folium


def add_game_menu(taipei_map):
    """
    右上角遊戲選單。

    功能：
    1. 結算遊戲
    2. 返回主畫面
    """

    html = """
    <div id="game-menu">
        <button class="game-menu-button finish-button" onclick="finishGame()">
            結算遊戲
        </button>

        <button class="game-menu-button home-button" onclick="goHome()">
            返回主畫面
        </button>
    </div>

    <style>
        #game-menu {
            position: fixed;
            top: 16px;
            right: 16px;
            z-index: 9999;
            width: 150px;
            padding: 12px;
            background-color: rgba(255, 255, 255, 0.96);
            border-radius: 14px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
            font-family: Arial, "Microsoft JhengHei", sans-serif;
            box-sizing: border-box;
        }

        .game-menu-button {
            width: 100%;
            padding: 10px 8px;
            margin-bottom: 8px;
            border: none;
            border-radius: 9px;
            color: white;
            font-size: 15px;
            font-weight: bold;
            cursor: pointer;
            box-sizing: border-box;
        }

        .game-menu-button:last-child {
            margin-bottom: 0;
        }

        .finish-button {
            background-color: #2b7cff;
        }

        .finish-button:hover {
            background-color: #125fd1;
        }

        .home-button {
            background-color: #555555;
        }

        .home-button:hover {
            background-color: #333333;
        }
    </style>

    <script>
        function finishGame() {
            if (typeof window.showGameResult === "function") {
                window.showGameResult();
            } else {
                alert("結算功能尚未載入");
            }
        }

        function goHome() {
            var confirmGoHome = confirm("確定要返回主畫面嗎？目前遊戲進度不會保留。");

            if (confirmGoHome) {
                window.location.href = "/";
            }
        }
    </script>
    """

    taipei_map.get_root().html.add_child(folium.Element(html))