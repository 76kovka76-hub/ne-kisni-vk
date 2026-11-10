import os
import random
from datetime import datetime, date
from zoneinfo import ZoneInfo

import requests

VK_API = "https://api.vk.com/method"
VK_VERSION = "5.199"
MOSCOW = ZoneInfo("Europe/Moscow")

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

def make_post(day: date) -> str:
    # Deterministic daily selection; combinations provide thousands of distinct posts.
    seed = day.toordinal()
    rng = random.Random(seed)
    starter = STARTERS[(seed * 7) % len(STARTERS)]
    action = ACTIONS[(seed * 13 + 3) % len(ACTIONS)]
    ending = ENDINGS[(seed * 17 + 5) % len(ENDINGS)]
    # Keep the post to one sentence while varying its construction.
    variants = [
        f"{starter}, {action}, потому что {ending}",
        f"{starter}: {action} — {ending}",
        f"{starter}, {action}; {ending}",
    ]
    return rng.choice(variants)

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
    message = make_post(today)

    # Group tokens can publish to the wall but cannot use wall.get to read it.
    # Publish directly; this avoids VK error 27 from group authorization.

    result = vk_call(
        "wall.post",
        token,
        owner_id=-group_id,
        from_group=1,
        message=message,
    )
    print(f"Опубликовано: {today.isoformat()}, post_id={result.get('post_id')}")
    print(message)

if __name__ == "__main__":
    main()
