from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = "sqlite:///./document.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def prepare_database() -> None:
    import app.models  # noqa: F401

    inspector = inspect(engine)
    if "submissions" in inspector.get_table_names():
        columns = {column["name"] for column in inspector.get_columns("submissions")}
        if "stored_name" not in columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE submissions RENAME TO submissions_legacy"))
            Base.metadata.create_all(bind=engine)
            with engine.begin() as connection:
                connection.execute(
                    text(
                        """
                        INSERT INTO submissions (
                            id, title, status, reviewer_note, submitter_id,
                            created_at, updated_at, original_filename, stored_name
                        )
                        SELECT
                            id, title, status, reviewer_note, submitter_id,
                            created_at, updated_at, 'previous-text.txt', ''
                        FROM submissions_legacy
                        """
                    )
                )
                connection.execute(text("DROP TABLE submissions_legacy"))
            return
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
