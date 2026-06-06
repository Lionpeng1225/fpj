def get_result_panel_style():
    """
    回傳結算畫面的 CSS。
    """

    return """
    <style>
        #result-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 10000;
            background-color: rgba(0, 0, 0, 0.45);
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: Arial, "Microsoft JhengHei", sans-serif;
        }

        #result-panel {
            width: 980px;
            max-width: 94vw;
            max-height: 88vh;
            padding: 22px;
            background-color: white;
            border-radius: 18px;
            box-shadow: 0 8px 28px rgba(0, 0, 0, 0.35);
            box-sizing: border-box;
            overflow-y: auto;
        }

        .result-header {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 18px;
        }

        .result-header h2 {
            margin: 0;
            font-size: 28px;
        }

        #result-loading {
            padding: 12px;
            margin-bottom: 14px;
            background-color: #e7f1ff;
            color: #0d6efd;
            border-radius: 10px;
            font-weight: bold;
            text-align: center;
        }

        #result-summary {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-bottom: 16px;
        }

        .summary-card {
            padding: 14px;
            background-color: #f1f3f5;
            border-radius: 12px;
            text-align: center;
            border: 1px solid #dddddd;
        }

        .summary-card .number {
            font-size: 24px;
            font-weight: bold;
            color: #2b7cff;
            margin-bottom: 4px;
        }

        .summary-card .label {
            font-size: 14px;
            color: #444444;
        }

        #result-map {
            width: 100%;
            height: 430px;
            border-radius: 14px;
            border: 1px solid #cccccc;
            margin-bottom: 16px;
            overflow: hidden;
        }

        #result-list {
            border-top: 1px solid #dddddd;
            margin-top: 8px;
        }

        .result-item {
            display: grid;
            grid-template-columns: 70px 1fr 130px 100px 100px;
            gap: 12px;
            align-items: center;
            padding: 12px 4px;
            border-bottom: 1px solid #eeeeee;
        }

        .result-question-number {
            font-weight: bold;
            color: #333333;
        }

        .result-question-name {
            font-size: 15px;
            line-height: 1.35;
        }

        .result-distance,
        .result-duration,
        .result-score {
            text-align: right;
            font-weight: bold;
        }

        .good-distance {
            color: #198754;
        }

        .normal-distance {
            color: #fd7e14;
        }

        .bad-distance {
            color: #dc3545;
        }

        .missing-distance {
            color: #888888;
        }

        .score-good {
            color: #198754;
        }

        .score-normal {
            color: #fd7e14;
        }

        .score-bad {
            color: #dc3545;
        }

        .score-missing {
            color: #888888;
        }

        .result-actions {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            margin-top: 18px;
        }

        .result-actions button {
            padding: 10px 18px;
            border: none;
            border-radius: 10px;
            color: white;
            font-weight: bold;
            cursor: pointer;
        }

        .home-result-button {
            background-color: #555555;
        }

        .home-result-button:hover {
            background-color: #333333;
        }

        .result-player-icon {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background-color: #2b7cff;
            border: 3px solid #004ecb;
            color: white;
            font-size: 14px;
            font-weight: bold;
            display: flex;
            justify-content: center;
            align-items: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
            font-family: Arial, "Microsoft JhengHei", sans-serif;
        }

        .result-answer-icon {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background-color: #2fb344;
            border: 3px solid #087f23;
            color: white;
            font-size: 14px;
            font-weight: bold;
            display: flex;
            justify-content: center;
            align-items: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
            font-family: Arial, "Microsoft JhengHei", sans-serif;
        }

        @media (max-width: 780px) {
            #result-summary {
                grid-template-columns: 1fr 1fr;
            }

            .result-item {
                grid-template-columns: 1fr;
                gap: 4px;
            }

            .result-distance,
            .result-duration,
            .result-score {
                text-align: left;
            }

            #result-map {
                height: 360px;
            }
        }
    </style>
    """