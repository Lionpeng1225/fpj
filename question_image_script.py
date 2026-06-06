def get_question_image_script():
    """
    回傳題目圖片切換 JavaScript。

    功能：
    1. 根據目前題目更新圖片
    2. 遊戲中不顯示地點名稱
    3. 提供 window.getCurrentQuestion() 給其他功能使用
    """

    return """
    <script>
        window.getCurrentQuestionNumber = function() {
            return currentQuestionIndex + 1;
        };

        window.getCurrentQuestion = function() {
            return questions[currentQuestionIndex];
        };

        window.getAllQuestions = function() {
            return questions;
        };

        function updateQuestionImage() {
            const question = questions[currentQuestionIndex];
            const imageElement = document.getElementById("question-image");
            const emptyElement = document.getElementById("question-image-empty");

            if (question.image) {
                imageElement.src = question.image;
                imageElement.style.display = "block";
                emptyElement.style.display = "none";
            } else {
                imageElement.removeAttribute("src");
                imageElement.style.display = "none";
                emptyElement.style.display = "block";
            }
        }

        function updateQuestionPanel() {
            document.getElementById("current-question-number").innerText =
                currentQuestionIndex + 1;

            updateQuestionImage();

            window.dispatchEvent(
                new CustomEvent("questionChanged", {
                    detail: {
                        questionNumber: currentQuestionIndex + 1,
                        question: questions[currentQuestionIndex]
                    }
                })
            );
        }

        function nextQuestion() {
            currentQuestionIndex++;

            if (currentQuestionIndex >= questions.length) {
                currentQuestionIndex = 0;
            }

            updateQuestionPanel();
        }

        function previousQuestion() {
            currentQuestionIndex--;

            if (currentQuestionIndex < 0) {
                currentQuestionIndex = questions.length - 1;
            }

            updateQuestionPanel();
        }
    </script>
    """