import random
from urllib.parse import urlencode
import os
from dotenv import load_dotenv

# 請換成你自己的 Google Street View Static API Key
# 注意：
# 1. 這裡需要啟用 Street View Static API
# 2. 建議不要把真正的 API Key 放到公開 GitHub
#GOOGLE_STREET_VIEW_API_KEY = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
load_dotenv()
GOOGLE_STREET_VIEW_API_KEY= os.getenv("GOOGLE_STREET_VIEW_API_KEY")

STREET_VIEW_IMAGE_URL = "https://maps.googleapis.com/maps/api/streetview"


def create_street_view_url(
    lat,
    lng,
    heading=None,
    fov=80,
    pitch=0,
    radius=120
):
    """
    建立 Google Street View Static API 圖片網址。

    重點：
    1. source=outdoor：盡量避免抓到室內街景
    2. radius：在地點附近找街景，不一定要剛好在建築物中心
    3. return_error_code=true：沒有街景時不要回傳灰色錯誤圖
    4. heading 如果傳 None，就不固定方向，讓 Google 自己選比較自然的視角
    """

    params = {
        "size": "640x640",
        "location": f"{lat},{lng}",
        "fov": fov,
        "pitch": pitch,
        "radius": radius,
        "source": "outdoor",
        "return_error_code": "true",
        "key": GOOGLE_STREET_VIEW_API_KEY,
    }

    if heading is not None:
        params["heading"] = heading

    return STREET_VIEW_IMAGE_URL + "?" + urlencode(params)


def create_question_street_view_url(lat, lng):
    """
    題目圖片專用街景網址。

    這裡故意不傳 heading。
    原因：
    - 如果硬指定 heading，有些題目會看向大樓牆面或錯誤方向
    - 不指定 heading 時，Google 會用附近街景點產生較自然的視角
    """

    return create_street_view_url(
        lat=lat,
        lng=lng,
        heading=None,
        fov=80,
        pitch=0,
        radius=120
    )


