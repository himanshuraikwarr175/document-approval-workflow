import uuid
from pathlib import Path

UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"
MAX_BYTES = 5 * 1024 * 1024
ALLOWED_SUFFIXES = {".pdf", ".txt", ".png", ".jpg", ".jpeg", ".doc", ".docx"}


class InvalidFile(Exception):
    def __init__(self, detail: str) -> None:
        self.detail = detail


def save_upload(filename: str | None, data: bytes) -> tuple[str, str]:
    original = Path(filename or "").name.strip()
    suffix = Path(original).suffix.lower()
    if not original or suffix not in ALLOWED_SUFFIXES:
        raise InvalidFile("Upload a pdf, txt, png, jpg, jpeg, doc, or docx file")
    if not data:
        raise InvalidFile("The file is empty")
    if len(data) > MAX_BYTES:
        raise InvalidFile("File must be 5 MB or smaller")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}{suffix}"
    (UPLOAD_DIR / stored_name).write_bytes(data)
    return original, stored_name


def delete_stored_file(stored_name: str) -> None:
    path = UPLOAD_DIR / stored_name
    if path.is_file():
        path.unlink()


def file_path(stored_name: str) -> Path:
    if not stored_name or Path(stored_name).name != stored_name:
        raise InvalidFile("File not found")
    path = (UPLOAD_DIR / stored_name).resolve()
    if UPLOAD_DIR.resolve() not in path.parents or not path.is_file():
        raise InvalidFile("File not found")
    return path
