import os
import sqlite3

from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

print("=== 雲端版：SQLite FastAPI 已啟動 ===")

app = FastAPI(title="User CRUD System (Cloud / SQLite)")

# ========== CORS ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 靜態檔案 ==========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# ========== SQLite 資料庫 ==========
DB_PATH = os.path.join(BASE_DIR, "fastapi.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users_fastapi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


# ========== 首頁 ==========
@app.get("/", response_class=HTMLResponse)
def root():
    with open(os.path.join(BASE_DIR, "static", "index.html"), "r", encoding="utf-8") as f:
        return f.read()


# ========== CRUD ==========
@app.get("/users/")
def get_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email FROM users_fastapi ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r["id"], "name": r["name"], "email": r["email"]} for r in rows]


@app.get("/users/{user_id}")
def get_user(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email FROM users_fastapi WHERE id=?", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return {"id": row["id"], "name": row["name"], "email": row["email"]}
    raise HTTPException(status_code=404, detail="使用者不存在")


@app.post("/users/")
def create_user(name: str = Form(...), email: str = Form(...)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users_fastapi (name, email) VALUES (?, ?)", (name, email))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "新增成功"}


@app.put("/users/{user_id}")
def update_user(user_id: int, name: str = Form(...), email: str = Form(...)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users_fastapi SET name=?, email=? WHERE id=?", (name, email, user_id))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "更新成功"}


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users_fastapi WHERE id=?", (user_id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "刪除成功"}


@app.get("/search/")
def search_users(keyword: str):
    conn = get_connection()
    cur = conn.cursor()
    kw = f"%{keyword}%"
    cur.execute("SELECT id, name, email FROM users_fastapi WHERE name LIKE ? OR email LIKE ?", (kw, kw))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r["id"], "name": r["name"], "email": r["email"]} for r in rows]


# ========== 啟動 ==========
if __name__ == "__main__":
    init_db()
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