EASY_LANDMARKS = [
    {"name": "台北101", "lat": 25.033964, "lng": 121.564468, "heading": 20},
    {"name": "中正紀念堂", "lat": 25.034611, "lng": 121.521833, "heading": 180},
    {"name": "台北車站周邊廣場", "lat": 25.047778, "lng": 121.517056, "heading": 0},
    {"name": "西門町行人徒步區", "lat": 25.042141, "lng": 121.508169, "heading": 90},
    {"name": "龍山寺", "lat": 25.037162, "lng": 121.499900, "heading": 0},
    {"name": "國父紀念館", "lat": 25.040029, "lng": 121.560245, "heading": 180},
    {"name": "大安森林公園", "lat": 25.032969, "lng": 121.535833, "heading": 90},
    {"name": "士林夜市", "lat": 25.088028, "lng": 121.524111, "heading": 0},
    {"name": "北門", "lat": 25.047819, "lng": 121.511944, "heading": 90},
    {"name": "松山慈祐宮", "lat": 25.050034, "lng": 121.577722, "heading": 180},

    {"name": "總統府", "lat": 25.040083, "lng": 121.511944, "heading": 180},
    {"name": "臺北市政府", "lat": 25.037525, "lng": 121.563782, "heading": 0},
    {"name": "台北小巨蛋", "lat": 25.051389, "lng": 121.549444, "heading": 90},
    {"name": "美麗華摩天輪", "lat": 25.082778, "lng": 121.557222, "heading": 180},
    {"name": "圓山大飯店", "lat": 25.078056, "lng": 121.526389, "heading": 0},
    {"name": "行天宮", "lat": 25.062778, "lng": 121.533056, "heading": 180},
    {"name": "臺北孔廟", "lat": 25.073333, "lng": 121.515278, "heading": 90},
    {"name": "保安宮", "lat": 25.073056, "lng": 121.515000, "heading": 90},
    {"name": "華山1914文化創意產業園區", "lat": 25.044167, "lng": 121.529722, "heading": 0},
    {"name": "松山文創園區", "lat": 25.043889, "lng": 121.560000, "heading": 90},

    {"name": "公館商圈", "lat": 25.014444, "lng": 121.534167, "heading": 0},
    {"name": "臺北市立動物園入口", "lat": 24.998611, "lng": 121.580833, "heading": 90},
    {"name": "北投溫泉博物館周邊", "lat": 25.136389, "lng": 121.507500, "heading": 0},
    {"name": "關渡宮周邊", "lat": 25.117778, "lng": 121.464722, "heading": 180},
    {"name": "饒河街夜市入口", "lat": 25.050250, "lng": 121.577450, "heading": 90},

    {"name": "寧夏夜市入口", "lat": 25.056950, "lng": 121.515250, "heading": 0},
    {"name": "南門市場", "lat": 25.030900, "lng": 121.518000, "heading": 90},
    {"name": "東門市場", "lat": 25.034500, "lng": 121.528900, "heading": 180},
    {"name": "晴光市場", "lat": 25.064400, "lng": 121.524400, "heading": 0},
    {"name": "臺北轉運站", "lat": 25.049200, "lng": 121.517900, "heading": 270},

    {"name": "松山車站", "lat": 25.049306, "lng": 121.578611, "heading": 90},
    {"name": "南港車站", "lat": 25.052222, "lng": 121.607222, "heading": 90},
    {"name": "萬華車站", "lat": 25.033800, "lng": 121.500800, "heading": 0},
    {"name": "臺北流行音樂中心", "lat": 25.051200, "lng": 121.598800, "heading": 180},
    {"name": "南港展覽館", "lat": 25.056000, "lng": 121.618200, "heading": 180},

    {"name": "台北國際會議中心", "lat": 25.033000, "lng": 121.560000, "heading": 0},
    {"name": "世貿一館", "lat": 25.034000, "lng": 121.562500, "heading": 180},
    {"name": "信義威秀影城", "lat": 25.035500, "lng": 121.566900, "heading": 90},
    {"name": "台北探索館", "lat": 25.037500, "lng": 121.563700, "heading": 0},
    {"name": "臺北市立美術館", "lat": 25.072500, "lng": 121.524300, "heading": 180},

    {"name": "臺北故事館", "lat": 25.073100, "lng": 121.524100, "heading": 180},
    {"name": "當代藝術館", "lat": 25.050400, "lng": 121.518400, "heading": 0},
    {"name": "國立臺灣博物館", "lat": 25.042800, "lng": 121.515000, "heading": 180},
    {"name": "二二八和平公園", "lat": 25.041300, "lng": 121.515400, "heading": 0},
    {"name": "青年公園", "lat": 25.022000, "lng": 121.506800, "heading": 90},

    {"name": "榮星花園", "lat": 25.064500, "lng": 121.540000, "heading": 180},
    {"name": "花博公園", "lat": 25.070278, "lng": 121.520000, "heading": 90},
    {"name": "大湖公園", "lat": 25.083600, "lng": 121.604000, "heading": 90},
    {"name": "碧湖公園", "lat": 25.079800, "lng": 121.584500, "heading": 180},
    {"name": "新生公園", "lat": 25.069000, "lng": 121.530000, "heading": 0},

    {"name": "林森公園", "lat": 25.052500, "lng": 121.525000, "heading": 0},
    {"name": "信義安和路口", "lat": 25.033300, "lng": 121.552500, "heading": 90},
    {"name": "敦化南路仁愛路口", "lat": 25.037300, "lng": 121.548200, "heading": 90},
    {"name": "忠孝敦化路口", "lat": 25.041500, "lng": 121.548300, "heading": 90},
    {"name": "南京復興路口", "lat": 25.052100, "lng": 121.544000, "heading": 90},

    {"name": "迪化街入口", "lat": 25.057300, "lng": 121.509000, "heading": 0},
    {"name": "永康街入口", "lat": 25.033600, "lng": 121.529790, "heading": 180},
    {"name": "師大夜市周邊", "lat": 25.024800, "lng": 121.528700, "heading": 90},
    {"name": "華西街觀光夜市", "lat": 25.038000, "lng": 121.498300, "heading": 0},
    {"name": "剝皮寮歷史街區", "lat": 25.036400, "lng": 121.503200, "heading": 90},

    {"name": "西本願寺廣場", "lat": 25.041300, "lng": 121.506100, "heading": 90},
    {"name": "大稻埕碼頭", "lat": 25.056800, "lng": 121.507000, "heading": 270},
    {"name": "彩虹橋", "lat": 25.050600, "lng": 121.576200, "heading": 90},
    {"name": "麥帥一橋周邊", "lat": 25.056000, "lng": 121.575000, "heading": 90},
    {"name": "洲美快速道路橋下周邊", "lat": 25.103000, "lng": 121.505500, "heading": 0},

    {"name": "臺北市立圖書館總館", "lat": 25.028900, "lng": 121.538000, "heading": 90},
    {"name": "國立臺灣大學校門周邊", "lat": 25.017300, "lng": 121.536600, "heading": 180},
    {"name": "臺灣科技大學周邊", "lat": 25.013700, "lng": 121.540800, "heading": 0},
    {"name": "臺北教育大學周邊", "lat": 25.024700, "lng": 121.544000, "heading": 180},
    {"name": "臺北醫學大學周邊", "lat": 25.026100, "lng": 121.561000, "heading": 180},

    {"name": "天母棒球場", "lat": 25.113900, "lng": 121.531900, "heading": 180},
    {"name": "臺北榮民總醫院周邊", "lat": 25.120000, "lng": 121.520000, "heading": 90},
    {"name": "士林官邸周邊", "lat": 25.094000, "lng": 121.530000, "heading": 180},
    {"name": "故宮博物院入口道路", "lat": 25.102400, "lng": 121.548500, "heading": 180},
    {"name": "大直橋周邊", "lat": 25.078500, "lng": 121.542000, "heading": 90},

    {"name": "臺北市立大學天母校區周邊", "lat": 25.113000, "lng": 121.537000, "heading": 90},
    {"name": "內湖行政中心周邊", "lat": 25.069500, "lng": 121.588000, "heading": 0},
    {"name": "松山機場入口道路", "lat": 25.063000, "lng": 121.552000, "heading": 90},
    {"name": "富錦街周邊", "lat": 25.060000, "lng": 121.563000, "heading": 90},
    {"name": "民生社區圓環周邊", "lat": 25.058000, "lng": 121.564000, "heading": 90},

    {"name": "象山步道登山口周邊", "lat": 25.027500, "lng": 121.570800, "heading": 180},
    {"name": "信義商圈香堤大道", "lat": 25.036200, "lng": 121.566500, "heading": 90},
    {"name": "松菸誠品生活周邊", "lat": 25.044200, "lng": 121.561000, "heading": 180},
    {"name": "台北市議會周邊", "lat": 25.037300, "lng": 121.561900, "heading": 0},
    {"name": "四四南村", "lat": 25.031900, "lng": 121.561700, "heading": 90},

    {"name": "永康公園周邊", "lat": 25.033100, "lng": 121.530900, "heading": 180},
    {"name": "青田街周邊", "lat": 25.028700, "lng": 121.531500, "heading": 90},
    {"name": "師大公園周邊", "lat": 25.024300, "lng": 121.528500, "heading": 0},
    {"name": "寶藏巖國際藝術村入口", "lat": 25.010700, "lng": 121.532600, "heading": 90},
    {"name": "自來水園區入口", "lat": 25.013600, "lng": 121.530800, "heading": 180},

    {"name": "大稻埕永樂市場", "lat": 25.054600, "lng": 121.510300, "heading": 0},
    {"name": "霞海城隍廟周邊", "lat": 25.055600, "lng": 121.510400, "heading": 90},
    {"name": "延三夜市周邊", "lat": 25.064700, "lng": 121.511400, "heading": 0},
    {"name": "重慶北路圓環周邊", "lat": 25.054900, "lng": 121.514000, "heading": 90},
    {"name": "台北橋台北端周邊", "lat": 25.063600, "lng": 121.509000, "heading": 270},

    {"name": "花博新生園區入口", "lat": 25.069700, "lng": 121.530300, "heading": 180},
    {"name": "圓山兒童樂園周邊", "lat": 25.097200, "lng": 121.514800, "heading": 90},
    {"name": "士林官邸正門周邊", "lat": 25.094300, "lng": 121.530400, "heading": 180},
    {"name": "天母運動公園周邊", "lat": 25.116100, "lng": 121.534300, "heading": 90},
    {"name": "北投公園入口", "lat": 25.136500, "lng": 121.507800, "heading": 0},
]


