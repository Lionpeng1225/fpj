import json
import folium


def get_level_name(level):
    if level == "easy":
        return "簡單模式"

    if level == "hard":
        return "困難模式"

    return "未知模式"


def get_question_image(question):
    """
    取得題目圖片。
    如果 question 裡沒有 image，就回傳空字串。
    """

    if "image" in question:
        return question["image"]

    return ""


def add_question_panel(taipei_map, questions, level):
    first_question = questions[0]
    questions_json = json.dumps(questions, ensure_ascii=False)

    first_image = get_question_image(first_question)

    html = f"""
    <div id="question-panel">
        <div class="panel-header">
            <div class="panel-title-area">
                <h2>台北市定向越野</h2>
                <span class="mode">{get_level_name(level)}</span>
            </div>

            <button id="collapse-question-panel-button" onclick="toggleQuestionPanelCollapse()">
                －
            </button>
        </div>

        <div id="question-panel-body">
            <div class="question-row">
                <div class="question-progress">
                    第 <span id="current-question-number">1</span> / {len(questions)} 題
                </div>

                <button class="hint-button" onclick="showQuestionHint()">
                    提示
                </button>

                <div class="small-buttons">
                    <button onclick="previousQuestion()">←</button>
                    <button onclick="nextQuestion()">→</button>
                </div>
            </div>

            <div class="question-image-box">
                <img id="question-image" src="{first_image}" alt="題目圖片">
            </div>

            <div id="hint-box" style="display: none;">
                <span class="hint-label">提示：</span>
                <span id="hint-text"></span>
            </div>
        </div>
    </div>

    <style>
        #question-panel {{
            position: fixed;
            top: 8px;
            left: 8px;
            width: 350px;
            padding: 14px;
            background-color: white;
            border-radius: 16px;
            box-shadow: 0 4px 18px rgba(0, 0, 0, 0.28);
            z-index: 9999;
            font-family: Arial, "Microsoft JhengHei", sans-serif;
            box-sizing: border-box;
        }}

        #question-panel.collapsed {{
            width: 330px;
            padding: 12px 14px;
        }}

        .panel-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
        }}

        .panel-title-area {{
            display: flex;
            align-items: center;
            gap: 10px;
            min-width: 0;
        }}

        #question-panel h2 {{
            margin: 0;
            font-size: 24px;
            font-weight: bold;
            line-height: 1.2;
            white-space: nowrap;
        }}

        .mode {{
            padding: 7px 10px;
            color: white;
            background-color: #5b78ff;
            border-radius: 10px;
            font-size: 15px;
            white-space: nowrap;
        }}

        #collapse-question-panel-button {{
            width: 34px;
            height: 34px;
            border: none;
            border-radius: 9px;
            background-color: #333333;
            color: white;
            font-size: 22px;
            font-weight: bold;
            cursor: pointer;
            line-height: 1;
            flex-shrink: 0;
        }}

        #collapse-question-panel-button:hover {{
            background-color: #111111;
        }}

        #question-panel-body {{
            margin-top: 14px;
        }}

        .question-row {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 12px;
        }}

        .question-progress {{
            font-size: 18px;
            line-height: 1.4;
            color: #333333;
            white-space: nowrap;
            margin-right: auto;
        }}

        .hint-button {{
            height: 40px;
            padding: 0 14px;
            border: none;
            border-radius: 10px;
            background-color: #28a745;
            color: white;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            font-family: Arial, "Microsoft JhengHei", sans-serif;
            white-space: nowrap;
        }}

        .hint-button:hover {{
            background-color: #1f8a38;
        }}

        .small-buttons {{
            display: flex;
            gap: 8px;
        }}

        .small-buttons button {{
            width: 48px;
            height: 40px;
            border: none;
            border-radius: 10px;
            background-color: #5b78ff;
            color: white;
            font-size: 22px;
            cursor: pointer;
            line-height: 1;
        }}

        .small-buttons button:hover {{
            background-color: #3f5fe0;
        }}

        .question-image-box {{
            width: 100%;
            padding: 10px;
            background-color: #f1f3f5;
            border-radius: 14px;
            border: 1px solid #d0d0d0;
            box-sizing: border-box;
        }}

        #question-image {{
            width: 100%;
            height: 220px;
            object-fit: cover;
            display: block;
            border-radius: 10px;
            background-color: #dddddd;
        }}

        #hint-box {{
            margin-top: 12px;
            padding: 11px 14px;
            background-color: #fff8dc;
            border: 1px solid #e0c96f;
            border-radius: 12px;
            color: #333333;
            font-size: 18px;
            line-height: 1.5;
            box-sizing: border-box;
        }}

        .hint-label {{
            font-weight: bold;
            color: #8a6d00;
        }}

        #hint-text {{
            font-weight: bold;
        }}
    </style>

    <script>
        const questions = {questions_json};
        let currentQuestionIndex = 0;
        let isQuestionPanelCollapsed = false;

        /*
            記錄每一題是否已經按過提示。
            shownHintQuestions[0] = true 代表第 1 題提示已顯示過。
        */
        let shownHintQuestions = {{}};

        window.getCurrentQuestionNumber = function() {{
            return currentQuestionIndex + 1;
        }};

        window.getCurrentQuestion = function() {{
            return questions[currentQuestionIndex];
        }};

        window.getAllQuestions = function() {{
            return questions;
        }};

        function getQuestionImage(question) {{
            if (question.image) {{
                return question.image;
            }}

            return "";
        }}

        function hideQuestionHint() {{
            const hintBox = document.getElementById("hint-box");
            const hintText = document.getElementById("hint-text");

            if (hintBox) {{
                hintBox.style.display = "none";
            }}

            if (hintText) {{
                hintText.innerText = "";
            }}
        }}

        function setQuestionHintText(question) {{
            const hintBox = document.getElementById("hint-box");
            const hintText = document.getElementById("hint-text");

            if (!hintBox || !hintText) {{
                return;
            }}

            if (!question || !question.name) {{
                hintText.innerText = "這題沒有提示資料";
            }} else {{
                hintText.innerText = question.name;
            }}

            hintBox.style.display = "block";
        }}

        function restoreHintState() {{
            const question = questions[currentQuestionIndex];

            if (shownHintQuestions[currentQuestionIndex]) {{
                setQuestionHintText(question);
            }} else {{
                hideQuestionHint();
            }}
        }}

        function showQuestionHint() {{
            const question = questions[currentQuestionIndex];

            shownHintQuestions[currentQuestionIndex] = true;

            setQuestionHintText(question);
        }}

        function toggleQuestionPanelCollapse() {{
            const panel = document.getElementById("question-panel");
            const body = document.getElementById("question-panel-body");
            const button = document.getElementById("collapse-question-panel-button");

            if (!panel || !body || !button) {{
                return;
            }}

            isQuestionPanelCollapsed = !isQuestionPanelCollapsed;

            if (isQuestionPanelCollapsed) {{
                body.style.display = "none";
                panel.classList.add("collapsed");
                button.innerText = "＋";
            }} else {{
                body.style.display = "block";
                panel.classList.remove("collapsed");
                button.innerText = "－";
                restoreHintState();
            }}
        }}

        function updateQuestionPanel() {{
            const question = questions[currentQuestionIndex];

            document.getElementById("current-question-number").innerText =
                currentQuestionIndex + 1;

            const imageElement = document.getElementById("question-image");
            imageElement.src = getQuestionImage(question);

            restoreHintState();

            window.dispatchEvent(
                new CustomEvent("questionChanged", {{
                    detail: {{
                        questionNumber: currentQuestionIndex + 1,
                        question: question
                    }}
                }})
            );
        }}

        function nextQuestion() {{
            currentQuestionIndex++;

            if (currentQuestionIndex >= questions.length) {{
                currentQuestionIndex = 0;
            }}

            updateQuestionPanel();
        }}

        function previousQuestion() {{
            currentQuestionIndex--;

            if (currentQuestionIndex < 0) {{
                currentQuestionIndex = questions.length - 1;
            }}

            updateQuestionPanel();
        }}
    </script>
    """

    taipei_map.get_root().html.add_child(folium.Element(html))