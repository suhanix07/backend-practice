import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

def get_db():
    conn = sqlite3.connect("app.db")
    conn.row_factory = sqlite3.Row
    return conn

conn = get_db()
conn.execute(
    "CREATE TABLE IF NOT EXISTS users ("
    "id INTEGER PRIMARY KEY AUTOINCREMENT, "
    "name TEXT NOT NULL, email TEXT NOT NULL UNIQUE)"
)
conn.commit()
conn.close()

class UserIn(BaseModel):
    name: str
    email: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/users", status_code=201)
def create_user(user: UserIn):
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (user.name, user.email),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="email already exists")
    finally:
        conn.close()
    return {"id": cur.lastrowid, "name": user.name, "email": user.email}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="user not found")
    return dict(row)