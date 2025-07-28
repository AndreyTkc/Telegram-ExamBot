from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database connection
DATABASE_URL = "sqlite:///./main.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Example user stats model
class UserStats(Base):
    __tablename__ = "user_stats"
    id = Column(Integer, primary_key=True, index=True)
    correct_answers = Column(Integer, default=0)
    wrong_answers = Column(Integer, default=0)
    points = Column(Integer, default=0)
    third_test_lives_amount = Column(Integer, default=3)
    second_attempt_daily_activated = Column(Boolean, default=False)
    explanation_for_wrong_answers_activated = Column(Boolean, default=False)
    point_multiplier = Column(Integer, default=1)

class UserHistory(Base):
    __tablename__ = "user_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, default=1)  # Example user ID
    date_time = Column(String, default="[]")  # Store as JSON string
    subject = Column(String, default="[]")
    difficulty = Column(String, default="[]")
    test_mode = Column(String, default="[]")
    correct_answers_in_test = Column(String, default="[]")
    wrong_answers_in_test = Column(String, default="[]")
    percentages = Column(String, default="[]")
    test_time = Column(String, default="[]")
    obtained_points = Column(String, default="[]")