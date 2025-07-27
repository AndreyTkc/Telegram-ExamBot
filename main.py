import asyncio
import os
# from replit import db
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from app.handlers import router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

bot_token = os.environ.get('BOT_TOKEN')


async def main():
    bot = Bot(token=bot_token,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


def daily_task():
    return
    # today = str(datetime.now().date())
    # db["completed"] = 0
    # if "last_date" not in db:
    #     db["last_date"] = today
    #     db["completed"] = 0
    #
    # last_date = db["last_date"]
    #
    # if today > last_date:
    #     db["last_date"] = today
    #     db["completed"] = 0
    #
    # else:
    #     return 0


stats_keys = [
    "correct_answers", "wrong_answers", "points", "third_test_lives_amount",
    "second_attempt_daily_activated",
    "explanation_for_wrong_answers_activated", "point_multiplier"
]


def user_stats():
    return
    # if not all(key in db for key in stats_keys):
    #     db[stats_keys[0]] = 0
    #     db[stats_keys[1]] = 0
    #     db[stats_keys[2]] = 0
    #     db[stats_keys[3]] = 3
    #     db[stats_keys[4]] = False
    #     db[stats_keys[5]] = False
    #     db[stats_keys[6]] = 1


history_keys = [
    "date_time", "subject", "difficulty", "test_mode",
    "correct_answers_in_test", "wrong_answers_in_test", "percentages",
    "test_time", "obtained_points"
]


def user_history():
    return
    # if not all(key in db for key in history_keys):
    #     db[history_keys[0]] = []
    #     db[history_keys[1]] = []
    #     db[history_keys[2]] = []
    #     db[history_keys[3]] = []
    #     db[history_keys[4]] = []
    #     db[history_keys[5]] = []
    #     db[history_keys[6]] = []
    #     db[history_keys[7]] = []
    #     db[history_keys[8]] = []


if __name__ == '__main__':
    try:
        daily_task()
        user_stats()
        user_history()
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot is offline')
