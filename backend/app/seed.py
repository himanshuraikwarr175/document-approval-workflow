from sqlalchemy.orm import Session

from app.models import User

DEMO_USERS = (
    {"name": "himanshu test submitter", "email": "ava@example.com", "role": "submitter"},
    {"name": "himanshu test reviewer", "email": "sam@example.com", "role": "reviewer"},
)


def seed_users(db: Session) -> None:
    if db.query(User).first() is not None:
        return
    for row in DEMO_USERS:
        db.add(User(**row))
    db.commit()
