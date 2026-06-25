from app.db import get_connection, reset_db
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def seed() -> None:
    reset_db()
    conn = get_connection()
    cur = conn.cursor()

    users = [
        ("admin@example.com", "admin123", 1),
        ("alice@example.com", "alice123", 0),
        ("bob@example.com", "bob123", 0),
    ]

    cur.executemany(
        "INSERT INTO users (email, password, is_admin) VALUES (?, ?, ?)",
        users,
    )

    notes = [
        (2, "Alice private note", "Alice secret project notes", 1),
        (2, "Alice public note", "Alice public update", 0),
        (3, "Bob private note", "Bob salary discussion", 1),
    ]

    cur.executemany(
        "INSERT INTO notes (owner_id, title, body, is_private) VALUES (?, ?, ?, ?)",
        notes,
    )

    cur.executemany(
        "INSERT INTO audit_logs (actor_email, action, details) VALUES (?, ?, ?)",
        [
            ("system", "seed", "database seeded"),
            ("admin@example.com", "login", "admin logged in"),
        ],
    )

    conn.commit()
    conn.close()
    print("Seeded database with demo users.")


if __name__ == "__main__":
    seed()
