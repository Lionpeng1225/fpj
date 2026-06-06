def get_marker_style():
    """
    回傳玩家標記需要的 CSS。
    """

    return """
    <style>
        .game-marker-icon {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background-color: #2f80ff;
            border: 3px solid #0057ff;
            color: white;
            font-size: 16px;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
            font-family: Arial, "Microsoft JhengHei", sans-serif;
        }

        .game-marker-icon.locked {
            background-color: #0044cc;
            border-color: #003bb3;
        }
    </style>
    """