HARD_ROADS = [
    {"name": "仁愛路", "start": (25.037100, 121.512500), "end": (25.037200, 121.562800), "heading": 90},
    {"name": "信義路", "start": (25.033600, 121.510700), "end": (25.033700, 121.573000), "heading": 90},
    {"name": "忠孝東路", "start": (25.041900, 121.515000), "end": (25.041300, 121.579000), "heading": 90},
    {"name": "南京東路", "start": (25.052100, 121.520000), "end": (25.051800, 121.580000), "heading": 90},
    {"name": "民生東路", "start": (25.058600, 121.530000), "end": (25.058400, 121.580000), "heading": 90},
    {"name": "羅斯福路", "start": (25.034000, 121.523000), "end": (25.013000, 121.537000), "heading": 180},
    {"name": "承德路", "start": (25.050000, 121.516000), "end": (25.100000, 121.523000), "heading": 0},
    {"name": "中山北路", "start": (25.046000, 121.523000), "end": (25.125000, 121.527000), "heading": 0},
    {"name": "內湖路", "start": (25.082000, 121.555000), "end": (25.083000, 121.592000), "heading": 90},
    {"name": "木柵路", "start": (24.988000, 121.555000), "end": (24.988500, 121.586000), "heading": 90},
    {"name": "和平東路", "start": (25.026000, 121.520000), "end": (25.024000, 121.560000), "heading": 90},
    {"name": "復興南路", "start": (25.053000, 121.543000), "end": (25.020000, 121.543000), "heading": 180},
    {"name": "敦化南路", "start": (25.060000, 121.548000), "end": (25.025000, 121.548000), "heading": 180},
    {"name": "基隆路", "start": (25.047000, 121.558000), "end": (25.010000, 121.540000), "heading": 180},
    {"name": "新生南路", "start": (25.045000, 121.533000), "end": (25.018000, 121.534000), "heading": 180},
    {"name": "建國南路", "start": (25.045000, 121.537000), "end": (25.020000, 121.537000), "heading": 180},
    {"name": "松江路", "start": (25.050000, 121.533000), "end": (25.075000, 121.533000), "heading": 0},
    {"name": "林森北路", "start": (25.050000, 121.525000), "end": (25.065000, 121.525000), "heading": 0},
    {"name": "重慶北路", "start": (25.050000, 121.513000), "end": (25.075000, 121.513000), "heading": 0},
    {"name": "延平北路", "start": (25.055000, 121.511000), "end": (25.090000, 121.510000), "heading": 0},
]


