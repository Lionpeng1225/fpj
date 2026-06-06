def get_question_image_style():
    """
    回傳題目圖片區塊 CSS。

    功能：
    1. 控制題目圖片大小
    2. 讓遊戲過程只看到圖片，不顯示地點名稱
    """

    return """
    <style>
        .question-description {
            width: 100%;
            min-height: 170px;
            padding: 8px;
            background-color: #f1f3f5;
            border-radius: 10px;
            border: 1px solid #d0d0d0;
            box-sizing: border-box;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 10px;
        }

        #question-image {
            width: 100%;
            height: 160px;
            object-fit: cover;
            border-radius: 8px;
            display: block;
        }

        #question-image-empty {
            color: #666666;
            font-size: 14px;
            text-align: center;
            display: none;
        }
    </style>
    """