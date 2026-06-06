# mrt_menu_style.py


def get_mrt_menu_style():
    """
    回傳「使用捷運」按鈕與捷運清單的 CSS。
    """

    return """
    <style>
        #mrt-menu-button {
            position: fixed;
            left: 92px;
            bottom: 18px;
            z-index: 10000;
            padding: 10px 16px;
            border: none;
            border-radius: 12px;
            background-color: #222222;
            color: white;
            font-size: 15px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 3px 12px rgba(0, 0, 0, 0.30);
            font-family: Arial, "Microsoft JhengHei", sans-serif;
        }

        #mrt-menu-button:hover {
            background-color: #000000;
        }

        #mrt-menu-button.disabled {
            background-color: #9a9a9a;
            color: #eeeeee;
            cursor: not-allowed;
            box-shadow: none;
        }

        #mrt-menu-button.disabled:hover {
            background-color: #9a9a9a;
        }

        #mrt-menu-panel {
            position: fixed;
            left: 14px;
            bottom: 64px;
            width: 290px;
            max-height: 460px;
            z-index: 10000;
            display: none;
            background-color: white;
            border-radius: 14px;
            box-shadow: 0 4px 18px rgba(0, 0, 0, 0.28);
            font-family: Arial, "Microsoft JhengHei", sans-serif;
            overflow: hidden;
        }

        #mrt-menu-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 14px;
            background-color: #222222;
            color: white;
            font-weight: bold;
        }

        #mrt-menu-close {
            border: none;
            background-color: transparent;
            color: white;
            font-size: 20px;
            cursor: pointer;
            line-height: 1;
        }

        #mrt-menu-content {
            padding: 10px;
            max-height: 400px;
            overflow-y: auto;
            box-sizing: border-box;
        }

        .mrt-line-block {
            margin-bottom: 8px;
            border: 1px solid #dddddd;
            border-radius: 10px;
            overflow: hidden;
            background-color: #ffffff;
        }

        .mrt-line-block.unavailable {
            opacity: 0.38;
        }

        .mrt-line-block.unavailable .mrt-line-title {
            cursor: not-allowed;
            background-color: #eeeeee;
        }

        .mrt-line-title {
            width: 100%;
            padding: 10px;
            border: none;
            background-color: #f5f5f5;
            display: flex;
            align-items: center;
            justify-content: space-between;
            cursor: pointer;
            font-size: 15px;
            font-weight: bold;
            font-family: Arial, "Microsoft JhengHei", sans-serif;
        }

        .mrt-line-left {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .mrt-line-color {
            width: 14px;
            height: 14px;
            border-radius: 50%;
            display: inline-block;
            border: 1px solid rgba(0, 0, 0, 0.25);
        }

        .mrt-station-list {
            display: none;
            padding: 8px 10px 10px 10px;
            background-color: white;
        }

        .mrt-station-item {
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 7px 4px;
            font-size: 14px;
            border-bottom: 1px solid #eeeeee;
            color: #222222;
            cursor: pointer;
            border-radius: 6px;
        }

        .mrt-station-item:hover {
            background-color: #eef5ff;
        }

        .mrt-station-item:last-child {
            border-bottom: none;
        }

        .mrt-station-code {
            font-weight: bold;
            color: #111111;
            min-width: 42px;
        }

        .mrt-station-name {
            flex: 1;
        }

        .mrt-transfer-dots {
            display: inline-flex;
            gap: 4px;
            align-items: center;
            margin-left: 4px;
            flex-shrink: 0;
        }

        .mrt-transfer-dot {
            width: 11px;
            height: 11px;
            border-radius: 50%;
            display: inline-block;
            border: 1px solid rgba(0, 0, 0, 0.35);
        }
    </style>
    """