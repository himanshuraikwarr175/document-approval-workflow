from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.submissions import router as submissions_router
from app.database import Base, SessionLocal, engine
from app.seed import seed_users


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Import registers both tables on Base.metadata before create_all.
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_users(db)
    finally:
        db.close()
    yield


app = FastAPI(title="Document Approval Workflow", lifespan=lifespan)
app.include_router(submissions_router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