def interpolate_points(start_lat, start_lng, end_lat, end_lng, count):
    points = []

    for index in range(count):
        ratio = index / (count - 1)
        lat = start_lat + (end_lat - start_lat) * ratio
        lng = start_lng + (end_lng - start_lng) * ratio
        points.append((lat, lng))

    return points


def generate_easy_questions():
    questions = []

    for index, landmark in enumerate(EASY_LANDMARKS, start=1):
        question = {
            "id": index,
            "level": "easy",
            "name": landmark["name"],
            "lat": landmark["lat"],
            "lng": landmark["lng"],
            "heading": landmark["heading"],
            "hint": "明顯地標題",
        }

        question["image"] = create_question_street_view_url(
            question["lat"],
            question["lng"]
        )

        questions.append(question)

    return questions


def generate_hard_questions():
    questions = []
    question_id = 101

    for road in HARD_ROADS:
        start_lat, start_lng = road["start"]
        end_lat, end_lng = road["end"]

        points = interpolate_points(start_lat, start_lng, end_lat, end_lng, 5)

        for point_index, point in enumerate(points, start=1):
            lat, lng = point

            question = {
                "id": question_id,
                "level": "hard",
                "name": f"{road['name']}街景 {point_index}",
                "lat": lat,
                "lng": lng,
                "heading": road["heading"],
                "hint": "一般道路街景題",
            }

            question["image"] = create_question_street_view_url(
                question["lat"],
                question["lng"]
            )

            questions.append(question)
            question_id += 1

    return questions


EASY_QUESTIONS = generate_easy_questions()
HARD_QUESTIONS = generate_hard_questions()


def get_questions(level):
    if level == "easy":
        return EASY_QUESTIONS

    if level == "hard":
        return HARD_QUESTIONS

    return EASY_QUESTIONS + HARD_QUESTIONS


def get_random_questions(level, count=10):
    questions = get_questions(level)

    if count > len(questions):
        count = len(questions)

    return random.sample(questions, count)