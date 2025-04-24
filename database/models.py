from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

# Базовый класс для моделей SQLAlchemy
Base = declarative_base()

class Phrase(Base):
    """
    Модель для хранения фраз и их переводов.
    """
    __tablename__ = "phrases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phrase = Column(String, nullable=False)  # Фраза на английском языке
    translation = Column(String, nullable=False)  # Перевод на русский язык