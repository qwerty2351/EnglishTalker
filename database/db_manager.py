from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import func

DATABASE_URL = "sqlite:///database.db"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Phrase(Base):
    __tablename__ = "phrases"
    id = Column(Integer, primary_key=True, autoincrement=True)
    phrase = Column(String, nullable=False)
    translation = Column(String, nullable=False)

def init_db():
    """Создание таблиц в базе данных."""
    Base.metadata.create_all(engine)

def add_phrase_to_db(phrase, translation):
    """Добавление новой фразы в базу данных."""
    session = Session()
    new_phrase = Phrase(phrase=phrase, translation=translation)
    session.add(new_phrase)
    session.commit()
    session.close()

def get_random_phrase():
    """Получение случайной фразы из базы данных."""
    session = Session()
    random_phrase = session.query(Phrase).order_by(func.random()).first()
    session.close()
    if random_phrase:
        return random_phrase.phrase, random_phrase.translation
    return None, None

def get_all_phrases():
    """Получение всех фраз из базы данных."""
    session = Session()
    phrases = session.query(Phrase).all()
    session.close()
    return [(phrase.phrase, phrase.translation) for phrase in phrases]

def clear_database():
    """Очистка базы данных."""
    session = Session()
    session.query(Phrase).delete()
    session.commit()
    session.close()