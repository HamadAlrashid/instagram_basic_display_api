from sqlalchemy import Engine, create_engine
from sqlalchemy_utils import create_database, database_exists
from sqlalchemy.orm import sessionmaker

DATABASE_URI = "postgresql+psycopg2://postgres:password@127.0.0.1:3333/instagram"


def read_prompt_file(filename: str, **kwargs) -> str:
    pass


def init_db() -> Engine:
    main_db_engine = create_engine(DATABASE_URI)
    if not database_exists(main_db_engine.url):
        create_database(main_db_engine.url)

    return main_db_engine


def call_OAI(model, messages):
    pass


SessionLocal = sessionmaker()
