from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext

from app.auth import create_token, get_current_user
from app.db import get_connection, init_db

app = FastAPI(title="Secure Notes API")

FILES_DIR = Path("data/files")

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class NoteRequest(BaseModel):
    title: str
    body: str
    is_private: bool = True


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/auth/register")
def register(body: RegisterRequest) -> dict:
    conn = get_connection()
    cur = conn.cursor()

    try:
        hashed_password = pwd_context.hash(body.password)

        cur.execute(
            "INSERT INTO users (email, password, is_admin) VALUES (?, ?, 0)",
            (body.email, hashed_password),
        )

        conn.commit()

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Registration failed: {exc}"
        )

    finally:
        conn.close()

    return {
        "message": "registered",
        "email": body.email
    }


@app.post("/auth/login")
def login(body: LoginRequest) -> dict:
    conn = get_connection()
    cur = conn.cursor()

    user = cur.execute(
        "SELECT * FROM users WHERE email = ?",
        (body.email,)
    ).fetchone()

    conn.close()

    if (
        not user
        or not pwd_context.verify(
            body.password,
            user["password"]
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_token(dict(user))

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@app.get("/auth/me")
def me(current_user: dict = Depends(get_current_user)) -> dict:
    return current_user


@app.get("/users/{user_id}")
def get_user(
    user_id: int,
    current_user: dict = Depends(get_current_user)
) -> dict:

    if (
        int(current_user["sub"]) != user_id
        and not current_user["is_admin"]
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    conn = get_connection()
    cur = conn.cursor()

    user = cur.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    conn.close()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "id": user["id"],
        "email": user["email"],
        "is_admin": bool(user["is_admin"])
    }


@app.post("/notes")
def create_note(
    body: NoteRequest,
    current_user: dict = Depends(get_current_user)
) -> dict:

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO notes (owner_id, title, body, is_private) VALUES (?, ?, ?, ?)",
        (
            int(current_user["sub"]),
            body.title,
            body.body,
            int(body.is_private)
        ),
    )

    note_id = cur.lastrowid

    cur.execute(
        "INSERT INTO audit_logs (actor_email, action, details) VALUES (?, ?, ?)",
        (
            current_user["email"],
            "create_note",
            f"created note {note_id}"
        ),
    )

    conn.commit()
    conn.close()

    return {
        "id": note_id,
        "title": body.title,
        "body": body.body,
        "is_private": body.is_private
    }


@app.get("/notes")
def list_notes(
    owner_id: int | None = Query(default=None),
    current_user: dict = Depends(get_current_user),
) -> dict:

    conn = get_connection()
    cur = conn.cursor()

    if owner_id is None:
        owner_id = int(current_user["sub"])

    if (
        owner_id != int(current_user["sub"])
        and not current_user["is_admin"]
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    notes = cur.execute(
        "SELECT * FROM notes WHERE owner_id = ?",
        (owner_id,)
    ).fetchall()

    conn.close()

    return {
        "notes": [dict(note) for note in notes]
    }


@app.get("/notes/{note_id}")
def get_note(
    note_id: int,
    current_user: dict = Depends(get_current_user)
) -> dict:

    conn = get_connection()
    cur = conn.cursor()

    note = cur.execute(
        "SELECT * FROM notes WHERE id = ?",
        (note_id,)
    ).fetchone()

    conn.close()

    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    if (
        note["owner_id"] != int(current_user["sub"])
        and not current_user["is_admin"]
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    return dict(note)


@app.get("/files/{file_name:path}")
def read_file(
    file_name: str,
    current_user: dict = Depends(get_current_user)
) -> dict:

    path = (FILES_DIR / file_name).resolve()
    base = FILES_DIR.resolve()

    if not str(path).startswith(str(base)):
        raise HTTPException(
            status_code=403,
            detail="Invalid path"
        )

    try:
        content = path.read_text()

    except Exception as exc:
        raise HTTPException(
            status_code=404,
            detail=f"Could not read file: {exc}"
        )

    return {
        "file": file_name,
        "content": content
    }


@app.get("/admin/audit-logs")
def audit_logs(
    current_user: dict = Depends(get_current_user)
) -> dict:

    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=403,
            detail="Admin only"
        )

    conn = get_connection()
    cur = conn.cursor()

    logs = cur.execute(
        "SELECT * FROM audit_logs ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return {
        "audit_logs": [dict(log) for log in logs]
    }