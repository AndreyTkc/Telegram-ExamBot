import asyncio
import os
# from replit import db
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from app.handlers import router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from dotenv import load_dotenv
load_dotenv()
from db.database import Base, engine, SessionLocal, UserStats, UserHistory

# Initialize the database
Base.metadata.create_all(bind=engine)

bot_token = os.environ.get('BOT_TOKEN')


async def main():
    bot = Bot(token=bot_token,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


def daily_task():
    db = SessionLocal()
    today = str(datetime.now().date())
    completed = db.query(UserStats).filter_by(id=1).first()
    if not completed:
        new_stats = UserStats()
        db.add(new_stats)
        db.commit()
    db.close()

stats_keys = [
    "correct_answers", "wrong_answers", "points", "third_test_lives_amount",
    "second_attempt_daily_activated",
    "explanation_for_wrong_answers_activated", "point_multiplier"
]


def user_stats():
    db = SessionLocal()
    stats = db.query(UserStats).filter_by(id=1).first()
    if not stats:
        new_stats = UserStats()
        db.add(new_stats)
        db.commit()
    db.close()


history_keys = [
    "date_time", "subject", "difficulty", "test_mode",
    "correct_answers_in_test", "wrong_answers_in_test", "percentages",
    "test_time", "obtained_points"
]


def user_history():
    db = SessionLocal()
    try:
        # Check if a user history entry exists for the user (e.g., id=1)
        history = db.query(UserHistory).filter_by(user_id=1).first()
        if not history:
            # Create a new history entry if it doesn't exist
            new_history = UserHistory(
                date_time="",
                subject="",
                difficulty="",
                test_mode="",
                correct_answers_in_test="",
                wrong_answers_in_test="",
                percentages="",
                test_time="",
                obtained_points=""
            )
            db.add(new_history)
            db.commit()
    finally:
        db.close()


if __name__ == '__main__':
    try:
        daily_task()
        user_stats()
        user_history()
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot is offline')
