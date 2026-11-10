import json
import os
import random
from datetime import datetime, date
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

VK_API = "https://api.vk.com/method"
VK_VERSION = "5.199"
MOSCOW = ZoneInfo("Europe/Moscow")
HISTORY_FILE = Path("post_history.json")

STARTERS = [
    "Эй, ты", "Слушай сюда", "Запомни, боец", "Ну-ка соберись",
    "Даже не думай сдаваться", "Подними голову", "Дыши ровно",
    "Хватит себя списывать", "Сегодня твой день", "Ты ещё покажешь",
    "Плевать на вчерашний бардак", "Соберись, красавчик",
    "Не кисни", "Выдохни и улыбнись", "Давай без самосаботажа",
    "Пусть весь мир подождёт", "Ты крепче, чем думаешь",
    "Пошло оно всё лесом", "Встряхнись как следует", "Сделай глубокий вдох",
]
ACTIONS = [
    "сделай хотя бы один шаг вперёд",
    "не отдавай этот день унынию",
    "разрули свои дела в собственном темпе",
    "напомни проблемам, кто здесь главный",
    "вытащи себя из этой эмоциональной жопы",
    "выбери себя, а не чужие ожидания",
    "двигайся дальше, даже если медленно",
    "дай себе шанс на хороший поворот",
    "перестань ждать идеального момента",
    "сделай сегодня что-нибудь для себя",
    "не позволяй одной неудаче испортить весь маршрут",
    "оставь лишний негатив за бортом",
    "начни с малого и не грызи себя",
    "покажи этому дню свой характер",
    "не сравнивай свой путь с чужой витриной",
    "разреши себе ошибаться и пробовать снова",
    "отправь внутреннего критика нахер отдохнуть",
    "сохрани силы для того, что действительно важно",
    "не сдавай свои мечты из-за временной херни",
    "сделай по-своему, но сделай",
]
ENDINGS = [
    "ты не обязан быть идеальным, чтобы быть охуенным.",
    "даже маленькая победа — это всё равно победа.",
    "ты заслуживаешь нормальной жизни, а не вечной гонки.",
    "у тебя ещё дофига возможностей всё изменить.",
    "главное — не бросай себя в трудную минуту.",
    "ты справишься, чёрт возьми, шаг за шагом.",
    "мир и так шумный, не становись собственным врагом.",
    "твоя ценность не измеряется чужим мнением.",
    "иногда смелость — это просто продолжать.",
    "пусть сегодня получится хоть что-то хорошее.",
    "ты уже пережил многое и всё ещё здесь.",
    "не требуй от себя невозможного, но верь в себя.",
    "впереди ещё будут поводы красиво охуеть от счастья.",
    "небольшой прогресс лучше идеального бездействия.",
    "ты имеешь право начать заново хоть сто раз.",
    "не отдавай свою энергию всякой ерунде.",
    "сначала поддержи себя, а потом покоряй мир.",
    "ты не сломан — ты просто человек, которому нужен отдых.",
    "пусть сегодня будет чуть легче, чем вчера.",
    "и да, у тебя всё ещё может охуенно получиться.",
]
HASHTAGS = [
    "#НеКисни", "#ЖивиНаПолную", "#СилаВнутри", "#ДержисьБоец",
    "#СамПоддержиСебя", "#БезСамосаботажа", "#ВсёБудетНормально",
    "#ШагЗаШагом", "#НастройНаПобеду", "#ХарактерЕсть",
    "#ЖизньПродолжается", "#ВремяДляСебя", "#НеСдавайся",
    "#ПофигНаНегатив", "#ВперёдИТолько", "#ПоддержкаСЮмором",
    "#ДеньЗаДнём", "#Смелее", "#ТыСправишься", "#Выдохни",
    "#МотивацияБезСахара", "#БудьСобой", "#Соберись",
    "#ПозитивСМатом", "#СильнееЧемКажется", "#НовыйДень",
]

def load_history():
    if not HISTORY_FILE.exists():
        return {"posts": [], "dates": []}
    with HISTORY_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)
    data.setdefault("posts", [])
    data.setdefault("dates", [])
    return data

def make_post(day: date, used_posts: set[str]) -> str:
    # Перебираем разные комбинации и никогда не выбираем уже использованный текст.
    seed = day.toordinal()
    rng = random.Random(seed)
    candidates = [
        f"{starter}, {action}, потому что {ending}"
        for starter in STARTERS
        for action in ACTIONS
        for ending in ENDINGS
    ]
    rng.shuffle(candidates)
    for candidate in candidates:
        if candidate not in used_posts:
            return candidate
    raise RuntimeError("Закончились уникальные комбинации постов — добавьте новые фразы в словари.")

def make_hashtags(day: date) -> list[str]:
    rng = random.Random(day.toordinal() * 7919)
    return rng.sample(HASHTAGS, 3)

def vk_call(method: str, token: str, **params):
    response = requests.post(
        f"{VK_API}/{method}",
        data={**params, "access_token": token, "v": VK_VERSION},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    if "error" in payload:
        error = payload["error"]
        raise RuntimeError(f"VK API error {error.get('error_code')}: {error.get('error_msg')}")
    return payload["response"]

def main():
    token = os.environ["VK_ACCESS_TOKEN"]
    group_id = int(os.environ.get("VK_GROUP_ID", "117734286"))
    today = datetime.now(MOSCOW).date()
    history = load_history()

    if today.isoformat() in history["dates"]:
        print(f"Пост за {today.isoformat()} уже публиковался. Повтор пропущен.")
        return

    used_posts = set(history["posts"])
    post_text = make_post(today, used_posts)
    hashtags = make_hashtags(today)
    message = post_text + "\n\n" + " ".join(hashtags)

    # Групповой токен может публиковать на стене, но не читать её через wall.get.
    result = vk_call(
        "wall.post",
        token,
        owner_id=-group_id,
        from_group=1,
        message=message,
    )

    history["posts"].append(post_text)
    history["dates"].append(today.isoformat())
    with HISTORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(history, file, ensure_ascii=False, indent=2)

    print(f"Опубликовано: {today.isoformat()}, post_id={result.get('post_id')}")
    print(message)

if __name__ == "__main__":
    main()
